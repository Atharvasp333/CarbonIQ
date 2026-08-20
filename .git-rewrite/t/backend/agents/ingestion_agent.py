"""
AGENT 1: CUR INGESTION & NORMALIZATION AGENT
Purpose: Accept AWS CUR CSV uploads and convert them into compressed, normalized dataset
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

    REQUIRED_COLUMNS = {
        'product/ProductName',
        'lineItem/UsageStartDate',
        'lineItem/UsageAmount',
        'lineItem/UnblendedCost'
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
        Process AWS CUR CSV:
        1. Skip Tax/Credit/Refund/Fee rows
        2. Keep Usage rows with usage_amount > 0
        3. Compress by (service, region, usage_type) to reduce API calls
        """
        self.validation_errors = []
        self.skipped_rows = 0
        self.processed_rows = 0
        self.original_rows = 0
        self.compressed_rows = 0

        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            columns = reader.fieldnames or []
            total_columns = len(columns)

            if not self._validate_columns(columns):
                return []

            logger.info(f"CSV has {total_columns} columns, starting row processing...")

            normalized_records = []

            for row_num, row in enumerate(reader, start=2):
                self.original_rows += 1

                if max_rows and self.original_rows > max_rows:
                    logger.info(f"Reached max_rows limit of {max_rows}")
                    break

                if self.original_rows % 500 == 0:
                    logger.info(f"  Scanned {self.original_rows} rows, found {self.processed_rows} valid...")

                try:
                    normalized = self._normalize_row(row)
                    if normalized:
                        normalized_records.append(normalized)
                        self.processed_rows += 1
                    else:
                        self.skipped_rows += 1
                except Exception as e:
                    self.skipped_rows += 1
                    if len(self.validation_errors) < 5:
                        logger.warning(f"Row {row_num}: {e}")
                    self.validation_errors.append({'row': row_num, 'error': str(e)})

            logger.info(f"Scanned {self.original_rows} rows -> {self.processed_rows} valid, {self.skipped_rows} skipped")

            if compress and normalized_records:
                compressed = self._compress_records(normalized_records)
                self.compressed_rows = len(compressed)
                logger.info(f"Compressed {len(normalized_records)} -> {len(compressed)} unique records")
                return compressed

            self.compressed_rows = len(normalized_records)
            return normalized_records

        except Exception as e:
            logger.error(f"CSV parsing failed: {e}")
            self.validation_errors.append({'row': 0, 'error': str(e)})
            return []

    def _validate_columns(self, columns: List[str]) -> bool:
        """Check minimum required columns exist"""
        missing = self.REQUIRED_COLUMNS - set(columns)
        if missing:
            err = f"Missing required columns: {missing}"
            logger.error(err)
            self.validation_errors.append({'row': 0, 'error': err})
            return False
        return True

    def _normalize_row(self, row: Dict) -> Optional[Dict]:
        """Convert a CUR row to normalized schema, returns None to skip"""

        # Skip non-usage rows
        line_item_type = row.get('lineItem/LineItemType', '')
        if line_item_type in ('Tax', 'Credit', 'Refund', 'Fee'):
            return None

        usage_amount = self._parse_float(row.get('lineItem/UsageAmount', '0'))
        cost = self._parse_float(row.get('lineItem/UnblendedCost', '0'))

        # Must have actual usage
        if usage_amount <= 0:
            return None

        product_name = row.get('product/ProductName', '').strip()
        if not product_name:
            return None

        service = self._extract_service_name(product_name)
        region = self._normalize_region(row.get('product/region', '') or row.get('product/regionCode', ''))
        start_time = self._parse_timestamp(row.get('lineItem/UsageStartDate', ''))

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
            'end_time': self._parse_timestamp(row.get('lineItem/UsageEndDate', '')),
            'resource_id': row.get('lineItem/ResourceId', '')
        }

    def _extract_service_name(self, product_name: str) -> str:
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
            'CloudWatch': ['CLOUDWATCH'],
            'Glue': ['GLUE', 'AWSGLUE'],
            'Amplify': ['AMPLIFY', 'AWSAMPLIFY'],
            'EFS': ['EFS', 'ELASTIC FILE SYSTEM', 'AMAZONEFS'],
            'API Gateway': ['API GATEWAY', 'AMAZONAPIGATEWAY', 'APIGATEWAY'],
            'DataZone': ['DATAZONE', 'AMAZONDATAZONE'],
            'Cognito': ['COGNITO', 'AMAZONCOGNITO'],
            'SNS': ['SNS', 'SIMPLE NOTIFICATION', 'AMAZONSNS'],
        }
        for service, keywords in service_map.items():
            if any(k in product_upper for k in keywords):
                return service
        return product_name[:25]

    def _normalize_region(self, region: str) -> str:
        region = (region or '').strip().lower()
        if not region or region in ('', 'global', 'n/a', 'none', 'any'):
            return 'global'
        if region.count('-') >= 2:
            return region
        region_map = {
            'us east': 'us-east-1', 'us west': 'us-west-1',
            'eu west': 'eu-west-1', 'eu central': 'eu-central-1',
            'asia pacific': 'ap-southeast-1', 'mumbai': 'ap-south-1',
        }
        for key, value in region_map.items():
            if key in region:
                return value
        return region

    def _parse_timestamp(self, ts: str) -> str:
        if not ts:
            return datetime.utcnow().replace(minute=0, second=0, microsecond=0).isoformat()
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            return dt.replace(minute=0, second=0, microsecond=0).isoformat()
        except Exception:
            return datetime.utcnow().replace(minute=0, second=0, microsecond=0).isoformat()

    def _parse_float(self, value: str) -> float:
        try:
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _compress_records(self, records: List[Dict]) -> List[Dict]:
        """
        TWO-LEVEL COMPRESSION:

        Level 1 - Key: (service, region, usage_type, DAY)
            Groups all hourly rows for the same service+region into daily buckets.
            e.g. DynamoDB ap-south-1 ReadRequestUnits across 24 hours → 1 row per day
            4918 hourly rows → ~200 daily rows

        Level 2 - Only keep one timestamp per (service, region) for carbon intensity.
            The carbon intensity agent will deduplicate by zone anyway,
            so within a day all ap-south-1 services share 1 API call.

        Result: daily granularity for charts + minimal API calls (1 per zone)

        Compression ratio for your CSV:
            5799 total rows
            - 881 Tax/Credit/zero → skipped
            = 4918 valid rows
            Grouped by (service, region, usage_type, day) → ~200 daily records
            Then carbon intensity: 3 unique zones → 3 API calls total
        """
        agg = defaultdict(lambda: {
            'usage_amount': 0.0,
            'cost': 0.0,
            'count': 0,
            'record': None
        })

        for r in records:
            # Compress to daily buckets - extract just the date part (YYYY-MM-DD)
            day = r['start_time'][:10]  # e.g. "2026-06-01"

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

        compressed = []
        for key, data in agg.items():
            rec = data['record']
            rec['usage_amount'] = data['usage_amount']
            rec['cost'] = data['cost']
            rec['_compressed_count'] = data['count']
            compressed.append(rec)

        logger.info(f"  Compression: (service, region, usage_type, day) grouping")
        logger.info(f"  {len(records)} valid rows -> {len(compressed)} daily records")
        return compressed

    def get_validation_summary(self) -> Dict:
        return {
            'original_rows': self.original_rows,
            'processed_rows': self.processed_rows,
            'compressed_rows': self.compressed_rows,
            'skipped_rows': self.skipped_rows,
            'columns_removed': self.columns_removed,
            'compression_ratio': (
                f"{(1 - self.compressed_rows / self.processed_rows) * 100:.1f}%"
                if self.processed_rows > 0 else "0%"
            ),
            'errors': self.validation_errors[:5],
            'total_errors': len(self.validation_errors)
        }
