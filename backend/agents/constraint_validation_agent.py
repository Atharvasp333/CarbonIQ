"""
CONSTRAINT VALIDATION AGENT
Validates optimization opportunities against organization constraints

Validates feasibility based on:
- Latency sensitivity
- Migration flexibility
- Primary user region
- Workload type
- Optimization priority

PURE DETERMINISTIC VALIDATION - NO AI/LLM
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ConstraintValidationAgent:
    """
    Validates optimization opportunities against organization profile constraints
    """
    
    # Confidence scoring rules
    CONFIDENCE_LEVELS = {
        'High': {'score': 3, 'label': 'High'},
        'Medium': {'score': 2, 'label': 'Medium'},
        'Low': {'score': 1, 'label': 'Low'}
    }
    
    def __init__(self):
        self.validation_stats = {
            'opportunities_validated': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'rejected': 0
        }
    
    def validate_opportunities(
        self,
        opportunities: List[Dict],
        org_profile: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Validate and score optimization opportunities
        
        Args:
            opportunities: List of opportunities from SmartOptimizationAgent
            org_profile: Organization profile with constraints (optional)
        
        Returns:
            List of validated opportunities with confidence scores and reasoning
        """
        logger.info("="*60)
        logger.info("[Constraint Validation Agent] Validating Opportunities")
        logger.info("="*60)
        
        if not org_profile:
            logger.info("No organization profile provided - using default validation")
            return self._default_validation(opportunities)
        
        validated = []
        
        for opp in opportunities:
            validation = self._validate_opportunity(opp, org_profile)
            
            # Skip rejected opportunities
            if validation['confidence'] == 'Rejected':
                self.validation_stats['rejected'] += 1
                continue
            
            # Add validation metadata
            opp['confidence'] = validation['confidence']
            opp['reasoning'] = validation['reasoning']
            opp['constraints_applied'] = validation['constraints']
            
            validated.append(opp)
            
            # Update stats
            if validation['confidence'] == 'High':
                self.validation_stats['high_confidence'] += 1
            elif validation['confidence'] == 'Medium':
                self.validation_stats['medium_confidence'] += 1
            else:
                self.validation_stats['low_confidence'] += 1
        
        self.validation_stats['opportunities_validated'] = len(validated)
        
        logger.info(f"✓ Validated {len(validated)} opportunities")
        logger.info(f"  High Confidence: {self.validation_stats['high_confidence']}")
        logger.info(f"  Medium Confidence: {self.validation_stats['medium_confidence']}")
        logger.info(f"  Low Confidence: {self.validation_stats['low_confidence']}")
        logger.info(f"  Rejected: {self.validation_stats['rejected']}")
        
        return validated
    
    def _validate_opportunity(self, opp: Dict, profile: Dict) -> Dict:
        """Validate single opportunity against profile"""
        confidence_score = 3  # Start with High
        reasoning_parts = []
        constraints_applied = []
        
        opp_type = opp.get('type', '')
        category = opp.get('category', '')
        
        # CONSTRAINT 1: Latency Sensitivity
        latency = profile.get('latency_sensitivity', 'Medium')
        
        if latency == 'High':
            if opp_type == 'region_migration':
                confidence_score -= 2
                reasoning_parts.append("High latency sensitivity reduces confidence for region migration")
                constraints_applied.append("Latency: High")
            elif opp_type == 'time_shift':
                confidence_score -= 1
                reasoning_parts.append("High latency sensitivity may limit time-shift flexibility")
                constraints_applied.append("Latency: High")
        
        # CONSTRAINT 2: Migration Flexibility
        migration = profile.get('migration_flexibility', 'Some Workloads')
        
        if migration == 'No':
            if opp_type == 'region_migration':
                return {
                    'confidence': 'Rejected',
                    'reasoning': 'Region migration not allowed due to migration flexibility constraints',
                    'constraints': ['Migration: No']
                }
            elif opp_type in ['ec2_right_sizing', 'ec2_auto_scaling']:
                confidence_score -= 1
                reasoning_parts.append("No migration flexibility limits infrastructure changes")
                constraints_applied.append("Migration: No")
        elif migration == 'Some Workloads':
            if opp_type == 'region_migration':
                confidence_score -= 1
                reasoning_parts.append("Limited migration flexibility for region changes")
                constraints_applied.append("Migration: Some Workloads")
        
        # CONSTRAINT 3: Primary User Region
        primary_region = profile.get('primary_user_region', 'Global')
        
        if opp_type == 'region_migration':
            current_region = opp.get('details', {}).get('current_region', '')
            suggested_region = opp.get('details', {}).get('suggested_region', '')
            
            # Map AWS regions to geographic areas
            region_mapping = {
                'India': ['ap-south-1', 'ap-south-2'],
                'North America': ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                'Europe': ['eu-west-1', 'eu-west-2', 'eu-central-1', 'eu-north-1'],
                'Asia Pacific': ['ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2']
            }
            
            primary_regions = region_mapping.get(primary_region, [])
            
            # If suggested region is far from primary user region, reduce confidence
            if primary_regions and suggested_region not in primary_regions:
                confidence_score -= 1
                reasoning_parts.append(f"Suggested region outside primary user region ({primary_region})")
                constraints_applied.append(f"Primary Region: {primary_region}")
        
        # CONSTRAINT 4: Workload Type
        workload = profile.get('workload_type', 'Mixed')
        
        if workload == 'Production':
            if opp_type in ['ec2_right_sizing', 'region_migration']:
                confidence_score -= 1
                reasoning_parts.append("Production workload requires careful testing before changes")
                constraints_applied.append("Workload: Production")
        elif workload == 'Machine Learning':
            if opp_type == 'time_shift' and category == 'SageMaker':
                confidence_score += 1  # Time-shifting ML training is ideal
                reasoning_parts.append("ML training workloads are ideal for time-shifting")
                constraints_applied.append("Workload: Machine Learning")
        
        # CONSTRAINT 5: Optimization Priority
        priority = profile.get('optimization_priority', 'Balance Both')
        
        if priority == 'Reduce Carbon':
            # Favor high carbon reduction even with cost impact
            if opp.get('carbon_reduction_pct', 0) > 20:
                confidence_score += 1
                reasoning_parts.append("High carbon reduction aligns with optimization priority")
                constraints_applied.append("Priority: Reduce Carbon")
        elif priority == 'Reduce Cost':
            # Favor cost-positive changes
            if opp.get('cost_impact') == 'Positive':
                confidence_score += 1
                reasoning_parts.append("Cost reduction aligns with optimization priority")
                constraints_applied.append("Priority: Reduce Cost")
            elif opp.get('cost_impact') == 'Negative':
                confidence_score -= 1
                reasoning_parts.append("Cost increase conflicts with optimization priority")
                constraints_applied.append("Priority: Reduce Cost")
        
        # Convert score to confidence level
        if confidence_score >= 3:
            confidence = 'High'
        elif confidence_score >= 2:
            confidence = 'Medium'
        elif confidence_score >= 1:
            confidence = 'Low'
        else:
            confidence = 'Rejected'
        
        # Build reasoning string
        if not reasoning_parts:
            reasoning_parts.append("No constraints conflict with this opportunity")
        
        return {
            'confidence': confidence,
            'reasoning': '. '.join(reasoning_parts),
            'constraints': constraints_applied
        }
    
    def _default_validation(self, opportunities: List[Dict]) -> List[Dict]:
        """Default validation when no profile is provided"""
        for opp in opportunities:
            # Assign medium confidence by default
            opp['confidence'] = 'Medium'
            opp['reasoning'] = 'No organization profile configured - default validation applied'
            opp['constraints_applied'] = []
            
            self.validation_stats['medium_confidence'] += 1
        
        self.validation_stats['opportunities_validated'] = len(opportunities)
        return opportunities
    
    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        return self.validation_stats.copy()
