"""
COMPRESSION AGENT (Carbon Accounting Engine)
Purpose: Compress normalized CUR records to reduce API calls and improve performance

TWO-LEVEL COMPRESSION STRATEGY:
- Level 1: Group by (service, region, usage_type, DAY) for daily granularity
- Level 2: Deduplicate timestamps per zone for minimal API calls

Example: 5000 hourly rows → 200 daily rows → 3 unique zone/day combos → 3 API calls
"""
import logging
from typing import List, Dict, Optional, cast
from collections import defaultdict

logger = logging.getLogger(__name__)


class CompressionAgent:
    """Compresses normalized CUR records for efficient processing"""
    
    def __init__(self):
        self.original_count = 0
        self.compressed_count = 0
        self.compression_ratio = 0.0
    
    def compress_records(self, records: List[Dict]) -> List[Dict]:
        """
        Compress records by grouping on (service, region, usage_type, day)
        
        Args:
            records: List of normalized records from CSV agent
        
        Returns:
            Compressed list of records
        """
        self.original_count = len(records)
        
        if not records:
            return cast(List[Dict], [])
        
        logger.info(f"[Compression Agent] Compressing {len(records)} records...")
        
        def _empty_bucket() -> Dict[str, object]:
            return {
                'usage_amount': 0.0,
                'cost': 0.0,
                'count': 0,
                'record': cast(Optional[Dict], None)
            }

        agg: defaultdict[tuple, Dict[str, object]] = defaultdict(_empty_bucket)
        
        for r in records:
            # Extract just the date part for daily grouping
            day = r['start_time'][:10]  # YYYY-MM-DD
            
            key = (
                r['service'],
                r['region'],
                r.get('usage_type', ''),
                day
            )
            
            agg[key]['usage_amount'] += r['usage_amount']
            agg[key]['cost'] += r['cost']
            agg[key]['count'] += 1
            
            if agg[key]['record'] is None:
                agg[key]['record'] = r.copy()
                # Normalize timestamp to midnight of that day for cache efficiency
                agg[key]['record']['start_time'] = f"{day}T00:00:00+00:00"
        
        compressed: List[Dict] = []
        for key, data in agg.items():
            rec = data['record']
            if rec is None:
                continue  # should never happen, but satisfies type checker
            rec['usage_amount'] = data['usage_amount']
            rec['cost'] = data['cost']
            rec['_compressed_count'] = data['count']
            compressed.append(rec)
        
        self.compressed_count = len(compressed)
        self.compression_ratio = (
            (1 - self.compressed_count / self.original_count) * 100
            if self.original_count > 0 else 0
        )
        
        logger.info(f"  Compression: {self.original_count} → {self.compressed_count} records")
        logger.info(f"  Ratio: {self.compression_ratio:.1f}% reduction")
        
        return compressed
    
    def get_compression_stats(self) -> Dict:
        """Return compression statistics"""
        return {
            'original_count': self.original_count,
            'compressed_count': self.compressed_count,
            'compression_ratio': f"{self.compression_ratio:.1f}%",
            'records_saved': self.original_count - self.compressed_count
        }
