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



# These two must be above, FastAPI matches routes from top down.
@router.get("/gyms/compare/history", response_model=CompareHistoryResponse)
def compare_history(ids: str, range: str = "7D", db: Session = Depends(get_session)):
    facility_ids = ids.split(",")
    return analytics_service.compare_history(facility_ids=facility_ids, range=range, db=db)



@router.get("/gyms/compare/heatmap", response_model=CompareHeatmapResponse)
def compare_heatmap(ids: str, db: Session = Depends(get_session)):
    facility_ids = ids.split(",")
    return analytics_service.compare_heatmap(facility_ids=facility_ids, db=db)



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



@router.get("/gyms/{facility_id}/day-over-day", response_model=DayOverDayResponse)
def get_day_over_day(facility_id: str, db: Session = Depends(get_session)):
    return analytics_service.get_day_over_day(facility_id=facility_id, db=db)