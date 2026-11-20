"""
AI RECOMMENDATION AGENT
Uses Gemini to generate explainable recommendations from structured evidence

CRITICAL RULES FOR GEMINI:
- Gemini does NOT calculate metrics
- Gemini does NOT discover opportunities
- Gemini does NOT invent facts
- Gemini ONLY explains provided evidence
- Gemini ONLY uses supplied data
"""
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class AIRecommendationAgent:
    """
    Converts evidence-based opportunities into explainable recommendations using AI
    """
    
    def __init__(self):
        self.recommendations_generated = 0
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_available = bool(gemini_key and gemini_key != "your_gemini_api_key_here")
        if self.gemini_available:
            logger.info("Gemini API key configured for recommendation explanations")
        else:
            logger.info("Gemini API key not configured, using deterministic template explanations")
    
    async def generate_recommendations(
        self,
        opportunities: List[Dict],
        org_profile: Optional[Dict] = None,
        use_ai: bool = True
    ) -> List[Dict]:
        """
        Generate explainable recommendations from opportunities
        
        Args:
            opportunities: Opportunities from OptimizationDiscoveryAgent (with validation)
            org_profile: Organization profile for context
            use_ai: Whether to use Gemini AI (default: True)
        
        Returns:
            List of explainable recommendations
        """
        logger.info("="*60)
        logger.info("[AI Recommendation Agent] Generating Explainable Recommendations")
        logger.info("="*60)
        
        recommendations = []
        
        for opp in opportunities:
            if use_ai and self.gemini_available:
                rec = await self._generate_ai_recommendation(opp, org_profile)
            else:
                rec = self._generate_template_recommendation(opp, org_profile)
            
            recommendations.append(rec)
            self.recommendations_generated += 1
        
        logger.info(f"✓ Generated {len(recommendations)} explainable recommendations")
        
        return recommendations
    
    async def _generate_ai_recommendation(self, opportunity: Dict, org_profile: Optional[Dict]) -> Dict:
        """Generate AI-powered recommendation using Gemini"""
        
        # Build prompt with strict constraints
        prompt = self._build_gemini_prompt(opportunity, org_profile)
        
        try:
            # Call Gemini API
            import google.generativeai as genai
            
            api_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Parse and strictly validate Gemini response against deterministic numbers
            raw_explanation = response.text
            explanation = self._validate_and_sanitize_ai_explanation(raw_explanation, opportunity)
            
            # Build recommendation with AI explanation
            recommendation = {
                **opportunity,  # Include all opportunity data
                'explanation': explanation,
                'explanation_source': 'gemini',
                'formatted': True,
                'reasoning': opportunity.get('recommended_action', opportunity.get('recommendation', '')) or opportunity.get('observation', ''),
                'recommendation': opportunity.get('recommended_action', opportunity.get('recommendation', '')),
                'carbon_reduction_kg': opportunity.get('expected_reduction_kg'),
                'carbon_reduction_pct': opportunity.get('expected_reduction_pct'),
                'potential_savings_kg': opportunity.get('expected_reduction_kg'),
                'potential_reduction_pct': opportunity.get('expected_reduction_pct'),
                'constraints': opportunity.get('constraints', opportunity.get('constraints_applied', [])),
                'details': opportunity.get('details', opportunity.get('evidence', {}))
            }
            
            return recommendation
            
        except Exception as e:
            logger.warning(f"Gemini generation failed: {e}, falling back to template")
            return self._generate_template_recommendation(opportunity, org_profile)
    
    def _build_gemini_prompt(self, opportunity: Dict, org_profile: Optional[Dict]) -> str:
        """Build a strict prompt for Gemini"""
        
        evidence_str = "\n".join([f"- {k}: {v}" for k, v in opportunity['evidence'].items()])
        
        profile_context = ""
        if org_profile:
            profile_context = f"""
Organization Context:
- Primary Region: {org_profile.get('primary_user_region', 'Unknown')}
- Workload Type: {org_profile.get('workload_type', 'Unknown')}
- Latency Sensitivity: {org_profile.get('latency_sensitivity', 'Unknown')}
- Migration Flexibility: {org_profile.get('migration_flexibility', 'Unknown')}
- Optimization Priority: {org_profile.get('optimization_priority', 'Unknown')}
"""
        
        prompt = f"""You are a cloud sustainability architect. Generate a clear, actionable recommendation explanation.

CRITICAL RULES:
- Use ONLY the evidence provided below
- Do NOT invent metrics, facts, or numbers
- Do NOT calculate or estimate values not provided
- Do NOT mention services not in the evidence
- Base your explanation ONLY on supplied data

Evidence Provided:
Service: {opportunity['service']}
Observation: {opportunity['observation']}
Root Cause: {opportunity['root_cause']}

Evidence Data:
{evidence_str}

Expected Impact:
- Reduction: {opportunity['expected_reduction_pct']}% ({opportunity['expected_reduction_kg']} kg CO2)
- Cost Impact: {opportunity['cost_impact']}
- Confidence: {opportunity.get('confidence', 'Medium')}

{profile_context}

Generate a recommendation in this EXACT format:

**Observation:**
[Restate the observation from evidence]

**Evidence:**
[List the key evidence points]

**Root Cause:**
[Explain why this is happening based on evidence]

**Recommendation:**
[Specific, actionable recommendation]

**Expected Impact:**
[Quantified impact from provided metrics]

**Implementation Notes:**
[Practical steps to implement, considering org context if provided]

Keep it concise, factual, and actionable. Use only the evidence provided.
"""
        
        return prompt
    
    def _generate_template_recommendation(self, opportunity: Dict, org_profile: Optional[Dict]) -> Dict:
        """Generate template-based recommendation (fallback)"""
        
        # Build explanation sections
        observation = f"**Observation:**\n{opportunity['observation']}"
        
        evidence_points = []
        for key, value in opportunity['evidence'].items():
            if key != 'data_source':
                # Format key nicely
                formatted_key = key.replace('_', ' ').title()
                evidence_points.append(f"- {formatted_key}: {value}")
        
        evidence = f"**Evidence:**\n" + "\n".join(evidence_points)
        
        root_cause = f"**Root Cause:**\n{opportunity['root_cause']}"
        
        # Generate recommendation text based on category
        rec_text = self._get_recommendation_text(opportunity)
        recommendation = f"**Recommendation:**\n{rec_text}"
        
        red_kg = opportunity.get('expected_reduction_kg')
        red_pct = opportunity.get('expected_reduction_pct')
        if red_kg is not None and red_kg > 0:
            carbon_red_text = f"{red_kg:.4f} kg CO2 ({red_pct:.1f}%)"
        else:
            carbon_red_text = "Not calculated (Qualitative architectural guidance)"
        
        impact = (
            f"**Expected Impact:**\n"
            f"- Carbon Reduction: {carbon_red_text}\n"
            f"- Cost Impact: {opportunity['cost_impact']}\n"
            f"- Calculation Basis: {opportunity.get('calculation_basis', 'Empirical operational telemetry')}\n"
            f"- Data Provenance: {opportunity.get('data_provenance', 'AWS CUR Telemetry')}\n"
            f"- Confidence: {opportunity.get('confidence', 'Medium')}"
        )
        
        # Generate implementation notes
        impl_notes = self._get_implementation_notes(opportunity, org_profile)
        implementation = f"**Implementation Notes:**\n{impl_notes}"
        
        # Combine all sections
        full_explanation = f"{observation}\n\n{evidence}\n\n{root_cause}\n\n{recommendation}\n\n{impact}\n\n{implementation}"
        
        return {
            **opportunity,
            'explanation': full_explanation,
            'explanation_source': 'template',
            'formatted': True,
            'reasoning': rec_text,
            'recommendation': opportunity.get('recommended_action', rec_text),
            'implementation_notes': impl_notes,
            'carbon_reduction_kg': red_kg,
            'carbon_reduction_pct': red_pct,
            'potential_savings_kg': red_kg,
            'potential_reduction_pct': red_pct,
            'constraints': opportunity.get('constraints', opportunity.get('constraints_applied', [])),
            'details': opportunity.get('details', opportunity.get('evidence', {}))
        }

    def _validate_and_sanitize_ai_explanation(self, explanation: str, opportunity: Dict) -> str:
        """
        Validate and sanitize Gemini-generated explanations against deterministic calculation outputs.
        Ensures AI cannot introduce unsupported numerical claims.
        """
        red_kg = opportunity.get('expected_reduction_kg')
        red_pct = opportunity.get('expected_reduction_pct')
        basis = opportunity.get('calculation_basis', 'Empirical operational baseline')
        provenance = opportunity.get('data_provenance', 'AWS CUR Telemetry')
        
        if red_kg is not None and red_kg > 0:
            carbon_str = f"- Carbon Reduction: {red_kg:.4f} kg CO2 ({red_pct:.1f}%)\n"
        else:
            carbon_str = "- Carbon Reduction: Not calculated (Qualitative architectural guidance)\n"
            
        impact_str = (
            f"{carbon_str}"
            f"- Cost Impact: {opportunity.get('cost_impact', 'Neutral')}\n"
            f"- Calculation Basis: {basis}\n"
            f"- Data Provenance: {provenance}\n"
            f"- Confidence: {opportunity.get('confidence', 'Medium')}"
        )
        
        # Enforce deterministic impact section in explanation
        if "**Expected Impact:**" in explanation:
            parts = explanation.split("**Expected Impact:**")
            prefix = parts[0]
            rest = parts[1]
            if "\n\n**" in rest:
                suffix = "\n\n**" + rest.split("\n\n**", 1)[1]
            else:
                suffix = ""
            return f"{prefix}**Expected Impact:**\n{impact_str}{suffix}"
        
        return f"{explanation.strip()}\n\n**Expected Impact (Deterministically Verified):**\n{impact_str}"
    
    def _get_recommendation_text(self, opportunity: Dict) -> str:
        """Generate recommendation text based on opportunity type"""
        
        if opportunity['type'] == 'time_shift':
            return f"Schedule {opportunity['service']} workloads to execute during the low-carbon window ({opportunity['evidence']['suggested_window']}) instead of current high-carbon periods ({opportunity['evidence']['current_window']}). This timing shift will reduce emissions without affecting functionality."
        
        elif opportunity['type'] == 'region_migration':
            return f"Evaluate migrating non-latency-sensitive workloads from {opportunity['evidence']['current_region']} to {opportunity['evidence']['suggested_region']}, which has significantly lower carbon intensity. Prioritize services that don't require regional proximity to users."
        
        elif opportunity['type'] == 'data_processing_optimization':
            return f"Optimize {opportunity['service']} job scheduling by consolidating runs, removing unnecessary executions, and timing jobs during low-carbon periods. Review job dependencies to identify scheduling flexibility."
        
        elif opportunity['type'] == 'compute_optimization':
            return f"Analyze {opportunity['service']} instance utilization patterns to identify right-sizing opportunities. Consider implementing auto-scaling to match actual demand and reduce idle capacity."
        
        elif opportunity['type'] == 'storage_optimization':
            return f"Implement lifecycle policies for {opportunity['service']} to automatically transition infrequently accessed data to lower-tier storage classes. Review object age and access patterns to optimize storage allocation."
        
        elif opportunity['type'] == 'cost_efficiency':
            return f"Review {opportunity['service']} configuration and usage patterns to improve carbon efficiency per dollar spent. Consider workload optimization, resource right-sizing, or alternative service configurations."
        
        else:
            return f"Optimize {opportunity['service']} based on the evidence and root cause identified above."
    
    def _get_implementation_notes(self, opportunity: Dict, org_profile: Optional[Dict]) -> str:
        """Generate implementation notes with org profile context"""
        
        notes = []
        
        # Add implementation steps based on opportunity type
        if opportunity['type'] == 'time_shift':
            notes.append("1. Identify workloads that are not time-critical")
            notes.append("2. Update job schedules to target low-carbon windows")
            notes.append("3. Monitor execution success and adjust if needed")
            
            if org_profile and org_profile.get('workload_type') == 'Production':
                notes.append("⚠️ Test scheduling changes in non-production first")
        
        elif opportunity['type'] == 'region_migration':
            notes.append("1. Assess latency requirements for affected services")
            notes.append("2. Plan phased migration starting with dev/test workloads")
            notes.append("3. Validate compliance and data residency requirements")
            
            if org_profile:
                if org_profile.get('latency_sensitivity') == 'High':
                    notes.append("⚠️ High latency sensitivity - migration may not be suitable")
                if org_profile.get('migration_flexibility') == 'No':
                    notes.append("⚠️ Migration not feasible per organizational constraints")
        
        elif opportunity['type'] == 'compute_optimization':
            notes.append("1. Enable AWS Compute Optimizer or similar tools")
            notes.append("2. Review recommendations for instance right-sizing")
            notes.append("3. Implement changes during maintenance windows")
        
        elif opportunity['type'] == 'storage_optimization':
            notes.append("1. Analyze S3 storage analytics to identify access patterns")
            notes.append("2. Create lifecycle rules for automatic tiering")
            notes.append("3. Monitor cost and performance impact")
        
        else:
            notes.append("1. Review evidence and validate root cause")
            notes.append("2. Plan implementation with stakeholders")
            notes.append("3. Implement changes incrementally")
        
        # Add org-specific notes
        if org_profile:
            priority = org_profile.get('optimization_priority')
            if priority == 'Reduce Carbon' and opportunity['cost_impact'] == 'Negative':
                notes.append("💡 Carbon reduction priority justifies potential cost increase")
            elif priority == 'Reduce Cost' and opportunity['cost_impact'] == 'Positive':
                notes.append("💡 Aligns with cost reduction priority")
        
        return "\n".join(notes)
    
    def get_stats(self) -> Dict:
        """Get recommendation statistics"""
        return {
            'recommendations_generated': self.recommendations_generated,
            'gemini_available': self.gemini_available
        }
