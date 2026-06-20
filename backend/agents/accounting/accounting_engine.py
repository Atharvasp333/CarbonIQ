"""
CARBON ACCOUNTING ENGINE
Purpose: "What happened?"

Pipeline:
AWS CUR → CSV Agent → Compression → Region Mapping → Carbon Intensity → Emission Calculation → Analysis Summary → Database

Outputs:
- analyses table
- emission_records table
- analysis_summary table
- api_call_logs table

RULES:
- NO AI/recommendations
- NO optimization logic
- ONLY historical accounting
- Store results for Intelligence Engine to consume
"""
import logging
from typing import Dict, List
from .csv_agent import CURIngestionAgent
from .compression_agent import CompressionAgent
from .region_mapping_agent import RegionMappingAgent
from .carbon_intensity_agent import CarbonIntensityAgent
from .emission_calculation_agent import EmissionCalculationAgent
from .analysis_summary_agent import AnalysisSummaryAgent

logger = logging.getLogger(__name__)


class CarbonAccountingEngine:
    """
    Carbon Accounting Engine - answers "What happened?"
    Processes AWS CUR and calculates historical emissions
    """
    
    def __init__(self):
        self.csv_agent = CURIngestionAgent()
        self.compression_agent = CompressionAgent()
        self.region_agent = RegionMappingAgent()
        self.carbon_intensity_agent = CarbonIntensityAgent()
        self.emission_agent = EmissionCalculationAgent()
        self.summary_agent = AnalysisSummaryAgent()
    
    async def process_cur(
        self,
        csv_content: str,
        max_rows: int = 1000
    ) -> Dict:
        """
        Process AWS CUR through accounting pipeline
        
        Args:
            csv_content: Raw AWS CUR CSV content
            max_rows: Maximum rows to process
        
        Returns:
            Complete accounting result with emission records and summary
        """
        import time
        start_time = time.time()
        
        logger.info("="*80)
        logger.info("CARBON ACCOUNTING ENGINE")
        logger.info("="*80)
        logger.info(f"CSV size: {len(csv_content):,} bytes")
        logger.info(f"Max rows: {max_rows:,}")
        
        try:
            # STAGE 1: CSV Ingestion & Normalization
            logger.info("\n[1/6] CSV Ingestion Agent")
            logger.info("-"*80)
            normalized_records = self.csv_agent.process_csv(
                csv_content,
                max_rows=max_rows,
                compress=False  # Compression done separately
            )
            
            if not normalized_records:
                return self._error_response("No valid records found in CSV")
            
            ingestion_summary = self.csv_agent.get_validation_summary()
            logger.info(f"✓ Ingested {len(normalized_records)} records")
            
            # STAGE 2: Compression
            logger.info("\n[2/6] Compression Agent")
            logger.info("-"*80)
            compressed_records = self.compression_agent.compress_records(normalized_records)
            compression_stats = self.compression_agent.get_compression_stats()
            logger.info(f"✓ Compressed to {len(compressed_records)} records ({compression_stats['compression_ratio']})")
            
            # STAGE 3: Region Mapping
            logger.info("\n[3/6] Region Mapping Agent")
            logger.info("-"*80)
            regions = list(set(r['region'] for r in compressed_records))
            region_mappings = self.region_agent.map_batch(regions)
            
            # Attach zone to records
            for record in compressed_records:
                mapping = region_mappings.get(record['region'], {})
                record['zone'] = mapping.get('electricity_maps_zone', 'US-MIDA-PJM')
                record['location_name'] = mapping.get('location_name', 'Unknown')
            
            region_stats = self.region_agent.get_mapping_summary()
            logger.info(f"✓ Mapped {len(region_mappings)} regions to electricity zones")
            
            # STAGE 4: Historical Carbon Intensity
            logger.info("\n[4/6] Carbon Intensity Agent")
            logger.info("-"*80)
            intensity_requests = [
                {'zone': r['zone'], 'timestamp': r['start_time']}
                for r in compressed_records
            ]
            
            intensity_results = await self.carbon_intensity_agent.get_batch_intensities(intensity_requests)
            
            # Attach intensity to records
            valid_records = []
            for record, intensity_result in zip(compressed_records, intensity_results):
                record['carbon_intensity'] = intensity_result['carbon_intensity']
                record['intensity_source'] = intensity_result.get('source', 'fallback')
                valid_records.append(record)
            
            intensity_stats = self.carbon_intensity_agent.get_cache_stats()
            logger.info(f"✓ Retrieved carbon intensity for {len(valid_records)} records")
            logger.info(f"  API calls: {intensity_stats['api_calls']}, Cached: {intensity_stats['cached_calls']}, Failed: {intensity_stats['failed_calls']}")
            
            # STAGE 5: Emission Calculation
            logger.info("\n[5/6] Emission Calculation Agent")
            logger.info("-"*80)
            workloads = [
                {
                    'service': r['service'],
                    'region': r['region'],
                    'zone': r['zone'],
                    'usage_amount': r['usage_amount'],
                    'carbon_intensity': r['carbon_intensity'],
                    'usage_type': r['usage_type'],
                    'operation': r['operation'],
                    'timestamp': r['start_time'],
                    'cost': r['cost'],
                    'resource_id': r['resource_id']
                }
                for r in valid_records
            ]
            
            emission_records = self.emission_agent.calculate_batch(workloads)
            emission_stats = self.emission_agent.get_calculation_stats()
            logger.info(f"✓ Calculated emissions: {emission_stats['total_emissions_kg']:.2f}kg CO2")
            
            # STAGE 6: Analysis Summary
            logger.info("\n[6/6] Analysis Summary Agent")
            logger.info("-"*80)
            analysis_summary = self.summary_agent.generate_summary(emission_records)
            summary_stats = self.summary_agent.get_stats()
            logger.info(f"✓ Generated analysis summary")
            
            duration = time.time() - start_time
            
            logger.info("\n" + "="*80)
            logger.info("ACCOUNTING ENGINE COMPLETE")
            logger.info("="*80)
            logger.info(f"Total Emissions: {analysis_summary['total_emissions_kg']:.2f}kg CO2")
            logger.info(f"Total Cost: ${analysis_summary['total_cost']:.2f}")
            logger.info(f"Total Energy: {analysis_summary['total_energy_kwh']:.2f}kWh")
            logger.info(f"Records Processed: {len(emission_records)}")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info("="*80 + "\n")
            
            return {
                'success': True,
                'emission_records': emission_records,
                'analysis_summary': analysis_summary,
                'pipeline_stats': {
                    'ingestion': ingestion_summary,
                    'compression': compression_stats,
                    'region_mapping': region_stats,
                    'carbon_intensity': intensity_stats,
                    'emission_calculation': emission_stats,
                    'analysis_summary': summary_stats,
                    'duration_seconds': round(duration, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Accounting engine error: {str(e)}", exc_info=True)
            return self._error_response(f"Accounting engine error: {str(e)}")
    
    def _error_response(self, message: str) -> Dict:
        """Generate error response"""
        return {
            'success': False,
            'error': message,
            'emission_records': [],
            'analysis_summary': {},
            'pipeline_stats': {}
        }
