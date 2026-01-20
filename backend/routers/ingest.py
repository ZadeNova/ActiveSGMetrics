from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from schemas import Gym_Data_From_Scraper, GymData
from services.ingest_service import ingest_gym_data
from database import get_session
from sqlmodel import Session

router = APIRouter()

@router.post("/ingestdata", status_code=status.HTTP_201_CREATED)
def ingest_data(
    payload: List[GymData],
    db: Session = Depends(get_session)
):
    try:
        result = ingest_gym_data(payload=payload, db=db)
        
        return {
            "status": "success",
            "message" : f"Successfully processed {result} gyms"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    