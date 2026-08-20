# CarbonIQ Multi-Agent System

## Overview

This directory contains the 6 specialized agents that power CarbonIQ's carbon intelligence pipeline.

## Agent Files

```
agents/
├── __init__.py                      # Package init
├── ingestion_agent.py              # Agent 1: CUR Ingestion & Normalization
├── region_mapping_agent.py         # Agent 2: AWS Region → Electricity Maps
├── carbon_intensity_agent.py       # Agent 3: Historical Carbon Intensity
├── emission_calculation_agent.py   # Agent 4: Energy & Emission Calculation
├── analytics_agent.py              # Agent 5: Dashboard Analytics
├── optimization_agent.py           # Agent 6: Optimization Engine
└── orchestrator.py                 # Pipeline Coordinator
```

## Quick Reference

### Agent 1: CUR Ingestion & Normalization
**Input:** AWS CUR CSV  
**Output:** Normalized records  
**Key Functions:**
- `process_csv(csv_content)` - Main entry point
- `get_validation_summary()` - Error tracking

### Agent 2: Region Mapping
**Input:** AWS region codes  
**Output:** Electricity Maps zones  
**Key Functions:**
- `map_region(region)` - Single region mapping
- `map_batch(regions)` - Batch mapping
- `get_supported_regions()` - All mappings

### Agent 3: Carbon Intensity
**Input:** Zone + timestamp  
**Output:** Historical carbon intensity (gCO₂/kWh)  
**Key Functions:**
- `get_historical_intensity(zone, timestamp)` - Async API call
- `get_batch_intensities(requests)` - Batch processing
- `get_cache_stats()` - Performance metrics

### Agent 4: Emission Calculation
**Input:** Usage + carbon intensity  
**Output:** Energy (kWh) + emissions (kg CO₂)  
**Key Functions:**
- `calculate_emission(service, usage, intensity)` - Single calculation
- `calculate_batch(workloads)` - Batch calculations
- `get_calculation_stats()` - Statistics

### Agent 5: Analytics
**Input:** Emission records  
**Output:** Dashboard metrics  
**Key Functions:**
- `generate_analytics(records)` - Full analytics
- `get_summary_stats()` - Summary only

### Agent 6: Optimization
**Input:** Analytics + emission records  
**Output:** Opportunities + recommendations  
**Key Functions:**
- `analyze_opportunities(records, analytics)` - Find optimizations
- `get_optimization_stats()` - Opportunity count

### Orchestrator
**Coordinates all agents in sequence**  
**Key Functions:**
- `process_cur_data(csv_content)` - Main pipeline
- `get_pipeline_status()` - System health

## Usage Example

```python
from agents.orchestrator import CarbonIQOrchestrator

# Initialize
orchestrator = CarbonIQOrchestrator()

# Process CUR data
result = await orchestrator.process_cur_data(csv_content)

# Access results
print(f"Total emissions: {result['summary']['total_emissions_kg']} kg")
print(f"Opportunities: {len(result['optimization']['opportunities'])}")
```

## Agent Communication Flow

```
CSV File
   ↓
Agent 1: Parse & Normalize
   ↓
Agent 2: Map to Zones
   ↓
Agent 3: Fetch Carbon Intensity (with caching)
   ↓
Agent 4: Calculate Emissions
   ↓
Agent 5: Generate Analytics
   ↓
Agent 6: Find Optimizations
   ↓
Dashboard
```

## Adding New Agents

To add a new agent:

1. Create new file: `your_agent.py`
2. Define agent class with clear methods
3. Import in `orchestrator.py`
4. Add to pipeline sequence
5. Update this README

## Performance Considerations

- **Caching**: Agent 3 caches by (zone, hour) for ~80% hit rate
- **Batch Processing**: All agents support batch operations
- **Error Handling**: Fallback mechanisms throughout
- **Scalability**: Tested with 1000+ CUR rows

## Testing

Run the test script:
```bash
python test_multi_agent.py
```

## Environment Variables

```bash
# Required for live carbon intensity data
ELECTRICITY_MAPS_API_KEY=your_key

# Optional for AI insights
GEMINI_API_KEY=your_key
```

## Error Handling

Each agent includes:
- Input validation
- Error logging
- Fallback mechanisms
- Statistics tracking

## Documentation

- **Quick Start**: `../MULTI_AGENT_QUICKSTART.md`
- **Architecture**: `../MULTI_AGENT_ARCHITECTURE.md`
- **API Docs**: `../routes/multi_agent_analysis.py`

---

**Built with modularity, scalability, and maintainability in mind** 🚀
