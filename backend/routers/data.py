from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models.gym import GymMetaData, GymOccupancyData
from schemas.schemas import GymResponse, OccupancyHistoryResponse, OccupancyRecord
from typing import List

"""
Its the HTTP layer, for URL params, response codes, pydantic response models
"""

router = APIRouter()

@router.get("/gyms", response_model=List[GymResponse])
def get_all_gyms(db: Session = Depends(get_session)):
    
    statement = select(GymMetaData)
    gyms = db.exec(statement).all()
    return gyms
