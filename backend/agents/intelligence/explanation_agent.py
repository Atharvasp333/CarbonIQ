"""
GEMINI EXPLANATION AGENT (OPTIONAL)
Converts structured recommendations into business-friendly language

IMPORTANT: Gemini should ONLY:
- Explain recommendations in natural language
- Provide context and rationale
- Make technical details accessible

Gemini should NEVER:
- Calculate emissions
- Calculate reductions
- Determine opportunities
- Generate metrics
- Make recommendations

All data comes from deterministic agents.
"""
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class GeminiExplanationAgent:
    """
    Converts structured recommendations into natural language explanations
    """
    
    def __init__(self):
        self.gemini_available = False
        self.explanation_stats = {
            'explanations_generated': 0,
            'gemini_calls': 0,
            'fallback_used': 0
        }
        
        # Check if Gemini is available
        try:
            from ..services.gemini import get_gemini_insight
            self.get_gemini_insight = get_gemini_insight
            self.gemini_available = True
            logger.info("Gemini API available for explanations")
        except Exception as e:
            logger.warning(f"Gemini API not available: {e}")
            self.gemini_available = False
    
    async def explain_recommendations(
        self,
        recommendations: List[Dict],
        workload_analysis: Dict,
        use_gemini: bool = True
    ) -> Dict:
        """
        Generate natural language explanations for recommendations
        
        Args:
            recommendations: List of recommendations from RecommendationAgent
            workload_analysis: Analysis from WorkloadAnalysisAgent
            use_gemini: Whether to use Gemini API (default: True)
        
        Returns:
            Dict with explained recommendations
        """
        logger.info("="*60)
        logger.info("[Gemini Explanation Agent] Generating Explanations")
        logger.info("="*60)
        
        if not use_gemini or not self.gemini_available:
            logger.info("Using template-based explanations (Gemini disabled)")
            return self._template_explanations(recommendations, workload_analysis)
        
        # Generate Gemini-powered explanations
        explained = []
        
        for rec in recommendations:
            # Check if there is valid evidence
            evidence = rec.get('evidence', {})
            if not evidence or not evidence.get('basis'):
                logger.warning(f"Skipping recommendation '{rec.get('title')}' - no valid evidence available")
                continue
                
            explanation = await self._generate_gemini_explanation(rec, workload_analysis)
            
            # Ensure the explanation has valid 'why' and 'how' keys
            if explanation and explanation.get('why') and len(explanation.get('how', [])) > 0:
                rec_copy = rec.copy()
                rec_copy['explanation'] = explanation
                explained.append(rec_copy)
                
                self.explanation_stats['explanations_generated'] += 1
                if explanation.get('source') == 'gemini':
                    self.explanation_stats['gemini_calls'] += 1
                else:
                    self.explanation_stats['fallback_used'] += 1
            else:
                logger.warning(f"Skipping recommendation '{rec.get('title')}' - failed to generate valid explanation")
        
        # Generate executive summary
        summary = await self._generate_executive_summary(explained, workload_analysis)
        
        logger.info(f"✓ Generated {len(explained)} explanations (filtered down from {len(recommendations)})")
        logger.info(f"  Gemini calls: {self.explanation_stats['gemini_calls']}")
        logger.info(f"  Fallback used: {self.explanation_stats['fallback_used']}")
        
        return {
            'explained_recommendations': explained,
            'executive_summary': summary,
            'stats': self.explanation_stats.copy()
        }
    
    async def _generate_gemini_explanation(self, rec: Dict, analysis: Dict) -> Dict:
        """Generate Gemini explanation for single recommendation"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            return self._template_explanation(rec)
        
        try:
            import google.generativeai as genai
            import json
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            opp_type = rec.get('type', '')
            
            # Build context for Gemini
            context = {
                'title': rec['title'],
                'category': rec['category'],
                'service': rec['service'],
                'carbon_reduction_pct': rec['carbon_reduction_pct'],
                'carbon_reduction_kg': rec['carbon_reduction_kg'],
                'cost_impact': rec['cost_impact'],
                'confidence': rec['confidence'],
                'reasoning': rec['reasoning'],
                'evidence': rec.get('evidence', {}),
                'root_cause': rec.get('root_cause', '')
            }
            
            prompt = f"""
You are a cloud sustainability advisor. Explain this carbon reduction recommendation in business-friendly language.
You MUST follow this exact JSON structure for your response (no prose, no markdown other than valid JSON):
{{
  "why": "<detailed plain-English causal explanation. Explain WHY less carbon is produced, detailing the grid-mix or resource mechanism using the actual intensity numbers below. Do not use generic buzzwords like 'improve efficiency' or 'optimize scheduling' without a specific mechanism attached.>",
  "how": [
    "1) <concrete numbered implementation step 1>",
    "2) <concrete numbered implementation step 2>",
    "3) <concrete numbered implementation step 3>"
  ]
}}

Recommendation: {context['title']}
Service: {context['service']}
Category: {context['category']}
Opportunity Type: {opp_type}
Carbon Reduction: {context['carbon_reduction_kg']:.2f}kg CO2 ({context['carbon_reduction_pct']:.1f}%)
Cost Impact: {context['cost_impact']}
Confidence: {context['confidence']}
Root Cause: {context['root_cause']}
Evidence Detail: {context['evidence']}

Requirements:
1. Ground the explanation in the provided Evidence Detail numbers (current region intensity vs target region intensity).
2. Detail the exact causal grid mechanism (e.g., coal/fossil fuels vs wind/solar/hydro/grid-mix).
3. Provide concrete numbered action steps under the "how" key.
4. Avoid any vague sustainability statements or buzzwords.
"""
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, model.generate_content, prompt)
            explanation_text = response.text.strip()
            
            # Clean JSON formatting if Gemini wrapped in codeblock
            if explanation_text.startswith("```json"):
                explanation_text = explanation_text[7:]
            if explanation_text.endswith("```"):
                explanation_text = explanation_text[:-3]
            explanation_text = explanation_text.strip()
            
            data = json.loads(explanation_text)
            
            if not data.get('why') or not data.get('how'):
                raise ValueError("JSON response from Gemini lacks 'why' or 'how' fields")
                
            return {
                'why': data.get('why'),
                'how': data.get('how'),
                'source': 'gemini',
                'confidence_note': f"Confidence: {rec['confidence']}"
            }
            
        except Exception as e:
            logger.warning(f"Gemini explanation failed: {e}. Using template fallback.")
            return self._template_explanation(rec)
    
    def _template_explanation(self, rec: Dict) -> Dict:
        """Generate template-based explanation with structured why and how"""
        opp_type = rec.get('type', '')
        service = rec.get('service', 'AWS Resource')
        evidence = rec.get('evidence', {})
        current_region = evidence.get('current_region', {})
        target_region = evidence.get('target_region', {})
        
        current_intensity = current_region.get('avg_intensity_gco2', 450.0)
        target_intensity = target_region.get('avg_intensity_gco2', 360.0)
        current_zone = current_region.get('zone', 'US')
        target_zone = target_region.get('zone', 'US')
        
        # Build specific default explanations based on opportunity type
        if opp_type == 'time_shift':
            details = rec.get('details', {})
            current_window = details.get('current_window', '14:00')
            suggested_window = details.get('suggested_window', '02:00')
            why = f"Grid carbon intensity at {current_window} is {current_intensity} gCO2/kWh due to peak grid load, whereas shifting execution to {suggested_window} runs during a lower grid demand window with average grid intensity of {target_intensity} gCO2/kWh."
            how = [
                f"1) Identify the scheduler or cron trigger controlling the {service} job.",
                f"2) Change the trigger timing from peak hours ({current_window}) to off-peak hours ({suggested_window}).",
                f"3) Confirm that downstream systems do not require the results before the new execution completes."
            ]
        elif opp_type == 'region_migration':
            details = rec.get('details', {})
            curr_reg = details.get('current_region', 'ap-south-1')
            sugg_reg = details.get('suggested_region', 'eu-north-1')
            why = f"Grid region {curr_reg} ({current_zone}) is coal-heavy with an intensity of {current_intensity} gCO2/kWh. Migrating to {sugg_reg} ({target_zone}) accesses a grid powered by wind, solar, and hydro which drops average intensity to {target_intensity} gCO2/kWh."
            how = [
                f"1) Enable replication/snapshots for resources in region {curr_reg}.",
                f"2) Spin up corresponding resources in target region {sugg_reg}.",
                f"3) Re-route application traffic to the new {sugg_reg} endpoints and verify latency parameters."
            ]
        elif opp_type == 'compute_optimization':
            why = f"Compute resource sizing scan detects underutilization for {service}. Sizing optimization scales resources down to align with active grid load profiles, reducing baseline grid draw from {current_intensity} gCO2/kWh equivalent to {target_intensity} gCO2/kWh equivalent."
            how = [
                f"1) Analyze CPU and memory utilization patterns for {service}.",
                f"2) Reconfigure Auto Scaling groups or resize instance families to Graviton-based instances.",
                f"3) Deploy instance changes during standard maintenance windows and monitor memory footprint."
            ]
        elif opp_type == 'data_processing_optimization':
            why = f"Repeated execution frequency of {service} jobs generates redundant container startup and resource overhead, causing elevated grid load."
            how = [
                f"1) Consolidate batch triggers into single scheduled executions.",
                f"2) Implement delta processing to scan modified data entries only, saving CPU time.",
                f"3) Configure task queues to buffer jobs until off-peak hours."
            ]
        else: # workload_smoothing or default
            why = f"Workload intensity spike analysis detects peak load demands. Smoothing baseline consumption reduces peak grid carbon intensity from {current_intensity} gCO2/kWh to {target_intensity} gCO2/kWh."
            how = [
                f"1) Distribute high-compute tasks across multiple scheduling intervals.",
                f"2) Throttle non-critical background routines during grid peak hours.",
                f"3) Monitor daily emission variance indicators to verify smoothing results."
            ]

        return {
            'why': why,
            'how': how,
            'source': 'template',
            'confidence_note': f"Confidence: {rec['confidence']}"
        }
    
    def _template_explanations(self, recommendations: List[Dict], analysis: Dict) -> Dict:
        """Generate all template-based explanations"""
        explained = []
        
        for rec in recommendations:
            # Check if there is valid evidence
            evidence = rec.get('evidence', {})
            if not evidence or not evidence.get('basis'):
                logger.warning(f"Skipping recommendation '{rec.get('title')}' - no valid evidence available")
                continue
                
            rec_copy = rec.copy()
            rec_copy['explanation'] = self._template_explanation(rec)
            explained.append(rec_copy)
            self.explanation_stats['explanations_generated'] += 1
            self.explanation_stats['fallback_used'] += 1
        
        summary = self._generate_template_summary(explained, analysis)
        
        return {
            'explained_recommendations': explained,
            'executive_summary': summary,
            'stats': self.explanation_stats.copy()
        }
    
    async def _generate_executive_summary(self, recommendations: List[Dict], analysis: Dict) -> str:
        """Generate executive summary"""
        return self._generate_template_summary(recommendations, analysis)
    
    def _generate_template_summary(self, recommendations: List[Dict], analysis: Dict) -> str:
        """Generate template-based summary"""
        if not recommendations:
            return "No optimization opportunities identified at this time."
        
        total_reduction = sum(r['carbon_reduction_kg'] for r in recommendations)
        high_confidence = sum(1 for r in recommendations if r['confidence'] == 'High')
        
        top_rec = recommendations[0]
        
        summary = f"""
CarbonIQ has identified {len(recommendations)} sustainability optimization opportunities across your AWS infrastructure.
Implementing these recommendations can reduce carbon emissions by up to {total_reduction:.2f}kg CO2.

High Confidence Opportunities: {high_confidence}

Top Recommendation: {top_rec['title']}
This opportunity alone can reduce emissions by {top_rec['carbon_reduction_kg']:.2f}kg CO2 ({top_rec['carbon_reduction_pct']:.1f}%) with a {top_rec['cost_impact'].lower()} cost impact.
        """.strip()
        
        return summary
    
    def get_explanation_stats(self) -> Dict:
        """Get explanation statistics"""
        return self.explanation_stats.copy()
