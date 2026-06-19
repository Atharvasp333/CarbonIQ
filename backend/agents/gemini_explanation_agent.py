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
            explanation = await self._generate_gemini_explanation(rec, workload_analysis)
            rec_copy = rec.copy()
            rec_copy['explanation'] = explanation
            explained.append(rec_copy)
            
            self.explanation_stats['explanations_generated'] += 1
            if explanation.get('source') == 'gemini':
                self.explanation_stats['gemini_calls'] += 1
            else:
                self.explanation_stats['fallback_used'] += 1
        
        # Generate executive summary
        summary = await self._generate_executive_summary(recommendations, workload_analysis)
        
        logger.info(f"✓ Generated {len(explained)} explanations")
        logger.info(f"  Gemini calls: {self.explanation_stats['gemini_calls']}")
        logger.info(f"  Fallback used: {self.explanation_stats['fallback_used']}")
        
        return {
            'explained_recommendations': explained,
            'executive_summary': summary,
            'stats': self.explanation_stats.copy()
        }
    
    async def _generate_gemini_explanation(self, rec: Dict, analysis: Dict) -> Dict:
        """Generate Gemini explanation for single recommendation"""
        if not self.gemini_available:
            return self._template_explanation(rec)
        
        try:
            # Build context for Gemini
            context = {
                'title': rec['title'],
                'category': rec['category'],
                'service': rec['service'],
                'carbon_reduction_pct': rec['carbon_reduction_pct'],
                'carbon_reduction_kg': rec['carbon_reduction_kg'],
                'cost_impact': rec['cost_impact'],
                'confidence': rec['confidence'],
                'reasoning': rec['reasoning']
            }
            
            prompt = f"""
You are a sustainability advisor. Explain this carbon reduction recommendation in business-friendly language.

Recommendation: {context['title']}
Service: {context['service']}
Category: {context['category']}
Carbon Reduction: {context['carbon_reduction_kg']:.2f}kg CO2 ({context['carbon_reduction_pct']:.1f}%)
Cost Impact: {context['cost_impact']}
Confidence: {context['confidence']}
Technical Reasoning: {context['reasoning']}

Provide a 2-3 sentence explanation that:
1. Explains WHY this matters for sustainability
2. Describes the BUSINESS BENEFIT
3. Mentions any TRADE-OFFS or constraints

Keep it concise and actionable. Do not recalculate any numbers.
"""
            
            # Call Gemini (would integrate with actual API)
            # For now, use template fallback
            return self._template_explanation(rec)
            
        except Exception as e:
            logger.warning(f"Gemini explanation failed: {e}")
            return self._template_explanation(rec)
    
    def _template_explanation(self, rec: Dict) -> Dict:
        """Generate template-based explanation"""
        templates = {
            'EC2': f"Optimizing {rec['service']} can reduce carbon emissions by {rec['carbon_reduction_kg']:.2f}kg CO2 ({rec['carbon_reduction_pct']:.1f}%). {rec['reasoning']}. This change has a {rec['cost_impact'].lower()} cost impact.",
            
            'Lambda': f"Adjusting Lambda configurations for {rec['service']} offers a {rec['carbon_reduction_kg']:.2f}kg CO2 reduction ({rec['carbon_reduction_pct']:.1f}%). {rec['reasoning']}. Cost impact is expected to be {rec['cost_impact'].lower()}.",
            
            'S3': f"Implementing lifecycle policies for {rec['service']} can save {rec['carbon_reduction_kg']:.2f}kg CO2 ({rec['carbon_reduction_pct']:.1f}%) by moving data to more efficient storage tiers. {rec['reasoning']}.",
            
            'SageMaker': f"Scheduling {rec['service']} training jobs during low-carbon hours can reduce emissions by {rec['carbon_reduction_kg']:.2f}kg CO2 ({rec['carbon_reduction_pct']:.1f}%). {rec['reasoning']}.",
            
            'Region': f"Migrating workloads to lower-carbon regions can achieve {rec['carbon_reduction_kg']:.2f}kg CO2 savings ({rec['carbon_reduction_pct']:.1f}%). {rec['reasoning']}.",
            
            'Time': f"Shifting workloads to low-carbon time windows can reduce emissions by {rec['carbon_reduction_kg']:.2f}kg CO2 ({rec['carbon_reduction_pct']:.1f}%). {rec['reasoning']}."
        }
        
        category = rec['category']
        explanation_text = templates.get(category, f"{rec['title']} can reduce emissions by {rec['carbon_reduction_kg']:.2f}kg CO2. {rec['reasoning']}.")
        
        return {
            'text': explanation_text,
            'source': 'template',
            'confidence_note': f"Confidence: {rec['confidence']}"
        }
    
    def _template_explanations(self, recommendations: List[Dict], analysis: Dict) -> Dict:
        """Generate all template-based explanations"""
        explained = []
        
        for rec in recommendations:
            rec_copy = rec.copy()
            rec_copy['explanation'] = self._template_explanation(rec)
            explained.append(rec_copy)
            self.explanation_stats['explanations_generated'] += 1
            self.explanation_stats['fallback_used'] += 1
        
        summary = self._generate_template_summary(recommendations, analysis)
        
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

Total Potential Carbon Reduction: {total_reduction:.2f}kg CO2
High Confidence Opportunities: {high_confidence}

Top Recommendation: {top_rec['title']}
This opportunity alone can reduce emissions by {top_rec['carbon_reduction_kg']:.2f}kg CO2 ({top_rec['carbon_reduction_pct']:.1f}%) with a {top_rec['cost_impact'].lower()} cost impact.

Focus areas include: {', '.join(set(r['category'] for r in recommendations[:3]))}.
        """.strip()
        
        return summary
    
    def get_explanation_stats(self) -> Dict:
        """Get explanation statistics"""
        return self.explanation_stats.copy()
