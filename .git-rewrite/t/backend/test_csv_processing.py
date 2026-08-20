"""
Test CSV Processing - See exactly how your CSV is filtered
Run: python backend/test_csv_processing.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents.ingestion_agent import CURIngestionAgent


def test_csv_processing():
    """Test with your actual CSV to see row/column filtering"""
    
    print("\n" + "="*80)
    print("CSV PROCESSING TEST - See How Rows & Columns Are Filtered")
    print("="*80)
    
    # Load your actual CSV
    csv_path = Path(__file__).parent.parent / "CUR_report-00001.csv"
    
    if not csv_path.exists():
        print(f"\n❌ CSV not found at: {csv_path}")
        print("Please make sure CUR_report-00001.csv is in project root")
        return
    
    print(f"\n📂 Loading CSV: {csv_path.name}")
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_content = f.read()
    
    total_lines = csv_content.count('\n')
    file_size_mb = len(csv_content) / (1024 * 1024)
    
    print(f"   File size: {file_size_mb:.2f} MB")
    print(f"   Total lines: {total_lines:,}")
    
    # Initialize agent
    agent = CURIngestionAgent()
    
    print("\n" + "="*80)
    print("STEP 1: COLUMN ANALYSIS")
    print("="*80)
    
    # Parse first line to get columns
    import csv
    import io
    reader = csv.DictReader(io.StringIO(csv_content))
    columns = reader.fieldnames or []
    
    print(f"\n📊 Total Columns in CSV: {len(columns)}")
    
    print("\n✅ REQUIRED COLUMNS (4 must exist):")
    required = [
        'product/ProductName',
        'lineItem/UsageStartDate',
        'lineItem/UsageAmount',
        'lineItem/UnblendedCost'
    ]
    for col in required:
        status = "✅" if col in columns else "❌"
        print(f"   {status} {col}")
    
    print("\n✅ OPTIONAL COLUMNS USED (9 additional):")
    optional = [
        'lineItem/LineItemType',
        'lineItem/UsageEndDate',
        'product/region',
        'product/regionCode',
        'product/location',
        'product/productFamily',
        'lineItem/UsageType',
        'lineItem/Operation',
        'lineItem/ResourceId',
    ]
    for col in optional:
        status = "✅" if col in columns else "⚠️ "
        print(f"   {status} {col}")
    
    print(f"\n❌ IGNORED COLUMNS ({len(columns) - 13}):")
    used_cols = set(required + optional)
    ignored = [c for c in columns if c not in used_cols]
    for i, col in enumerate(ignored[:10], 1):
        print(f"   {i}. {col}")
    if len(ignored) > 10:
        print(f"   ... and {len(ignored) - 10} more columns")
    
    print("\n" + "="*80)
    print("STEP 2: ROW PROCESSING (First 10 rows detailed)")
    print("="*80)
    
    # Manually process first 10 rows to show decisions
    reader = csv.DictReader(io.StringIO(csv_content))
    
    print("\n🔍 Detailed Processing of First 10 Rows:")
    print("-" * 80)
    
    for i, row in enumerate(reader, 1):
        if i > 10:
            break
        
        line_type = row.get('lineItem/LineItemType', '')
        product = row.get('product/ProductName', '')
        usage = row.get('lineItem/UsageAmount', '0')
        cost = row.get('lineItem/UnblendedCost', '0')
        
        try:
            usage_float = float(usage) if usage else 0.0
        except:
            usage_float = 0.0
        
        print(f"\nRow {i}:")
        print(f"   LineItemType: {line_type}")
        print(f"   ProductName: {product[:50]}")
        print(f"   UsageAmount: {usage}")
        print(f"   Cost: {cost}")
        
        # Decision logic
        if line_type in ('Tax', 'Credit', 'Refund', 'Fee'):
            print(f"   ❌ SKIPPED - Reason: LineItemType = '{line_type}' (not usage)")
        elif usage_float <= 0:
            print(f"   ❌ SKIPPED - Reason: UsageAmount = 0 (no actual usage)")
        elif not product:
            print(f"   ❌ SKIPPED - Reason: Missing ProductName")
        else:
            print(f"   ✅ KEPT - Valid usage row")
    
    print("\n" + "="*80)
    print("STEP 3: FULL CSV PROCESSING")
    print("="*80)
    
    print("\n⏳ Processing all rows (this may take a few seconds)...")
    
    # Process full CSV with compression
    records = agent.process_csv(csv_content, max_rows=None, compress=True)
    
    summary = agent.get_validation_summary()
    
    print("\n✅ PROCESSING COMPLETE!")
    print("="*80)
    
    print(f"\n📊 STATISTICS:")
    print(f"   Original Rows:     {summary['original_rows']:>6,}")
    print(f"   Valid Rows:        {summary['processed_rows']:>6,}")
    print(f"   Skipped Rows:      {summary['skipped_rows']:>6,}")
    print(f"   Compressed Rows:   {summary['compressed_rows']:>6,}")
    print(f"   Compression Ratio: {summary['compression_ratio']:>6}")
    
    print(f"\n🎯 ROW FILTERING:")
    print(f"   Kept:    {summary['processed_rows']:>6,} rows ({summary['processed_rows']/summary['original_rows']*100:.1f}%)")
    print(f"   Removed: {summary['skipped_rows']:>6,} rows ({summary['skipped_rows']/summary['original_rows']*100:.1f}%)")
    
    print(f"\n🗜️  COMPRESSION:")
    print(f"   Before: {summary['processed_rows']:>6,} rows (hourly data)")
    print(f"   After:  {summary['compressed_rows']:>6,} rows (daily aggregates)")
    print(f"   Saved:  {summary['processed_rows'] - summary['compressed_rows']:>6,} rows")
    
    print(f"\n📦 DATA REDUCTION:")
    total_reduction = (1 - summary['compressed_rows'] / summary['original_rows']) * 100
    print(f"   {summary['original_rows']:,} → {summary['compressed_rows']:,} rows ({total_reduction:.1f}% reduction)")
    
    # Show sample records
    print("\n" + "="*80)
    print("STEP 4: SAMPLE PROCESSED RECORDS")
    print("="*80)
    
    if records:
        print(f"\n📋 Showing first 5 compressed records:\n")
        for i, rec in enumerate(records[:5], 1):
            print(f"Record {i}:")
            print(f"   Service: {rec['service']}")
            print(f"   Region: {rec['region']}")
            print(f"   Usage Type: {rec['usage_type'][:50]}")
            print(f"   Usage Amount: {rec['usage_amount']:.2f}")
            print(f"   Cost: ${rec['cost']:.4f}")
            print(f"   Timestamp: {rec['start_time']}")
            if '_compressed_count' in rec:
                print(f"   Compressed From: {rec['_compressed_count']} hourly rows")
            print()
    
    # Service breakdown
    print("="*80)
    print("STEP 5: SERVICE BREAKDOWN")
    print("="*80)
    
    from collections import defaultdict
    
    service_stats = defaultdict(lambda: {'count': 0, 'usage': 0, 'cost': 0})
    for rec in records:
        service = rec['service']
        service_stats[service]['count'] += 1
        service_stats[service]['usage'] += rec['usage_amount']
        service_stats[service]['cost'] += rec['cost']
    
    print(f"\n📊 Services Found: {len(service_stats)}")
    print("\nTop 10 Services by Cost:")
    print("-" * 80)
    print(f"{'Service':<25} {'Records':>10} {'Cost':>15}")
    print("-" * 80)
    
    sorted_services = sorted(
        service_stats.items(),
        key=lambda x: x[1]['cost'],
        reverse=True
    )
    
    for i, (service, stats) in enumerate(sorted_services[:10], 1):
        print(f"{service:<25} {stats['count']:>10} ${stats['cost']:>14.2f}")
    
    # Region breakdown
    print("\n" + "="*80)
    print("STEP 6: REGION BREAKDOWN")
    print("="*80)
    
    region_stats = defaultdict(lambda: {'count': 0, 'cost': 0})
    for rec in records:
        region = rec['region']
        region_stats[region]['count'] += 1
        region_stats[region]['cost'] += rec['cost']
    
    print(f"\n🌍 Regions Found: {len(region_stats)}")
    print("\nAll Regions:")
    print("-" * 80)
    print(f"{'Region':<20} {'Records':>10} {'Cost':>15}")
    print("-" * 80)
    
    sorted_regions = sorted(
        region_stats.items(),
        key=lambda x: x[1]['cost'],
        reverse=True
    )
    
    for region, stats in sorted_regions:
        print(f"{region:<20} {stats['count']:>10} ${stats['cost']:>14.2f}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    print("\nKey Takeaways:")
    print(f"1. Only 13/{len(columns)} columns are used (86% ignored)")
    print(f"2. {summary['skipped_rows']:,}/{summary['original_rows']:,} rows removed (tax/zero-usage)")
    print(f"3. {summary['processed_rows']:,} valid rows compressed to {summary['compressed_rows']:,} daily records")
    print(f"4. Found {len(service_stats)} unique services across {len(region_stats)} regions")
    print(f"5. Total data reduction: {total_reduction:.1f}%")
    print()


if __name__ == "__main__":
    test_csv_processing()
