import json
import random
from typing import Dict, Any, List, Optional
from api.agents.state import ScoredCrop

# Load crop dataset
try:
    with open("data/crops.json", "r") as f:
        CROP_DATASET = json.load(f)
except Exception:
    CROP_DATASET = []

def soil_agent(crop: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    score = 1.0
    warnings = []
    
    # pH check
    ph = profile.get("soil_ph")
    if ph:
        ph_range = crop.get("ph_range", [5.5, 7.5])
        if ph < ph_range[0] or ph > ph_range[1]:
            score *= 0.7
            warnings.append(f"Soil pH ({ph}) is outside ideal range ({ph_range[0]}-{ph_range[1]})")
            
    # Soil type check
    preferred_soils = [s.lower() for s in crop.get("soil_types", [])]
    farmer_soil = profile.get("soil_type", "").lower()
    
    # check soil distribution if available
    soil_dist = profile.get("soil_type_distribution")
    if isinstance(soil_dist, str):
        try: soil_dist = json.loads(soil_dist)
        except: soil_dist = []
        
    if soil_dist:
        # if any part of the land matches
        matches = [d for d in soil_dist if d.get("type", "").lower() in preferred_soils]
        if not matches:
            score *= 0.6
            warnings.append(f"Crop typically prefers {', '.join(preferred_soils)} soil")
    elif farmer_soil and farmer_soil not in preferred_soils:
        score *= 0.6
        warnings.append(f"Crop typically prefers {', '.join(preferred_soils)} soil")
        
    return {"score": score, "warnings": warnings}

def water_agent(crop: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    score = 1.0
    setup_required = None
    setup_impact = 0.0
    warnings = []
    
    water_source = profile.get("water_source", "Rain-fed")
    crop_need = crop.get("water_need", "medium").lower()
    
    # If high water need but rain-fed
    if crop_need in ["high", "very_high"] and water_source == "Rain-fed":
        score = 0.2 # Critical mismatch
        setup_required = "Drip Irrigation or Borewell"
        setup_impact = 0.75 # Massive boost if setup is done
        warnings.append(f"High water needs are risky for Rain-fed farms. Drip Irrigation recommended.")
    elif crop_need == "medium" and water_source == "Rain-fed":
        score *= 0.7
        setup_required = "Sprinkler System"
        setup_impact = 0.2
        warnings.append("Moderate water needs might be tight for Rain-fed farms.")
        
    return {
        "score": score, 
        "setup_required": setup_required, 
        "setup_impact": setup_impact,
        "warnings": warnings
    }

def market_agent(crop: Dict[str, Any]) -> Dict[str, Any]:
    # Mocking price trend analysis
    trends = ["stable", "rising", "volatile"]
    trend = random.choice(trends)
    score = 1.0
    if trend == "rising": score = 1.2
    if trend == "volatile": score = 0.8
    
    return {"score": score, "market_trend": trend}

def policy_agent(crop: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    subsidies = []
    # logic for PMFBY, Irrigation subsidies
    if crop.get("category") in ["cereal", "oilseed"]:
        subsidies.append("PMFBY Crop Insurance available")
    
    # If setup is required, add infrastructure subsidies
    return {"subsidies": subsidies}

def sustainability_agent(crop: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    # Check for crop rotation benefits
    score = 1.0
    if crop.get("category") == "pulse":
        score = 1.2 # Legumes fix nitrogen
    return {"score": score}

def pest_agent(crop: Dict[str, Any], pest_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    score = 1.0
    warnings = []
    
    # check if this crop was affected recently
    crop_name = crop["name"].lower()
    past_attacks = [p for p in pest_history if p.get("affected_crop", "").lower() == crop_name]
    
    if past_attacks:
        score *= 0.8
        warnings.append(f"Warning: This farm has a history of {past_attacks[0]['pest_name']} on {crop['name']}")
        
    return {"score": score, "warnings": warnings}

def orchestrator_score_crops(profile: Dict[str, Any], pest_history: List[Dict[str, Any]]) -> List[ScoredCrop]:
    scored_list = []
    
    for crop in CROP_DATASET:
        # Run agents
        soil = soil_agent(crop, profile)
        water = water_agent(crop, profile)
        market = market_agent(crop)
        policy = policy_agent(crop, profile)
        sustain = sustainability_agent(crop, profile)
        pest = pest_agent(crop, pest_history)
        
        # Conflict Resolution & Proactive Setup logic
        base_score = (soil["score"] + water["score"] + sustain["score"] + pest["score"]) / 4.0
        final_score = base_score * market["score"]
        
        # Calculate potential score (if setup is done)
        potential_score = final_score
        if water.get("setup_required"):
            potential_score = (base_score + water["setup_impact"]) * market["score"]

        # Balanced Logic: Priority to Actual Suitability (75%) + Potential (25%)
        # This ensures currently feasible crops stay at the top,
        # while high-impact suggestions (like Drip Irrigation) still surface.
        blended_score = (final_score * 0.75) + (potential_score * 0.25)
            
        scored_list.append({
            "name": crop["name"],
            "base_score": round(base_score, 2),
            "final_score": round(final_score, 2),
            "potential_score": round(potential_score, 2),
            "blended_score": round(blended_score, 2),
            "suitability_details": {
                "soil": soil["score"],
                "water": water["score"],
                "market": market["market_trend"],
                "sustainability": sustain["score"]
            },
            "required_setup": water.get("setup_required"),
            "setup_impact": water.get("setup_impact"),
            "subsidies": policy["subsidies"],
            "warnings": soil["warnings"] + water["warnings"] + pest["warnings"]
        })
        
    # Sort by Blended Score (75% Now / 25% Future)
    scored_list.sort(key=lambda x: x["blended_score"], reverse=True)
    
    return scored_list
