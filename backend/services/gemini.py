import os
import json
import logging
import google.generativeai as genai
from models.schemas import AWSInsightRequest, AWSInsightResponse

logger = logging.getLogger(__name__)


async def get_aws_insights(request: AWSInsightRequest) -> AWSInsightResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key and api_key != "your_gemini_api_key_here":
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            services_text = "\n".join([
                f"- {item['service']}: {item['co2_kg']} kg CO₂ (${item['cost']})"
                for item in request.by_service[:5]
            ])
            
            regions_text = "\n".join([
                f"- {item['region']}: {item['co2_kg']} kg CO₂"
                for item in request.by_region[:5]
            ])
            
            prompt = f"""You are an AWS cloud sustainability expert.

AWS Cloud Carbon Analysis:
Total Emissions: {request.total_co2_kg} kg CO₂
Total Cost: ${request.total_cost}
Top Service: {request.top_service}
Top Region: {request.top_region}

Emissions by Service:
{services_text}

Emissions by Region:
{regions_text}

Provide EXACTLY 4 actionable recommendations to reduce AWS carbon emissions.
Respond in this JSON format only:
{{
  "recommendations": [
    {{
      "priority": "high|medium|low",
      "category": "region|instance|service|idle",
      "title": "<short title>",
      "description": "<specific recommendation>",
      "estimated_savings_kg": <number>,
      "estimated_savings_cost": <number>
    }}
  ],
  "summary": "<one sentence overall assessment>",
  "carbon_budget_status": {{
    "current_monthly_kg": <estimated monthly CO2>,
    "recommended_target_kg": <recommended target>,
    "status": "over_budget|on_track|excellent"
  }}
}}"""
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            data = json.loads(text)
            return AWSInsightResponse(**data)
            
        except Exception as e:
            logger.warning(f"Gemini API error: {e}. Using fallback suggestions.")
            return _fallback_aws_insights(request)
    else:
        logger.warning("Gemini API key not configured. Using fallback suggestions.")
        return _fallback_aws_insights(request)


def _fallback_aws_insights(request: AWSInsightRequest) -> AWSInsightResponse:
    recommendations = [
        {
            "priority": "high",
            "category": "region",
            "title": "Migrate to Low-Carbon Regions",
            "description": f"Move workloads from {request.top_region} to us-west-1 (California) or eu-west-1 (Ireland) for 30-40% emission reduction",
            "estimated_savings_kg": request.total_co2_kg * 0.35,
            "estimated_savings_cost": request.total_cost * 0.05
        },
        {
            "priority": "high",
            "category": "idle",
            "title": "Remove Idle Resources",
            "description": "Detected resources with low usage but high cost. Terminate or schedule them to save 15-20% emissions",
            "estimated_savings_kg": request.total_co2_kg * 0.18,
            "estimated_savings_cost": request.total_cost * 0.20
        },
        {
            "priority": "medium",
            "category": "instance",
            "title": "Right-Size EC2 Instances",
            "description": "Downsize over-provisioned instances to Graviton-based alternatives for better efficiency",
            "estimated_savings_kg": request.total_co2_kg * 0.25,
            "estimated_savings_cost": request.total_cost * 0.30
        },
        {
            "priority": "medium",
            "category": "service",
            "title": "Optimize Storage & Lambda",
            "description": "Use S3 Intelligent-Tiering and optimize Lambda memory allocation to reduce waste",
            "estimated_savings_kg": request.total_co2_kg * 0.10,
            "estimated_savings_cost": request.total_cost * 0.15
        }
    ]
    
    monthly_co2 = request.total_co2_kg * 30
    recommended_target = monthly_co2 * 0.70
    
    return AWSInsightResponse(
        recommendations=recommendations,
        summary=f"Your AWS infrastructure emits {request.total_co2_kg} kg CO₂ daily. Implementing these recommendations can reduce emissions by 40-50%.",
        carbon_budget_status={
            "current_monthly_kg": round(monthly_co2, 2),
            "recommended_target_kg": round(recommended_target, 2),
            "status": "over_budget" if monthly_co2 > 10000 else "on_track"
        }
    )
