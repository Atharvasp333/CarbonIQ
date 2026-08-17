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
    
    # Static physical feasibility lookup table for region migrations
    MIGRATION_FEASIBILITY = {
        'EC2': {
            'rating': 'High',
            'explanation': 'Stateless compute instances allow relatively straightforward cross-region migration.'
        },
        'Lambda': {
            'rating': 'High',
            'explanation': 'Stateless serverless compute functions allow direct cross-region deployment.'
        },
        'RDS': {
            'rating': 'Medium',
            'explanation': 'Stateful relational databases require a cross-region read replica and replication strategy.'
        },
        'S3': {
            'rating': 'Medium',
            'explanation': 'Stateful object storage, migrating large volumes requires cross-region replication setup.'
        },
        'DynamoDB': {
            'rating': 'Low',
            'explanation': 'Stateful NoSQL database, cross-region migration requires DynamoDB Global Tables configuration.'
        },
        'API Gateway': {
            'rating': 'Low',
            'explanation': 'Infrastructure configuration routing, requires API endpoint adjustments and custom domain transition steps.'
        }
    }

    # Confidence scoring rules
    CONFIDENCE_LEVELS = {
        'High': {'score': 3, 'label': 'High'},
        'Medium': {'score': 2, 'label': 'Medium'},
        'Low': {'score': 1, 'label': 'Low'}
    }

    def _get_migration_feasibility(self, service: str) -> Dict:
        """Get migration feasibility rating and explanation for a service"""
        service_upper = service.upper()
        for key, val in self.MIGRATION_FEASIBILITY.items():
            if key in service_upper:
                return val
        # Default fallback
        return {
            'rating': 'High',
            'explanation': 'General service. Standard migration procedures apply.'
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
            
            # Add validation metadata
            opp['confidence'] = validation['confidence']
            opp['reasoning'] = validation['reasoning']
            opp['constraints_applied'] = validation['constraints']
            opp['constraint_status'] = validation['constraint_status']
            opp['constraint_reason'] = validation['constraint_reason']
            opp['effort'] = validation['effort']
            opp['implementation_complexity'] = validation['effort'] # Sync field names
            
            validated.append(opp)
            
            # Update stats
            if validation['constraint_status'] == 'rejected':
                self.validation_stats['rejected'] += 1
            elif validation['confidence'] == 'High':
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
        service = opp.get('service', '')
        
        # Default status/reason/effort
        constraint_status = 'compatible'
        constraint_reason = 'Compatible with organization constraints'
        effort = 'Medium'
        if opp_type in ['compute_optimization', 'ec2_right_sizing']:
            effort = 'Low'  # Resizing EC2 is low effort
        
        primary_user_region = profile.get('primary_user_region', 'Global')
        latency = profile.get('latency_sensitivity', 'Medium')
        migration = profile.get('migration_flexibility', 'Some Workloads')
        workload = profile.get('workload_type', 'Mixed')
        priority = profile.get('optimization_priority', 'Balance Both')
        
        # 1. LATENCY SENSITIVITY + PRIMARY USER REGION
        # Latency band lookup
        LATENCY_BAND = {
            'India': {
                'ap-south-1': 'compatible',
                'ap-south-2': 'compatible',
                'ap-southeast-1': 'flagged',   # Singapore - medium latency
                'ap-southeast-2': 'flagged',   # Sydney - high latency
                'eu-west-1': 'flagged',        # Ireland - medium/high latency
                'us-west-2': 'rejected',       # Oregon - high latency
                'eu-north-1': 'flagged',       # Sweden - medium/high latency
                'ca-central-1': 'rejected',    # Montreal - high latency
            },
            'North America': {
                'us-east-1': 'compatible',
                'us-east-2': 'compatible',
                'us-west-1': 'compatible',
                'us-west-2': 'compatible',
                'ca-central-1': 'compatible',
                'eu-north-1': 'rejected',
                'eu-west-1': 'flagged',
                'ap-south-1': 'rejected',
            },
            'Europe': {
                'eu-west-1': 'compatible',
                'eu-west-2': 'compatible',
                'eu-central-1': 'compatible',
                'eu-north-1': 'compatible',
                'us-east-1': 'flagged',
                'us-west-2': 'rejected',
                'ap-south-1': 'rejected',
            },
            'Asia Pacific': {
                'ap-southeast-1': 'compatible',
                'ap-southeast-2': 'compatible',
                'ap-northeast-1': 'compatible',
                'ap-northeast-2': 'compatible',
                'ap-south-1': 'flagged',
                'us-west-2': 'rejected',
                'eu-north-1': 'rejected',
            },
            'Global': {}
        }

        if opp_type == 'region_migration':
            suggested_region = opp.get('details', {}).get('suggested_region', '')
            
            if latency == 'High':
                status = 'compatible'
                if primary_user_region in LATENCY_BAND:
                    status = LATENCY_BAND[primary_user_region].get(suggested_region, 'compatible')
                
                if status == 'flagged':
                    constraint_status = 'flagged'
                    constraint_reason = f"⚠️ May not suit your latency requirements (High Latency Sensitivity in {primary_user_region} vs {suggested_region})"
                    confidence_score -= 1
                    reasoning_parts.append("High latency sensitivity reduces confidence for distant regions")
                    constraints_applied.append("Latency: High")
                elif status == 'rejected':
                    constraint_status = 'rejected'
                    constraint_reason = f"❌ Rejected: Region {suggested_region} exceeds latency threshold for primary region {primary_user_region}"
                    confidence_score -= 2
                    reasoning_parts.append("Suggested region exceeds latency threshold")
                    constraints_applied.append("Latency: High")
            elif latency == 'Medium':
                # Treat rejected as flagged
                status = 'compatible'
                if primary_user_region in LATENCY_BAND:
                    status = LATENCY_BAND[primary_user_region].get(suggested_region, 'compatible')
                if status == 'rejected':
                    constraint_status = 'flagged'
                    constraint_reason = f"⚠️ Warning: Region {suggested_region} may cause latency impact for primary region {primary_user_region}"
                    confidence_score -= 1
                    reasoning_parts.append("Suggested region may have latency impact")
                    constraints_applied.append("Latency: Medium")

        # 2. MIGRATION FLEXIBILITY
        if migration == 'No':
            if opp_type == 'region_migration':
                constraint_status = 'rejected'
                constraint_reason = "❌ Rejected: Region migration disabled by organization flexibility settings"
                confidence_score = 0
                reasoning_parts.append("Region migration disabled by flexibility constraints")
                constraints_applied.append("Migration: No")
            elif opp_type in ['ec2_right_sizing', 'ec2_auto_scaling']:
                confidence_score -= 1
                reasoning_parts.append("No migration flexibility limits infrastructure changes")
                constraints_applied.append("Migration: No")
        elif migration == 'Some Workloads':
            if opp_type == 'region_migration' and constraint_status == 'compatible':
                constraint_status = 'flagged'
                constraint_reason = "⚠️ Warning: Region migration requires workload suitability check under limited flexibility"
                confidence_score -= 1
                reasoning_parts.append("Limited migration flexibility for region changes")
                constraints_applied.append("Migration: Some Workloads")

        # 3. WORKLOAD TYPE & STATEFUL SERVICES
        is_stateful = (workload in ['Database', 'Stateful']) or (service in ['RDS', 'S3', 'Amazon RDS', 'Amazon Simple Storage Service', 'Database', 'Storage']) or ('db.' in str(opp.get('details', {}).get('instance_type', '')).lower())
        
        if is_stateful:
            if opp_type == 'region_migration':
                effort = 'High'
                if constraint_status == 'compatible':
                    constraint_status = 'flagged'
                    constraint_reason = "⚠️ High effort: Stateful database migration requires active-active sync or replication"
                reasoning_parts.append("Stateful workloads require high effort for migration")
                constraints_applied.append("Workload: Stateful/DB")
            else:
                effort = 'Medium'
                reasoning_parts.append("Stateful workloads require extra verification")
                constraints_applied.append("Workload: Stateful/DB")
        
        if workload == 'Production':
            confidence_score -= 1
            reasoning_parts.append("Production workload requires careful testing before changes")
            constraints_applied.append("Workload: Production")

        # 4. OPTIMIZATION PRIORITY
        if priority == 'Reduce Carbon':
            if opp.get('expected_reduction_pct', 0) > 20:
                confidence_score += 1
                reasoning_parts.append("High carbon reduction aligns with optimization priority")
                constraints_applied.append("Priority: Reduce Carbon")
        elif priority == 'Reduce Cost':
            if opp.get('cost_impact') == 'Positive':
                confidence_score += 1
                reasoning_parts.append("Cost reduction aligns with optimization priority")
                constraints_applied.append("Priority: Reduce Cost")
            elif opp.get('cost_impact') == 'Negative':
                confidence_score -= 1
                reasoning_parts.append("Cost increase conflicts with optimization priority")
                constraints_applied.append("Priority: Reduce Cost")

        # 5. PHYSICAL FEASIBILITY VALIDATION (Region Migration Only)
        if opp_type == 'region_migration':
            feasibility = self._get_migration_feasibility(service)
            rating = feasibility['rating']
            explanation = feasibility['explanation']
            
            if rating == 'Low':
                if constraint_status != 'rejected':
                    constraint_status = 'flagged'
                    constraint_reason = f"⚠️ Low Feasibility: {explanation}"
                confidence_score -= 2
                reasoning_parts.append(f"Low physical feasibility: {explanation}")
                constraints_applied.append(f"Feasibility: Low ({service})")
            elif rating == 'Medium':
                if constraint_status == 'compatible':
                    constraint_status = 'flagged'
                    constraint_reason = f"⚠️ Medium Feasibility: {explanation}"
                confidence_score -= 1
                reasoning_parts.append(f"Medium physical feasibility: {explanation}")
                constraints_applied.append(f"Feasibility: Medium ({service})")

        # Convert score to confidence level
        if constraint_status == 'rejected':
            confidence = 'Low'
        elif confidence_score >= 3:
            confidence = 'High'
        elif confidence_score >= 2:
            confidence = 'Medium'
        else:
            confidence = 'Low'

        if not reasoning_parts:
            reasoning_parts.append("No constraints conflict with this opportunity")

        return {
            'confidence': confidence,
            'reasoning': '. '.join(reasoning_parts),
            'constraints': constraints_applied,
            'constraint_status': constraint_status,
            'constraint_reason': constraint_reason,
            'effort': effort
        }
    
    def _default_validation(self, opportunities: List[Dict]) -> List[Dict]:
        """Default validation when no profile is provided (still checks service physical feasibility)"""
        for opp in opportunities:
            opp_type = opp.get('type', '')
            service = opp.get('service', 'AWS Resource')
            
            # Default values
            opp['confidence'] = 'Medium'
            opp['reasoning'] = 'No organization profile configured - default validation applied'
            opp['constraints_applied'] = []
            opp['constraint_status'] = 'compatible'
            opp['constraint_reason'] = ''
            opp['effort'] = 'Medium'
            opp['implementation_complexity'] = 'Medium'
            
            # Apply physical feasibility validation to region migrations
            if opp_type == 'region_migration':
                feasibility = self._get_migration_feasibility(service)
                rating = feasibility['rating']
                explanation = feasibility['explanation']
                
                if rating == 'Low':
                    opp['constraint_status'] = 'flagged'
                    opp['constraint_reason'] = f"⚠️ Low Feasibility: {explanation}"
                    opp['confidence'] = 'Low'
                    opp['reasoning'] = f"Low physical feasibility: {explanation}"
                    opp['constraints_applied'].append(f"Feasibility: Low ({service})")
                    self.validation_stats['low_confidence'] += 1
                elif rating == 'Medium':
                    opp['constraint_status'] = 'flagged'
                    opp['constraint_reason'] = f"⚠️ Medium Feasibility: {explanation}"
                    opp['confidence'] = 'Medium'
                    opp['reasoning'] = f"Medium physical feasibility: {explanation}"
                    opp['constraints_applied'].append(f"Feasibility: Medium ({service})")
                    self.validation_stats['medium_confidence'] += 1
                else:
                    self.validation_stats['medium_confidence'] += 1
            else:
                self.validation_stats['medium_confidence'] += 1
            
        self.validation_stats['opportunities_validated'] = len(opportunities)
        return opportunities
    
    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        return self.validation_stats.copy()
