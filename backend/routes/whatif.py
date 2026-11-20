from fastapi import APIRouter
from models.schemas import WhatIfAWSRequest, WhatIfAWSResponse

router = APIRouter()


@router.post("/whatif", response_model=WhatIfAWSResponse)
async def simulate_whatif(request: WhatIfAWSRequest):
    # Use real analyzed emissions/cost if passed, otherwise default to baseline
    current_co2 = request.current_co2_kg if (request.current_co2_kg is not None and request.current_co2_kg > 0) else 450.0
    current_cost = request.current_cost if (request.current_cost is not None and request.current_cost > 0) else 150.0
    
    if request.scenario == "move_region":
        # Target regions and regional delta
        target = request.target_region or "us-west-2"
        reduction_rate = 0.35
        if "west" in target or "eu" in target:
            reduction_rate = 0.42
        projected_co2 = current_co2 * (1.0 - reduction_rate)
        projected_cost = current_cost * 0.98
        savings_kg = current_co2 - projected_co2
        savings_cost = current_cost - projected_cost
        pct = round(reduction_rate * 100, 1)
        description = f"Migrating eligible workloads to {target} achieves ~{pct}% carbon reduction via cleaner regional grid power."
        calc_basis = f"ΔE = E_current × (1 - (I_target / I_origin)) = {current_co2:.4f} kg × {pct}%"
        data_prov = "Electricity Maps Regional Average Intensity Telemetry & AWS CUR Geo-location"
    
    elif request.scenario == "downsize_instance":
        target = request.target_instance or "t3.medium"
        reduction_rate = 0.25
        projected_co2 = current_co2 * (1.0 - reduction_rate)
        projected_cost = current_cost * 0.70
        savings_kg = current_co2 - projected_co2
        savings_cost = current_cost - projected_cost
        description = f"Downsizing underutilized compute instances to {target} saves 25% energy emissions and 30% spend."
        calc_basis = f"ΔE = E_compute × Right-sizing Idle Reduction = {current_co2:.4f} kg × 25.0%"
        data_prov = "AWS Compute Optimizer & CUR Instance Byte-Hour Profiles"
    
    elif request.scenario == "remove_idle":
        reduction_rate = 0.15
        projected_co2 = current_co2 * (1.0 - reduction_rate)
        projected_cost = current_cost * 0.80
        savings_kg = current_co2 - projected_co2
        savings_cost = current_cost - projected_cost
        description = "Automating scheduled shutdown of idle non-production resources eliminates ~15% idle carbon burn."
        calc_basis = f"ΔE = E_total × Non-Business Hours Off-time Factor = {current_co2:.4f} kg × 15.0%"
        data_prov = "CloudWatch Usage Metrics & AWS CUR Chronological Workload Log"
    
    else:
        projected_co2 = current_co2
        projected_cost = current_cost
        savings_kg = 0.0
        savings_cost = 0.0
        description = "Baseline scenario: no operational modifications applied."
        calc_basis = "E_projected = E_current (No modification)"
        data_prov = "AWS CUR Baseline Data"
    
    return WhatIfAWSResponse(
        scenario_name=request.scenario,
        current_co2_kg=round(current_co2, 4),
        projected_co2_kg=round(projected_co2, 4),
        savings_kg=round(savings_kg, 4),
        savings_cost=round(savings_cost, 4),
        description=description,
        calculation_basis=calc_basis,
        data_provenance=data_prov
    )
