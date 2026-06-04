"""
AGENT 1: CUR INGESTION & NORMALIZATION AGENT (OPTIMIZED)
Purpose: Accept AWS CUR CSV uploads and convert them into compressed, normalized dataset

OPTIMIZATIONS:
- Column filtering: Keep ONLY required columns
- Row compression: Aggregate identical records
- Timestamp normalization: Round to hourly buckets
- Batch processing: Process in configurable chunks
"""
import csv
import io
import logging
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class CURIngestionAgent:
    """Validates, normalizes, compresses, and standardizes AWS CUR data"""
    
    # ONLY columns needed for emission calculation
    REQUIRED_COLUMNS = {
        'product/ProductName',
        'product/region',
        'lineItem/UsageStartDate',
        'lineItem/UsageAmount',
        'lineItem/UnblendedCost'
    }
    
    # Optional columns (used if available, not required)
    OPTIONAL_COLUMNS = {
        'product/location',
        'product/productFamily',
        'lineItem/UsageType',
        'lineItem/Operation',
        'lineItem/UsageEndDate',
        'lineItem/ResourceId'
    }
    
    def __init__(self):
        self.validation_errors = []
        self.skipped_rows = 0
        self.processed_rows = 0
        self.original_rows = 0
        self.compressed_rows = 0
        self.columns_removed = 0
    
    def process_csv(self, csv_content: str, max_rows: int = None, compress: bool = True) -> List[Dict]:
        """
        Process AWS CUR CSV with aggressive optimization
        
        OPTIMIZATIONS APPLIED:
        1. Column filtering - drop unnecessary columns immediately
        2. Row compression - aggregate identical records
        3. Timestamp normalization - round to hourly buckets
        
        Args:
            csv_content: Raw CSV string
            max_rows: Optional limit on rows to process (applied BEFORE compression)
            compress: Enable row compression (default: True)
        
        Returns: List of compressed, normalized records
        """
        self.validation_errors = []
        self.skipped_rows = 0
        self.processed_rows = 0
        self.original_rows = 0
        self.compressed_rows = 0
        
        logger.info("="*60)
        logger.info("STAGE 1A: Column Filtering & Row Normalization")
        logger.info("="*60)
        
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            columns = reader.fieldnames or []
            
            # Log column reduction
            total_columns = len(columns)
            kept_columns = self.REQUIRED_COLUMNS | self.OPTIONAL_COLUMNS
            self.columns_removed = total_columns - len(kept_columns)
            logger.info(f"CSV columns: {total_columns} total, keeping {len(kept_columns)}, dropping {self.columns_removed}")
            
            # Validate required columns exist
            if not self._validate_columns(columns):
                return []
            
            # STAGE 1: Normalize rows (filter columns implicitly during normalization)
            normalized_records = []
            row_count = 0
            
            for row_num, row in enumerate(reader, start=2):
                self.original_rows += 1
                
                # Check max_rows limit FIRST (before any processing)
                if max_rows and self.original_rows > max_rows:
                    logger.info(f"Reached max_rows limit of {max_rows}, stopping ingestion")
                    break
                
                # Progress logging every 100 rows for faster feedback
                if self.original_rows % 100 == 0:
                    logger.info(f"  Normalized {self.original_rows} rows...")
                    
                try:
                    normalized_row = self._normalize_row(row)
                    if normalized_row:
                        normalized_records.append(normalized_row)
                        self.processed_rows += 1
                except Exception as e:
                    self.skipped_rows += 1
                    if self.skipped_rows <= 5:  # Only log first 5 errors
                        logger.warning(f"Row {row_num}: {str(e)}")
                    self.validation_errors.append({
                        'row': row_num,
                        'error': str(e)
                    })
            
            logger.info(f"✓ Normalized: {self.processed_rows} valid rows, skipped {self.skipped_rows} invalid rows")
            
            # STAGE 2: Compress identical records
            if compress and normalized_records:
                logger.info("="*60)
                logger.info("STAGE 1B: Row Compression")
                logger.info("="*60)
                compressed_records = self._compress_records(normalized_records)
                logger.info(f"✓ Compressed: {len(normalized_records)} rows → {len(compressed_records)} unique records")
                logger.info(f"  Compression ratio: {(1 - len(compressed_records)/len(normalized_records))*100:.1f}% reduction")
                self.compressed_rows = len(compressed_records)
                return compressed_records
            
            self.compressed_rows = len(normalized_records)
            return normalized_records
            
        except Exception as e:
            logger.error(f"CSV parsing failed: {str(e)}")
            self.validation_errors.append({'row': 0, 'error': f"CSV parsing failed: {str(e)}"})
            return []
    
    def _validate_columns(self, columns: List[str]) -> bool:
        """Check if CSV has minimum required columns"""
        column_set = set(columns)
        missing = self.REQUIRED_COLUMNS - column_set
        
        if missing:
            error_msg = f"Missing required columns: {', '.join(missing)}"
            logger.error(error_msg)
            self.validation_errors.append({'row': 0, 'error': error_msg})
            return False
        
        return True
    
    def _normalize_row(self, row: Dict) -> Optional[Dict]:
        """Convert CUR row to CarbonIQ schema"""
        # Skip tax and empty rows
        line_item_type = row.get('lineItem/LineItemType', '')
        if line_item_type in ['Tax', 'Credit', 'Refund', 'Fee']:
            return None
        
        # Extract and validate usage amount
        usage_amount = self._parse_float(row.get('lineItem/UsageAmount', '0'), 'UsageAmount')
        cost = self._parse_float(row.get('lineItem/UnblendedCost', '0'), 'UnblendedCost')
        
        # Skip zero-usage rows
        if usage_amount <= 0 and cost <= 0:
            return None
        
        # Extract service name
        product_name = row.get('product/ProductName', '').strip()
        if not product_name:
            raise ValueError("Missing product name")
        
        service = self._extract_service_name(product_name)
        
        # Extract and normalize region
        region = self._normalize_region(row.get('product/region', ''))
        
        # Extract timestamps
        start_time = self._parse_timestamp(row.get('lineItem/UsageStartDate', ''))
        end_time = self._parse_timestamp(row.get('lineItem/UsageEndDate', ''))
        
        # Build normalized record
        return {
            'service': service,
            'region': region,
            'location': row.get('product/location', ''),
            'product_family': row.get('product/productFamily', ''),
            'usage_type': row.get('lineItem/UsageType', ''),
            'operation': row.get('lineItem/Operation', ''),
            'usage_amount': usage_amount,
            'cost': cost,
            'start_time': start_time,
            'end_time': end_time,
            'resource_id': row.get('lineItem/ResourceId', '')
        }
    
    def _extract_service_name(self, product_name: str) -> str:
        """Extract clean service name from AWS product name"""
        product_upper = product_name.upper()
        
        service_map = {
            'EC2': ['EC2', 'ELASTIC COMPUTE', 'AMAZONEC2'],
            'Lambda': ['LAMBDA', 'AWSLAMBDA'],
            'S3': ['S3', 'SIMPLE STORAGE', 'AMAZONS3'],
            'RDS': ['RDS', 'RELATIONAL DATABASE', 'AMAZONRDS'],
            'SageMaker': ['SAGEMAKER', 'AMAZONSAGEMAKER'],
            'EBS': ['EBS', 'ELASTIC BLOCK'],
            'ECS': ['ECS', 'ELASTIC CONTAINER SERVICE'],
            'EKS': ['EKS', 'ELASTIC KUBERNETES'],
            'DynamoDB': ['DYNAMODB', 'AMAZONDYNAMODB'],
            'CloudFront': ['CLOUDFRONT', 'AMAZONCLOUDFRONT'],
            'ElastiCache': ['ELASTICACHE', 'AMAZONELASTICACHE'],
        }
        
        for service, keywords in service_map.items():
            if any(keyword in product_upper for keyword in keywords):
                return service
        
        # Return first 20 chars for unknown services
        return product_name[:20]
    
    def _normalize_region(self, region: str) -> str:
        """Normalize AWS region codes"""
        region = region.strip().lower()
        
        # Handle empty or global regions
        if not region or region in ['', 'global', 'n/a', 'none']:
            return 'us-east-1'  # Default to us-east-1
        
        # Already in correct format (e.g., us-east-1)
        if region.count('-') == 2:
            return region
        
        # Map common variations
        region_map = {
            'us east': 'us-east-1',
            'us west': 'us-west-1',
            'eu west': 'eu-west-1',
            'eu central': 'eu-central-1',
            'asia pacific': 'ap-southeast-1',
            'mumbai': 'ap-south-1',
        }
        
        for key, value in region_map.items():
            if key in region:
                return value
        
        return region
    
    def _parse_timestamp(self, timestamp_str: str) -> str:
        """
        Parse and NORMALIZE timestamp to hourly bucket
        
        OPTIMIZATION: Round timestamps to hour for API call deduplication
        Example: 2026-01-05 14:17:23 → 2026-01-05 14:00:00
        """
        if not timestamp_str:
            return datetime.utcnow().replace(minute=0, second=0, microsecond=0).isoformat()
        
        try:
            # AWS CUR uses ISO format: 2026-05-01T00:00:00Z
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # NORMALIZE: Round to hour
            dt_hourly = dt.replace(minute=0, second=0, microsecond=0)
            return dt_hourly.isoformat()
        except Exception:
            # Fallback to current hour
            return datetime.utcnow().replace(minute=0, second=0, microsecond=0).isoformat()
    
    def _parse_float(self, value: str, field_name: str) -> float:
        """Parse float value with validation"""
        try:
            return float(value) if value else 0.0
        except ValueError:
            raise ValueError(f"Invalid {field_name}: {value}")
    
    def _compress_records(self, records: List[Dict]) -> List[Dict]:
        """
        Compress identical records by aggregating them
        
        COMPRESSION KEY: (service, region, start_time, usage_type, operation)
        AGGREGATED: usage_amount, cost, count
        
        Example: 100 identical EC2 records → 1 aggregated record with totals
        """
        compression_map = defaultdict(lambda: {
            'usage_amount': 0,
            'cost': 0,
            'count': 0,
            'record': None
        })
        
        for record in records:
            # Create compression key
            key = (
                record['service'],
                record['region'],
                record['start_time'],  # Already normalized to hour
                record.get('usage_type', ''),
                record.get('operation', '')
            )
            
            # Aggregate
            compression_map[key]['usage_amount'] += record['usage_amount']
            compression_map[key]['cost'] += record['cost']
            compression_map[key]['count'] += 1
            
            # Store first record as template
            if compression_map[key]['record'] is None:
                compression_map[key]['record'] = record.copy()
        
        # Build compressed records
        compressed = []
        for key, data in compression_map.items():
            record = data['record']
            record['usage_amount'] = data['usage_amount']
            record['cost'] = data['cost']
            record['_compressed_count'] = data['count']  # Track compression
            compressed.append(record)
        
        return compressed
    
    def get_validation_summary(self) -> Dict:
        """Return summary of validation and compression results"""
        return {
            'original_rows': self.original_rows,
            'processed_rows': self.processed_rows,
            'compressed_rows': self.compressed_rows,
            'skipped_rows': self.skipped_rows,
            'columns_removed': self.columns_removed,
            'compression_ratio': (
                f"{(1 - self.compressed_rows/self.processed_rows)*100:.1f}%"
                if self.processed_rows > 0 else "0%"
            ),
            'errors': self.validation_errors[:5],  # First 5 errors only
            'total_errors': len(self.validation_errors)
        }
