"""
AGENT 3: CARBON INTENSITY AGENT
Fetches carbon intensity per (zone, day) from Electricity Maps API.

HOW IT WORKS:
- CSV has 350 compressed daily records across 3 zones (IN-WE, SE, US-MIDA-PJM) and ~16 days
- We call the API once per unique (zone, day) combo → max ~48 calls, cached on repeat
- For past dates: /carbon-intensity/past?zone=X&datetime=YYYY-MM-DDT12:00:00Z
- For today/future: /carbon-intensity/latest?zone=X
- If API fails for any reason: use hardcoded fallback values (no data loss)
- API KEY: read from ELECTRICITY_MAPS_API_KEY env var — never hardcoded
"""
import logging
import os
from datetime import datetime
from typing import Dict
import httpx

logger = logging.getLogger(__name__)

# Fallback values (gCO2/kWh) used when API is unavailable
# Source: published national grid averages
FALLBACK_CARBON_INTENSITY = {
    "US-MIDA-PJM": 420, "US-MIDW-MISO": 500, "US-CAL-CISO": 285,
    "US-NW-PACW": 200, "IE": 295, "GB": 230, "FR": 60, "DE": 350,
    "SE": 40, "IT-NO": 300, "IN-WE": 708, "IN": 708,
    "JP-TK": 463, "KR": 450, "JP-KN": 463, "SG": 493,
    "AU-NSW": 700, "HK": 650, "BR-CS": 100, "CA-ON": 120,
    "AE": 500, "ZA": 850, "UNKNOWN": 450,
}


class CarbonIntensityAgent:

    def __init__(self):
        self.api_key = os.getenv('ELECTRICITY_MAPS_API_KEY')
        self.base_url = 'https://api.electricitymap.org/v3'
        self.cache = {}          # (zone, day_str) -> intensity value
        self.api_calls = 0
        self.cached_calls = 0
        self.failed_calls = 0
        self.api_call_log = []   # Every API attempt, logged with full details
        self.use_api = bool(
            self.api_key and
            self.api_key.strip() not in ('', 'your_electricity_maps_api_key_here') and
            len(self.api_key.strip()) > 10
        )

    async def get_batch_intensities(self, requests: list[Dict]) -> list[Dict]:
        """
        For each request {zone, timestamp}, return carbon intensity for that day.

        Deduplication: (zone, day) — so 10 DynamoDB records all on 2026-06-05 in IN-WE
        → 1 API call for (IN-WE, 2026-06-05), result reused for all 10.

        API selection:
        - Past date   → /carbon-intensity/past?zone=X&datetime=YYYY-MM-DDT12:00:00Z
        - Today/future → /carbon-intensity/latest?zone=X
        """
        if not requests:
            return []

        today = datetime.utcnow().date()

        # Build (zone, day) key for each request
        request_keys = []
        unique_pairs = {}  # (zone, day_str) -> None initially

        for req in requests:
            zone = req['zone']
            ts = req.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                day_str = dt.strftime('%Y-%m-%d')
            except Exception:
                day_str = today.strftime('%Y-%m-%d')
            key = (zone, day_str)
            request_keys.append(key)
            unique_pairs[key] = unique_pairs.get(key)  # preserve existing if already set

        logger.info(f"Carbon intensity: {len(requests)} records → {len(unique_pairs)} unique (zone, day) combos")

        # Fetch each unique (zone, day)
        for (zone, day_str) in list(unique_pairs.keys()):
            if unique_pairs[(zone, day_str)] is not None:
                continue  # already resolved

            cache_key = f"{zone}|{day_str}"
            if cache_key in self.cache:
                self.cached_calls += 1
                unique_pairs[(zone, day_str)] = self.cache[cache_key]
                logger.info(f"  Cache [{day_str}] {zone} = {self.cache[cache_key]}")
                continue

            if not self.use_api:
                fallback = FALLBACK_CARBON_INTENSITY.get(zone, 450)
                unique_pairs[(zone, day_str)] = fallback
                self.cache[cache_key] = fallback
                self.api_call_log.append({
                    'zone': zone, 'date': day_str,
                    'called_at': datetime.utcnow().isoformat(),
                    'endpoint': None, 'response_ms': None,
                    'carbon_intensity': fallback,
                    'source': 'fallback_no_key', 'status': 'no_api_key'
                })
                continue

            # Make the API call
            import time as _t
            t0 = _t.time()
            record_date = datetime.strptime(day_str, '%Y-%m-%d').date()
            use_past = record_date < today

            try:
                intensity = await self._fetch(zone, day_str, use_past)
                elapsed_ms = int((_t.time() - t0) * 1000)
                unique_pairs[(zone, day_str)] = intensity
                self.cache[cache_key] = intensity
                self.api_calls += 1
                endpoint = (
                    f"{self.base_url}/carbon-intensity/past?zone={zone}&datetime={day_str}T12:00:00Z"
                    if use_past else
                    f"{self.base_url}/carbon-intensity/latest?zone={zone}"
                )
                self.api_call_log.append({
                    'zone': zone, 'date': day_str,
                    'called_at': datetime.utcnow().isoformat(),
                    'endpoint': endpoint, 'response_ms': elapsed_ms,
                    'carbon_intensity': intensity,
                    'source': 'api', 'status': 'success'
                })
                logger.info(f"  API [{day_str}] {zone} = {intensity} gCO2/kWh ({elapsed_ms}ms)")

            except Exception as e:
                self.failed_calls += 1
                fallback = FALLBACK_CARBON_INTENSITY.get(zone, 450)
                unique_pairs[(zone, day_str)] = fallback
                self.cache[cache_key] = fallback
                self.api_call_log.append({
                    'zone': zone, 'date': day_str,
                    'called_at': datetime.utcnow().isoformat(),
                    'endpoint': f"{self.base_url}/carbon-intensity/past?zone={zone}&datetime={day_str}T12:00:00Z",
                    'response_ms': None,
                    'carbon_intensity': fallback,
                    'source': 'fallback', 'status': 'failed', 'error': str(e)
                })
                logger.warning(f"  Fallback [{day_str}] {zone} = {fallback} ({e})")

        logger.info(f"Done: {self.api_calls} API calls, {self.cached_calls} cached, {self.failed_calls} fallback")

        # Return results in same order as input
        return [
            {
                'timestamp': req['timestamp'],
                'zone': req['zone'],
                'carbon_intensity': unique_pairs.get(key, 450),
                'source': 'resolved'
            }
            for req, key in zip(requests, request_keys)
        ]

    async def _fetch(self, zone: str, day_str: str, use_past: bool) -> float:
        """Single API call — past or latest endpoint."""
        headers = {'auth-token': self.api_key.strip()}

        if use_past:
            url = f"{self.base_url}/carbon-intensity/past"
            params = {'zone': zone, 'datetime': f"{day_str}T12:00:00Z"}
        else:
            url = f"{self.base_url}/carbon-intensity/latest"
            params = {'zone': zone}

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            intensity = data.get('carbonIntensity', 0)
            if not intensity or intensity <= 0:
                raise ValueError(f"Bad intensity: {intensity}")
            return float(intensity)

    def get_cache_stats(self) -> Dict:
        return {
            'api_calls': self.api_calls,
            'cached_calls': self.cached_calls,
            'failed_calls': self.failed_calls,
            'cache_size': len(self.cache),
            'has_api_key': self.use_api,
            'total_requests': self.api_calls + self.cached_calls + self.failed_calls,
            'api_call_log': self.api_call_log
        }
