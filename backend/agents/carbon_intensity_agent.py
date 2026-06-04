"""
AGENT 3: HISTORICAL CARBON INTENSITY AGENT (OPTIMIZED)
Purpose: Retrieve historical carbon intensity from Electricity Maps API

OPTIMIZATIONS:
- Unique key deduplication: (region + hour) to minimize API calls
- Smart caching: Reuse results for identical zone+time
- Batch async processing: Concurrent API requests
- No-API-key fast path: Instant fallback without network delays
- Error handling: Return errors instead of fake data
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class CarbonIntensityAgent:
    """Fetches historical carbon intensity data with aggressive caching and batching"""
    
    def __init__(self):
        self.api_key = os.getenv('ELECTRICITY_MAPS_API_KEY')
        self.base_url = 'https://api.electricitymap.org/v3'
        self.cache = {}  # Cache: {(zone, timestamp_hour): carbon_intensity}
        self.api_calls = 0
        self.cached_calls = 0
        self.failed_calls = 0
        self.use_api = (
            self.api_key and 
            self.api_key != 'your_electricity_maps_api_key_here' and
            len(self.api_key) > 10
        )
    
    async def get_historical_intensity(
        self, 
        zone: str, 
        timestamp: str
    ) -> Dict:
        """
        Get historical carbon intensity for a specific zone and time
        
        OPTIMIZATION: Cache-first lookup to avoid redundant API calls
        
        Args:
            zone: Electricity Maps zone code
            timestamp: ISO format timestamp (should already be hourly normalized)
        
        Returns: {
            timestamp, zone, carbon_intensity (gCO2/kWh),
            source: 'electricity_maps', 'cached', or 'error'
        }
        """
        # Parse timestamp to hour precision for caching
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            cache_key = (zone, dt.strftime('%Y-%m-%d %H:00:00'))
        except Exception as e:
            logger.error(f"Invalid timestamp {timestamp}: {e}")
            return self._error_intensity(zone, timestamp, f"Invalid timestamp: {e}")
        
        # FAST PATH: Check cache first
        if cache_key in self.cache:
            self.cached_calls += 1
            return {
                'timestamp': timestamp,
                'zone': zone,
                'carbon_intensity': self.cache[cache_key],
                'source': 'cached'
            }
        
        # FAST PATH: If no valid API key, return error immediately
        if not self.use_api:
            return self._error_intensity(zone, timestamp, "No valid API key configured")
        
        # Try API call with timeout
        try:
            intensity = await self._fetch_from_api(zone, dt)
            
            # Cache the result
            self.cache[cache_key] = intensity
            self.api_calls += 1
            
            return {
                'timestamp': timestamp,
                'zone': zone,
                'carbon_intensity': intensity,
                'source': 'electricity_maps'
            }
            
        except Exception as e:
            self.failed_calls += 1
            logger.warning(f"API call failed for {zone} at {timestamp}: {e}")
            return self._error_intensity(zone, timestamp, str(e))
    
    async def _fetch_from_api(self, zone: str, dt: datetime) -> float:
        """Fetch carbon intensity from Electricity Maps API with very short timeout"""
        url = f"{self.base_url}/carbon-intensity/past"
        
        params = {
            'zone': zone,
            'datetime': dt.strftime('%Y-%m-%dT%H:00:00Z')
        }
        
        headers = {
            'auth-token': self.api_key
        }
        
        # Use VERY short timeout (1 second) - if API is slow, fail fast
        async with httpx.AsyncClient(timeout=1.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            carbon_intensity = data.get('carbonIntensity', 0)
            
            if carbon_intensity <= 0:
                raise ValueError(f"Invalid carbon intensity: {carbon_intensity}")
            
            return carbon_intensity
    
    def _error_intensity(self, zone: str, timestamp: str, error_msg: str) -> Dict:
        """Return error response instead of fake data"""
        return {
            'timestamp': timestamp,
            'zone': zone,
            'carbon_intensity': 0,
            'source': 'error',
            'error': error_msg
        }
    
    async def get_batch_intensities(
        self, 
        requests: list[Dict]
    ) -> list[Dict]:
        """
        Get carbon intensities with AGGRESSIVE deduplication
        
        OPTIMIZATION STRATEGY:
        1. Build unique (zone, hour) keys from all requests
        2. Check cache for each unique key
        3. Only make API calls for cache misses
        4. Process API calls in concurrent batches
        5. Map results back to original request order
        
        Args:
            requests: List of {zone, timestamp} dicts
        
        Returns: List of carbon intensity results (same order as input)
        """
        if not requests:
            return []
        
        logger.info("="*60)
        logger.info(f"STAGE 3: Carbon Intensity Lookup ({len(requests)} requests)")
        logger.info("="*60)
        
        # STAGE 3A: Build unique request keys
        unique_requests = {}
        request_mapping = []  # Maps original index → cache_key
        
        for i, req in enumerate(requests):
            try:
                dt = datetime.fromisoformat(req['timestamp'].replace('Z', '+00:00'))
                cache_key = (req['zone'], dt.strftime('%Y-%m-%d %H:00:00'))
                
                # Track mapping from original request to unique key
                request_mapping.append(cache_key)
                
                # Store unique request
                if cache_key not in unique_requests:
                    unique_requests[cache_key] = {
                        'zone': req['zone'],
                        'timestamp': req['timestamp']
                    }
            except Exception as e:
                logger.warning(f"Invalid timestamp in request {i}: {e}")
                request_mapping.append(None)
        
        logger.info(f"✓ Deduplication: {len(requests)} requests → {len(unique_requests)} unique (zone, hour) combinations")
        logger.info(f"  Reduction: {(1 - len(unique_requests)/len(requests))*100:.1f}%")
        
        # STAGE 3B: Check cache and identify API calls needed
        unique_results = {}
        api_needed = []
        
        for cache_key, req_data in unique_requests.items():
            # Check cache
            if cache_key in self.cache:
                self.cached_calls += 1
                unique_results[cache_key] = {
                    'timestamp': req_data['timestamp'],
                    'zone': req_data['zone'],
                    'carbon_intensity': self.cache[cache_key],
                    'source': 'cached'
                }
            else:
                api_needed.append((cache_key, req_data))
        
        logger.info(f"✓ Cache check: {self.cached_calls} cached, {len(api_needed)} API calls needed")
        
        # STAGE 3C: Process API calls (or return errors if no API key)
        if api_needed:
            if not self.use_api:
                logger.warning("⚠ No valid API key - returning errors for all API requests")
                for cache_key, req_data in api_needed:
                    unique_results[cache_key] = self._error_intensity(
                        req_data['zone'],
                        req_data['timestamp'],
                        "No valid Electricity Maps API key configured"
                    )
                    self.failed_calls += 1
            else:
                # Process API calls in batches (VERY AGGRESSIVE for speed)
                MAX_CONCURRENT = 3  # Reduced from 5 for better reliability
                BATCH_TIMEOUT = 5.0  # 5 second timeout per batch
                
                for i in range(0, len(api_needed), MAX_CONCURRENT):
                    batch = api_needed[i:i+MAX_CONCURRENT]
                    
                    # Create tasks
                    tasks = []
                    for cache_key, req_data in batch:
                        task = self.get_historical_intensity(
                            req_data['zone'],
                            req_data['timestamp']
                        )
                        tasks.append((cache_key, task))
                    
                    # Execute concurrently with SHORT timeout
                    try:
                        batch_results = await asyncio.wait_for(
                            asyncio.gather(*[task for _, task in tasks], return_exceptions=True),
                            timeout=BATCH_TIMEOUT  # 5 second timeout per batch
                        )
                    except asyncio.TimeoutError:
                        logger.error(f"API batch {i//MAX_CONCURRENT + 1} timed out after {BATCH_TIMEOUT}s")
                        # Return errors for this batch
                        batch_results = [Exception("API timeout") for _ in batch]
                    
                    # Store results
                    for (cache_key, _), result in zip(tasks, batch_results):
                        if isinstance(result, Exception):
                            logger.error(f"API error for {cache_key}: {result}")
                            result = self._error_intensity(
                                cache_key[0],
                                cache_key[1],
                                str(result)
                            )
                        unique_results[cache_key] = result
                    
                    logger.info(f"  API batch {i//MAX_CONCURRENT + 1}/{(len(api_needed) + MAX_CONCURRENT - 1)//MAX_CONCURRENT} completed")
        
        # STAGE 3D: Map unique results back to original request order
        results = []
        errors = 0
        for cache_key in request_mapping:
            if cache_key is None:
                # Invalid timestamp
                results.append(self._error_intensity('', '', 'Invalid timestamp'))
                errors += 1
            elif cache_key in unique_results:
                result = unique_results[cache_key]
                if result.get('source') == 'error':
                    errors += 1
                results.append(result)
            else:
                # Should never happen
                results.append(self._error_intensity('', '', 'Internal error'))
                errors += 1
        
        logger.info(f"✓ Carbon intensity lookup complete")
        logger.info(f"  API calls: {self.api_calls}, Cached: {self.cached_calls}, Failed: {self.failed_calls}")
        if errors > 0:
            logger.warning(f"  ⚠ {errors} requests returned errors")
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Return cache and API usage statistics"""
        return {
            'api_calls': self.api_calls,
            'cached_calls': self.cached_calls,
            'failed_calls': self.failed_calls,
            'cache_size': len(self.cache),
            'has_api_key': self.use_api,
            'total_requests': self.api_calls + self.cached_calls + self.failed_calls
        }
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("Carbon intensity cache cleared")
