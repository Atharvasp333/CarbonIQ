from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.csv_parser import parse_usage_csv
from services.energy_calculator import calculate_energy
from services.climatiq_service import estimate_emissions
from data.results_store import save_result
from datetime import datetime

router = APIRouter()

@router.post("/upload-custom-csv")
async def upload_usage_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file containing `runtime`, `cpu_usage`, and `region`.
    Calculates total energy and emissions and aggregates the results.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
    try:
        content = await file.read()
        csv_text = content.decode('utf-8')
        rows = parse_usage_csv(csv_text)
        
        total_energy = 0.0
        total_emissions = 0.0
        details = []
        
        for row in rows:
            energy = calculate_energy(row["runtime"], row["cpu_usage"])
            emissions = await estimate_emissions(energy, row["region"])
            total_energy += energy
            total_emissions += emissions
            
            details.append({
                "runtime": row["runtime"],
                "cpu_usage": row["cpu_usage"],
                "region": row["region"],
                "energy_kwh": round(energy, 4),
                "emissions_kg_co2e": round(emissions, 4)
            })
            
        result = {
            "type": "csv_upload",
            "filename": file.filename,
            "total_energy_kwh": round(total_energy, 4),
            "total_emissions_kg_co2e": round(total_emissions, 4),
            "row_count": len(rows),
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        save_result(result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
