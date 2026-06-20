"""
CARBONIQ MAIN ORCHESTRATOR
Coordinates both Carbon Accounting and Sustainability Intelligence Engines

SYSTEM 1: Carbon Accounting Engine
- Purpose: "What happened?"
- Input: AWS CUR CSV
- Output: Historical emissions, analysis summary (stored in database)

SYSTEM 2: Sustainability Intelligence Engine  
- Purpose: "What should we do?"
- Input: Stored accounting results + organization profile
- Output: Recommendations (stored in database)

SEPARATION RULES:
- Accounting engine NEVER generates recommendations
- Intelligence engine NEVER touches CUR files or recalculates emissions
- Communication through database tables ONLY
"""
import logging
from typing import Dict, Optional
from .accounting.accounting_engine import CarbonAccountingEngine
from .intelligence.intelligence_engine import SustainabilityIntelligenceEngine

logger = logging.getLogger(__name__)


class CarbonIQOrchestrator:
    """
    Main orchestrator coordinating both Carbon Accounting and Intelligence engines
    """
    
    def __init__(self):
        self.accounting_engine = CarbonAccountingEngine()
        self.intelligence_engine = SustainabilityIntelligenceEngine()
    
    async def process_cur_only(
        self,
        csv_content: str,
        max_rows: int = 1000
    ) -> Dict:
        """
        Run ONLY Carbon Accounting Engine
        
        Use case: Dashboard display of historical emissions
        
        Args:
            csv_content: AWS CUR CSV content
            max_rows: Maximum rows to process
        
        Returns:
            Accounting results (emissions, summary)
        """
        logger.info("="*80)
        logger.info("MODE: ACCOUNTING ONLY")
        logger.info("="*80)
        
        accounting_result = await self.accounting_engine.process_cur(
            csv_content=csv_content,
            max_rows=max_rows
        )
        
        if not accounting_result['success']:
            return accounting_result
        
        return {
            'success': True,
            'mode': 'accounting_only',
            'accounting': accounting_result,
            'intelligence': None
        }
    
    async def generate_insights_only(
        self,
        analysis_summary: Dict,
        emission_records: list,
        org_profile: Optional[Dict] = None,
        use_gemini: bool = False
    ) -> Dict:
        """
        Run ONLY Sustainability Intelligence Engine
        
        Use case: Generate recommendations from stored accounting data
        
        Args:
            analysis_summary: Precomputed analysis from database
            emission_records: Emission records from database
            org_profile: Organization constraints
            use_gemini: Use Gemini for explanations
        
        Returns:
            Intelligence results (recommendations)
        """
        logger.info("="*80)
        logger.info("MODE: INTELLIGENCE ONLY")
        logger.info("="*80)
        
        intelligence_result = await self.intelligence_engine.generate_insights(
            analysis_summary=analysis_summary,
            emission_records=emission_records,
            org_profile=org_profile,
            use_gemini=use_gemini
        )
        
        if not intelligence_result['success']:
            return intelligence_result
        
        return {
            'success': True,
            'mode': 'intelligence_only',
            'accounting': None,
            'intelligence': intelligence_result
        }
    
    async def process_cur_with_insights(
        self,
        csv_content: str,
        max_rows: int = 1000,
        org_profile: Optional[Dict] = None,
        use_gemini: bool = False
    ) -> Dict:
        """
        Run BOTH engines in sequence
        
        Use case: Complete end-to-end analysis with recommendations
        
        Args:
            csv_content: AWS CUR CSV content
            max_rows: Maximum rows to process
            org_profile: Organization constraints
            use_gemini: Use Gemini for explanations
        
        Returns:
            Complete results (accounting + intelligence)
        """
        logger.info("="*80)
        logger.info("MODE: COMPLETE PIPELINE (ACCOUNTING + INTELLIGENCE)")
        logger.info("="*80)
        
        # STEP 1: Carbon Accounting
        logger.info("\n" + "▶"*40)
        logger.info("STEP 1: CARBON ACCOUNTING ENGINE")
        logger.info("▶"*40 + "\n")
        
        accounting_result = await self.accounting_engine.process_cur(
            csv_content=csv_content,
            max_rows=max_rows
        )
        
        if not accounting_result['success']:
            return {
                'success': False,
                'error': 'Accounting engine failed',
                'mode': 'complete_pipeline',
                'accounting': accounting_result,
                'intelligence': None
            }
        
        # STEP 2: Sustainability Intelligence
        logger.info("\n" + "▶"*40)
        logger.info("STEP 2: SUSTAINABILITY INTELLIGENCE ENGINE")
        logger.info("▶"*40 + "\n")
        
        intelligence_result = await self.intelligence_engine.generate_insights(
            analysis_summary=accounting_result['analysis_summary'],
            emission_records=accounting_result['emission_records'],
            org_profile=org_profile,
            use_gemini=use_gemini
        )
        
        if not intelligence_result['success']:
            return {
                'success': False,
                'error': 'Intelligence engine failed',
                'mode': 'complete_pipeline',
                'accounting': accounting_result,
                'intelligence': intelligence_result
            }
        
        logger.info("\n" + "="*80)
        logger.info("COMPLETE PIPELINE SUCCESS")
        logger.info("="*80)
        logger.info(f"Accounting: {accounting_result['analysis_summary']['total_emissions_kg']:.2f}kg CO2")
        logger.info(f"Intelligence: {len(intelligence_result['recommendations'])} recommendations")
        logger.info(f"Potential Reduction: {intelligence_result['summary']['total_potential_reduction_kg']:.2f}kg CO2")
        logger.info("="*80 + "\n")
        
        return {
            'success': True,
            'mode': 'complete_pipeline',
            'accounting': accounting_result,
            'intelligence': intelligence_result,
            'summary': {
                'total_emissions_kg': accounting_result['analysis_summary']['total_emissions_kg'],
                'total_cost': accounting_result['analysis_summary']['total_cost'],
                'recommendations_count': len(intelligence_result['recommendations']),
                'potential_reduction_kg': intelligence_result['summary']['total_potential_reduction_kg'],
                'potential_reduction_pct': intelligence_result['summary'].get('total_potential_reduction_pct', 0)
            }
        }
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            'accounting_engine': 'ready',
            'intelligence_engine': 'ready',
            'modes_available': [
                'accounting_only',
                'intelligence_only',
                'complete_pipeline'
            ]
        }
