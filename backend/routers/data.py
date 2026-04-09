from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from schemas.schemas import *
from typing import List
from services import analytics_service

"""
Its the HTTP layer, for URL params, response codes, pydantic response models
"""

router = APIRouter()

@router.get("/gyms", response_model=List[GymResponse])
def get_all_gyms(db: Session = Depends(get_session)):
    return analytics_service.get_all_gyms(db=db)



@router.get("/gyms/{facility_id}/history", response_model=OccupancyHistoryResponse)
def get_history(facility_id: str, range: str = "1D", db: Session = Depends(get_session)):
    return analytics_service.get_history(facility_id=facility_id, range=range, db=db)



@router.get("/gyms/{facility_id}/heatmap", response_model=HeatmapResponse)
def get_heatmap(facility_id: str, db: Session = Depends(get_session)):
    return analytics_service.get_heatmap(facility_id=facility_id, db=db)



@router.get("/gyms/{facility_id}/best-time", response_model=BestTimeResponse)
def get_best_time(facility_id: str, db: Session = Depends(get_session), limit: int = 5):
    return analytics_service.get_best_time(facility_id=facility_id, db=db, limit=limit)



@router.get("/gyms/{facility_id}/anomaly", response_model=AnomalyResponse)
def get_anomaly(facility_id: str, db: Session = Depends(get_session)):
    return analytics_service.get_anomaly(facility_id=facility_id, db=db)
