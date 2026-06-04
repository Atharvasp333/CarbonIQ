"""
AGENT 4: EMISSION CALCULATION AGENT
Purpose: Calculate emissions for every workload entry
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EmissionCalculationAgent:
    """Calculates energy consumption and CO2 emissions from AWS usage"""
    
    # Service-specific energy estimation factors
    # Maps usage units to kWh conversion
    SERVICE_ENERGY_FACTORS = {
        # Compute services (kWh per hour)
        'EC2': {
            'unit': 'hours',
            'base_factor': 0.15,  # Base: average instance
            'instance_multipliers': {
                'nano': 0.1,
                'micro': 0.2,
                'small': 0.3,
                'medium': 0.5,
                'large': 1.0,
                'xlarge': 2.0,
                '2xlarge': 4.0,
                '4xlarge': 8.0,
                '8xlarge': 16.0,
                '12xlarge': 24.0,
                '16xlarge': 32.0,
                '24xlarge': 48.0,
            }
        },
        'RDS': {
            'unit': 'hours',
            'base_factor': 0.12,
            'instance_multipliers': {
                'micro': 0.15,
                'small': 0.25,
                'medium': 0.4,
                'large': 0.8,
                'xlarge': 1.6,
                '2xlarge': 3.2,
                '4xlarge': 6.4,
                '8xlarge': 12.8,
            }
        },
        'SageMaker': {
            'unit': 'hours',
            'base_factor': 0.18,  # Training instances typically higher power
            'instance_multipliers': {
                'medium': 0.5,
                'large': 1.0,
                'xlarge': 2.5,
                '2xlarge': 5.0,
                '4xlarge': 10.0,
                '8xlarge': 20.0,
            }
        },
        'ECS': {
            'unit': 'hours',
            'base_factor': 0.10,
        },
        'EKS': {
            'unit': 'hours',
            'base_factor': 0.10,
        },
        'ElastiCache': {
            'unit': 'hours',
            'base_factor': 0.08,
        },
        
        # Serverless (kWh per GB-second or invocation)
        'Lambda': {
            'unit': 'gb-seconds',
            'base_factor': 0.0001,  # Very efficient
        },
        
        # Storage (kWh per GB-hour)
        'S3': {
            'unit': 'gb-hours',
            'base_factor': 0.0000005,
        },
        'EBS': {
            'unit': 'gb-hours',
            'base_factor': 0.000002,
        },
        'DynamoDB': {
            'unit': 'requests',
            'base_factor': 0.00000001,
        },
        
        # Networking (kWh per GB transferred)
        'CloudFront': {
            'unit': 'gb',
            'base_factor': 0.0001,
        },
    }
    
    def __init__(self):
        self.calculations_performed = 0
        self.total_energy = 0.0
        self.total_emissions = 0.0
    
    def calculate_emission(
        self,
        service: str,
        usage_amount: float,
        carbon_intensity: float,
        usage_type: Optional[str] = None,
        operation: Optional[str] = None
    ) -> Dict:
        """
        Calculate energy and emissions for a workload
        
        Args:
            service: AWS service name (EC2, Lambda, etc.)
            usage_amount: Usage quantity from CUR
            carbon_intensity: Carbon intensity in gCO2/kWh
            usage_type: Optional usage type for better estimation
            operation: Optional operation type
        
        Returns: {
            service, usage_amount, energy_kwh, carbon_intensity,
            emissions_kg, estimation_method
        }
        """
        # Estimate energy consumption
        energy_kwh = self._estimate_energy(service, usage_amount, usage_type)
        
        # Calculate emissions: CO2 = Energy × Carbon Intensity
        # carbon_intensity is in gCO2/kWh, convert to kg
        emissions_kg = (energy_kwh * carbon_intensity) / 1000
        
        self.calculations_performed += 1
        self.total_energy += energy_kwh
        self.total_emissions += emissions_kg
        
        return {
            'service': service,
            'usage_amount': usage_amount,
            'energy_kwh': round(energy_kwh, 6),
            'carbon_intensity': carbon_intensity,
            'emissions_kg': round(emissions_kg, 6),
            'estimation_method': self._get_estimation_method(service)
        }
    
    def _estimate_energy(
        self,
        service: str,
        usage_amount: float,
        usage_type: Optional[str] = None
    ) -> float:
        """Estimate energy consumption in kWh"""
        if usage_amount <= 0:
            return 0.0
        
        # Get service energy profile
        service_profile = self.SERVICE_ENERGY_FACTORS.get(service)
        
        if not service_profile:
            # Unknown service - use generic compute factor
            logger.warning(f"Unknown service {service}, using generic factor")
            return usage_amount * 0.1
        
        base_factor = service_profile['base_factor']
        
        # Apply instance size multiplier if available
        if 'instance_multipliers' in service_profile and usage_type:
            multiplier = self._get_instance_multiplier(
                service_profile['instance_multipliers'],
                usage_type
            )
            base_factor *= multiplier
        
        # Calculate energy
        energy_kwh = usage_amount * base_factor
        
        return energy_kwh
    
    def _get_instance_multiplier(
        self,
        multipliers: Dict[str, float],
        usage_type: str
    ) -> float:
        """Extract instance size multiplier from usage type"""
        usage_lower = usage_type.lower()
        
        # Try to find size keyword in usage type
        for size, multiplier in multipliers.items():
            if size in usage_lower:
                return multiplier
        
        # Default to 1.0 (large equivalent)
        return 1.0
    
    def _get_estimation_method(self, service: str) -> str:
        """Return description of estimation method used"""
        if service in self.SERVICE_ENERGY_FACTORS:
            return f"{service}_specific"
        else:
            return "generic_compute"
    
    def calculate_batch(
        self,
        workloads: list[Dict]
    ) -> list[Dict]:
        """
        Calculate emissions for multiple workloads
        
        Args:
            workloads: List of {service, usage_amount, carbon_intensity, usage_type, operation}
        
        Returns: List of emission calculation results
        """
        results = []
        
        for workload in workloads:
            result = self.calculate_emission(
                service=workload['service'],
                usage_amount=workload['usage_amount'],
                carbon_intensity=workload['carbon_intensity'],
                usage_type=workload.get('usage_type'),
                operation=workload.get('operation')
            )
            
            # Merge with original workload data
            result.update({
                'region': workload.get('region'),
                'timestamp': workload.get('timestamp'),
                'zone': workload.get('zone'),
                'cost': workload.get('cost', 0),
                'resource_id': workload.get('resource_id', ''),
            })
            
            results.append(result)
        
        return results
    
    def get_calculation_stats(self) -> Dict:
        """Return calculation statistics"""
        return {
            'calculations_performed': self.calculations_performed,
            'total_energy_kwh': round(self.total_energy, 2),
            'total_emissions_kg': round(self.total_emissions, 2),
            'avg_emissions_per_calc': round(
                self.total_emissions / max(self.calculations_performed, 1), 4
            )
        }
