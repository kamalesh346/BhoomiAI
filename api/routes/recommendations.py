from fastapi import APIRouter, HTTPException
from db.database import get_crop_history, add_crop_history

router = APIRouter()

@router.post("/history")
def add_history_record(data: dict):
    try:
        add_crop_history(
            data["farmer_id"],
            data["crop"],
            data["season"],
            data["year"],
            data.get("yield_kg"),
            data.get("income"),
            data.get("notes", "")
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{farmer_id}")
def get_farm_history(farmer_id: int):
    try:
        history = get_crop_history(farmer_id)
        return {"status": "success", "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def get_recommendations():
    # Placeholder: Recommendations are now moved entirely inside the chat flow.
    # We keep this file/route empty or repurpose it later if needed.
    return {"status": "success", "message": "Recommendations are integrated into the Consultant Chat."}
