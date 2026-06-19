"""
SMART OPTIMIZATION AGENT
Generates actionable optimization opportunities based on workload analysis

Generates service-specific recommendations for:
- EC2: Right-sizing, Auto Scaling, Spot Instances
- Lambda: Memory optimization, invocation optimization
- S3: Lifecycle policies, Glacier migration
- SageMaker: Training schedule optimization
- Region optimization
- Time-based optimization

PURE DETERMINISTIC LOGIC - NO AI/LLM
"""
import logging
from typing import Dict, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class SmartOptimizationAgent:
    """
    Generates optimization opportunities based on workload analysis
    """
    
    # Service-specific optimization templates
    EC2_OPTIMIZATIONS = {
        'right_sizing': {
            'title': 'EC2 Instance Right-Sizing',
            'category': 'EC2',
            'description': 'Resize underutilized EC2 instances to reduce carbon and cost'
        },
        'auto_scaling': {
            'title': 'Enable EC2 Auto Scaling',
            'category': 'EC2',
            'description': 'Implement auto-scaling to match demand and reduce idle capacity'
        },
        'spot_instances': {
            'title': 'Use EC2 Spot Instances',
            'category': 'EC2',
            'description': 'Leverage spot instances for non-critical workloads'
        }
    }
    
    LAMBDA_OPTIMIZATIONS = {
        'memory': {
            'title': 'Optimize Lambda Memory Configuration',
            'category': 'Lambda',
            'description': 'Adjust Lambda memory settings for optimal performance/efficiency'
        },
        'invocations': {
            'title': 'Reduce Lambda Cold Starts',
            'category': 'Lambda',
            'description': 'Implement provisioned concurrency for frequently used functions'
        }
    }
    
    S3_OPTIMIZATIONS = {
        'lifecycle': {
            'title': 'S3 Lifecycle Policies',
            'category': 'S3',
            'description': 'Implement lifecycle policies to transition old data to cheaper storage'
        },
        'glacier': {
            'title': 'S3 Glacier Migration',
            'category': 'S3',
            'description': 'Move infrequently accessed data to S3 Glacier'
        }
    }
    
    SAGEMAKER_OPTIMIZATIONS = {
        'training_schedule': {
            'title': 'Schedule SageMaker Training Jobs',
            'category': 'SageMaker',
            'description': 'Schedule training jobs during low carbon intensity hours'
        }
    }
    
    def __init__(self):
        self.optimization_stats = {
            'opportunities_generated': 0,
            'total_potential_reduction_kg': 0,
            'services_analyzed': 0
        }
    
    def generate_opportunities(
        self,
        workload_analysis: Dict,
        emission_records: List[Dict]
    ) -> List[Dict]:
        """
        Generate optimization opportunities based on workload analysis
        
        Args:
            workload_analysis: Output from WorkloadAnalysisAgent
            emission_records: Raw emission records
        
        Returns:
            List of optimization opportunities
        """
        logger.info("="*60)
        logger.info("[Smart Optimization Agent] Generating Opportunities")
        logger.info("="*60)
        
        opportunities = []
        
        # Service-specific optimizations
        service_analysis = workload_analysis['service_analysis']
        for service_data in service_analysis['top_services']:
            service = service_data['service']
            
            if 'EC2' in service or 'Elastic Compute Cloud' in service:
                opportunities.extend(self._generate_ec2_opportunities(service_data, emission_records))
            elif 'Lambda' in service:
                opportunities.extend(self._generate_lambda_opportunities(service_data, emission_records))
            elif 'S3' in service or 'Simple Storage Service' in service:
                opportunities.extend(self._generate_s3_opportunities(service_data, emission_records))
            elif 'SageMaker' in service:
                opportunities.extend(self._generate_sagemaker_opportunities(service_data, emission_records))
        
        # Region optimization opportunities
        region_opps = workload_analysis.get('region_opportunities', [])
        for opp in region_opps:
            opportunities.append({
                'type': 'region_migration',
                'title': f"Migrate from {opp['current_region']} to {opp['suggested_region']}",
                'category': 'Region',
                'service': 'Multi-Service',
                'carbon_reduction_pct': opp['potential_reduction_pct'],
                'carbon_reduction_kg': opp['potential_savings_kg'],
                'cost_impact': 'Neutral',
                'details': opp
            })
        
        # Time-shift opportunities
        time_opps = workload_analysis.get('time_opportunities', [])
        for opp in time_opps:
            opportunities.append({
                'type': 'time_shift',
                'title': f"Schedule {opp['service']} during low-carbon hours",
                'category': 'Time',
                'service': opp['service'],
                'carbon_reduction_pct': opp['potential_reduction_pct'],
                'carbon_reduction_kg': opp['potential_savings_kg'],
                'cost_impact': 'Neutral',
                'details': opp
            })
        
        # Calculate statistics
        self.optimization_stats['opportunities_generated'] = len(opportunities)
        self.optimization_stats['total_potential_reduction_kg'] = sum(
            o.get('carbon_reduction_kg', 0) for o in opportunities
        )
        self.optimization_stats['services_analyzed'] = len(service_analysis['top_services'])
        
        logger.info(f"✓ Generated {len(opportunities)} optimization opportunities")
        logger.info(f"  Potential Reduction: {self.optimization_stats['total_potential_reduction_kg']:.2f}kg CO2")
        
        return opportunities
    
    def _generate_ec2_opportunities(self, service_data: Dict, records: List[Dict]) -> List[Dict]:
        """Generate EC2-specific opportunities"""
        opportunities = []
        service = service_data['service']
        
        # Right-sizing opportunity (assume 20% reduction potential)
        if service_data['total_emissions'] > 10:  # Significant emissions
            opportunities.append({
                'type': 'ec2_right_sizing',
                'title': self.EC2_OPTIMIZATIONS['right_sizing']['title'],
                'category': 'EC2',
                'service': service,
                'carbon_reduction_pct': 20,
                'carbon_reduction_kg': service_data['total_emissions'] * 0.20,
                'cost_impact': 'Positive',
                'details': {
                    'description': self.EC2_OPTIMIZATIONS['right_sizing']['description'],
                    'current_emissions': service_data['total_emissions'],
                    'estimated_reduction': service_data['total_emissions'] * 0.20
                }
            })
        
        # Auto-scaling opportunity
        if service_data['count'] > 100:  # Frequently used
            opportunities.append({
                'type': 'ec2_auto_scaling',
                'title': self.EC2_OPTIMIZATIONS['auto_scaling']['title'],
                'category': 'EC2',
                'service': service,
                'carbon_reduction_pct': 15,
                'carbon_reduction_kg': service_data['total_emissions'] * 0.15,
                'cost_impact': 'Positive',
                'details': {
                    'description': self.EC2_OPTIMIZATIONS['auto_scaling']['description'],
                    'current_emissions': service_data['total_emissions'],
                    'estimated_reduction': service_data['total_emissions'] * 0.15
                }
            })
        
        return opportunities
    
    def _generate_lambda_opportunities(self, service_data: Dict, records: List[Dict]) -> List[Dict]:
        """Generate Lambda-specific opportunities"""
        opportunities = []
        service = service_data['service']
        
        # Memory optimization
        if service_data['total_emissions'] > 5:
            opportunities.append({
                'type': 'lambda_memory',
                'title': self.LAMBDA_OPTIMIZATIONS['memory']['title'],
                'category': 'Lambda',
                'service': service,
                'carbon_reduction_pct': 10,
                'carbon_reduction_kg': service_data['total_emissions'] * 0.10,
                'cost_impact': 'Neutral',
                'details': {
                    'description': self.LAMBDA_OPTIMIZATIONS['memory']['description'],
                    'current_emissions': service_data['total_emissions'],
                    'estimated_reduction': service_data['total_emissions'] * 0.10
                }
            })
        
        return opportunities
    
    def _generate_s3_opportunities(self, service_data: Dict, records: List[Dict]) -> List[Dict]:
        """Generate S3-specific opportunities"""
        opportunities = []
        service = service_data['service']
        
        # Lifecycle policies
        if service_data['total_emissions'] > 5:
            opportunities.append({
                'type': 's3_lifecycle',
                'title': self.S3_OPTIMIZATIONS['lifecycle']['title'],
                'category': 'S3',
                'service': service,
                'carbon_reduction_pct': 30,
                'carbon_reduction_kg': service_data['total_emissions'] * 0.30,
                'cost_impact': 'Positive',
                'details': {
                    'description': self.S3_OPTIMIZATIONS['lifecycle']['description'],
                    'current_emissions': service_data['total_emissions'],
                    'estimated_reduction': service_data['total_emissions'] * 0.30
                }
            })
        
        return opportunities
    
    def _generate_sagemaker_opportunities(self, service_data: Dict, records: List[Dict]) -> List[Dict]:
        """Generate SageMaker-specific opportunities"""
        opportunities = []
        service = service_data['service']
        
        # Training schedule optimization
        if service_data['total_emissions'] > 10:
            opportunities.append({
                'type': 'sagemaker_schedule',
                'title': self.SAGEMAKER_OPTIMIZATIONS['training_schedule']['title'],
                'category': 'SageMaker',
                'service': service,
                'carbon_reduction_pct': 25,
                'carbon_reduction_kg': service_data['total_emissions'] * 0.25,
                'cost_impact': 'Neutral',
                'details': {
                    'description': self.SAGEMAKER_OPTIMIZATIONS['training_schedule']['description'],
                    'current_emissions': service_data['total_emissions'],
                    'estimated_reduction': service_data['total_emissions'] * 0.25
                }
            })
        
        return opportunities
    
    def get_optimization_stats(self) -> Dict:
        """Get optimization statistics"""
        return self.optimization_stats.copy()
