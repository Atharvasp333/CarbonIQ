"""
AGENT 2: REGION MAPPING AGENT
Purpose: Convert AWS regions into Electricity Maps zones
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RegionMappingAgent:
    """Maps AWS regions to Electricity Maps zones"""
    
    # AWS Region to Electricity Maps Zone mapping
    REGION_ZONE_MAP = {
        # US Regions
        'us-east-1': 'US-MIDA-PJM',      # Virginia
        'us-east-2': 'US-MIDW-MISO',     # Ohio
        'us-west-1': 'US-CAL-CISO',      # California
        'us-west-2': 'US-NW-PACW',       # Oregon
        
        # Global/Unknown
        'global': 'US-MIDA-PJM',         # Default to US East for global services
        
        # EU Regions
        'eu-west-1': 'IE',               # Ireland
        'eu-west-2': 'GB',               # London
        'eu-west-3': 'FR',               # Paris
        'eu-central-1': 'DE',            # Frankfurt
        'eu-north-1': 'SE',              # Stockholm
        'eu-south-1': 'IT-NO',           # Milan
        
        # Asia Pacific
        'ap-south-1': 'IN-WE',           # Mumbai (West India zone)
        'ap-southeast-1': 'SG',          # Singapore
        'ap-southeast-2': 'AU-NSW',      # Sydney
        'ap-northeast-1': 'JP-TK',       # Tokyo
        'ap-northeast-2': 'KR',          # Seoul
        'ap-northeast-3': 'JP-KN',       # Osaka
        'ap-east-1': 'HK',               # Hong Kong
        
        # Canada
        'ca-central-1': 'CA-ON',         # Montreal
        
        # South America
        'sa-east-1': 'BR-CS',            # São Paulo
        
        # Middle East
        'me-south-1': 'BH',              # Bahrain
        'me-central-1': 'IL',            # Tel Aviv
        
        # Africa
        'af-south-1': 'ZA',              # Cape Town
    }
    
    # Fallback zones for unmapped regions
    FALLBACK_ZONE = 'US-MIDA-PJM'
    
    def __init__(self):
        self.mapping_errors = []
        self.mapped_count = 0
        self.fallback_count = 0
    
    def map_region(self, region: str) -> Dict:
        """
        Convert AWS region to Electricity Maps zone
        
        Returns: {region, electricity_maps_zone, is_fallback, location_name}
        """
        region = region.strip().lower()
        
        # Check if region is mapped
        zone = self.REGION_ZONE_MAP.get(region)
        
        if zone:
            self.mapped_count += 1
            return {
                'region': region,
                'electricity_maps_zone': zone,
                'is_fallback': False,
                'location_name': self._get_location_name(region)
            }
        else:
            # Use fallback
            self.fallback_count += 1
            logger.warning(f"Unknown region '{region}', using fallback zone: {self.FALLBACK_ZONE}")
            self.mapping_errors.append({
                'region': region,
                'message': f"Unknown region, using fallback: {self.FALLBACK_ZONE}"
            })
            
            return {
                'region': region,
                'electricity_maps_zone': self.FALLBACK_ZONE,
                'is_fallback': True,
                'location_name': 'Unknown'
            }
    
    def map_batch(self, regions: list) -> Dict[str, Dict]:
        """Map multiple regions at once"""
        results = {}
        for region in set(regions):  # Unique regions only
            results[region] = self.map_region(region)
        
        return results
    
    def _get_location_name(self, region: str) -> str:
        """Get human-readable location name for region"""
        location_names = {
            'us-east-1': 'Virginia',
            'us-east-2': 'Ohio',
            'us-west-1': 'California',
            'us-west-2': 'Oregon',
            'eu-west-1': 'Ireland',
            'eu-west-2': 'London',
            'eu-west-3': 'Paris',
            'eu-central-1': 'Frankfurt',
            'eu-north-1': 'Stockholm',
            'eu-south-1': 'Milan',
            'ap-south-1': 'Mumbai',
            'ap-southeast-1': 'Singapore',
            'ap-southeast-2': 'Sydney',
            'ap-northeast-1': 'Tokyo',
            'ap-northeast-2': 'Seoul',
            'ap-northeast-3': 'Osaka',
            'ap-east-1': 'Hong Kong',
            'ca-central-1': 'Montreal',
            'sa-east-1': 'São Paulo',
            'me-south-1': 'Bahrain',
            'me-central-1': 'Tel Aviv',
            'af-south-1': 'Cape Town',
        }
        
        return location_names.get(region, region)
    
    def get_mapping_summary(self) -> Dict:
        """Return summary of mapping results"""
        return {
            'mapped_count': self.mapped_count,
            'fallback_count': self.fallback_count,
            'errors': self.mapping_errors,
            'total_regions': self.mapped_count + self.fallback_count
        }
    
    @staticmethod
    def get_supported_regions() -> Dict[str, str]:
        """Return all supported region mappings"""
        return RegionMappingAgent.REGION_ZONE_MAP.copy()
