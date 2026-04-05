from fastapi import APIRouter, HTTPException, Depends
from api.db.models import FarmerCreate, FarmerLogin, FarmerProfileUpdate, PestHistoryCreate
from db.database import create_farmer, login_farmer, update_farmer_profile, get_farmer, add_pest_history, get_pest_history

router = APIRouter()

@router.put("/profile/{farmer_id}")
def update_profile(farmer_id: int, data: FarmerProfileUpdate):
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = data.dict(exclude_none=True)
        update_farmer_profile(farmer_id, **update_data)
        updated_farmer = get_farmer(farmer_id)
        return {"status": "success", "farmer": updated_farmer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
def register(farmer: FarmerCreate):
    try:
        new_farmer = create_farmer(farmer.name, farmer.email, farmer.password, farmer.location, farmer.land_size)
        return {"status": "success", "farmer": new_farmer}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(credentials: FarmerLogin):
    farmer = login_farmer(credentials.email, credentials.password)
    if not farmer:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"status": "success", "farmer": farmer}

@router.get("/pest-history/{farmer_id}")
def fetch_pest_history(farmer_id: int):
    try:
        history = get_pest_history(farmer_id)
        return {"status": "success", "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pest-history/{farmer_id}")
def create_pest_history(farmer_id: int, entry: PestHistoryCreate):
    try:
        add_pest_history(
            farmer_id, 
            entry.pest_name, 
            entry.affected_crop, 
            entry.severity, 
            entry.observation_date, 
            entry.description
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
