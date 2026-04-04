from fastapi import APIRouter, HTTPException, Depends
from api.db.models import FarmerCreate, FarmerLogin
from db.database import create_farmer, login_farmer, update_farmer_profile, get_farmer

router = APIRouter()

@router.put("/profile/{farmer_id}")
def update_profile(farmer_id: int, data: dict):
    try:
        update_farmer_profile(farmer_id, **data)
        updated_farmer = get_farmer(farmer_id)
        return {"status": "success", "farmer": updated_farmer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
def register(farmer: FarmerCreate):
    try:
        new_farmer = create_farmer(farmer.name, farmer.email, farmer.password, farmer.location)
        return {"status": "success", "farmer": new_farmer}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(credentials: FarmerLogin):
    farmer = login_farmer(credentials.email, credentials.password)
    if not farmer:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"status": "success", "farmer": farmer}
