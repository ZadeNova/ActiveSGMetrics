from sqlalchemy import func, extract
from sqlmodel import select, Session
from models.gym import GymOccupancyData, GymMetaData
from schemas.schemas import *
from datetime import timezone, timedelta, datetime
from fastapi import HTTPException
from typing import NamedTuple


"""
Business Logic: For SQL querying the database.
"""

SGT_OFFSET = 8
SGT = timezone(timedelta(hours=SGT_OFFSET))
RANGE_DICT = {"1D": timedelta(days=1), "3D": timedelta(days=3), "7D": timedelta(days=7), "30D": timedelta(days=30)}

class HeatmapRow(NamedTuple):
    day_of_week: int
    hour: int
    avg_occupancy: float
    


def get_heatmap(facility_id: str, db: Session) -> HeatmapResponse:
    gym = get_gym_by_id(facility_id, db)
    results = _query_heatmap(facility_id=facility_id, db=db)
        
    return HeatmapResponse(
        facility_id = gym.facility_id,
        name= gym.name,
        data = [
            HeatmapCell(day_of_week=int(row.day_of_week), hour=int(row.hour), avg_occupancy=row.avg_occupancy)
            for row in results
        ]
    )


def get_best_time(facility_id: str, db: Session, limit: int = 5) -> list[QuietSlot]:
    results = get_heatmap(facility_id=facility_id, db=db)
    # Sorts by the avg_occupancy in ASC order and then slices it by the limit..
    sorted_slots = sorted(results.data, key=lambda x: x.avg_occupancy)[:limit]
    
    return BestTimeResponse(
        facility_id = results.facility_id,
        name= results.name,
        quietest_slots=[
            
            QuietSlot(day_of_week=int(s.day_of_week), hour=int(s.hour), avg_occupancy=s.avg_occupancy)
            
            for s in sorted_slots
        ]
        
    )
        
        
    
    
# write the get_history and get_all_gyms functions
    
def get_all_gyms(db: Session) -> list[GymResponse]:
    
    results = db.exec(
        select(GymMetaData)
    ).all()
    
    return [
        GymResponse(
            facility_id=gym.facility_id,
            name=gym.name,
            facility_type=gym.facility_type,
        )
        for gym in results
    ]

def get_history(facility_id: str, range: str, db: Session) -> OccupancyHistoryResponse:
    
    
    
    if range not in RANGE_DICT:
        raise HTTPException(status_code=422, detail="Invalid range. Must be 1D, 3D, 7D, or 30D")
    
    gym = get_gym_by_id(facility_id=facility_id, db=db)
    
    delta = RANGE_DICT[range]
    cutoff = datetime.now(timezone.utc) - delta
    
    results = _query_history(facility_id=facility_id, cutoff=cutoff, db=db)
    
    return OccupancyHistoryResponse(
        facility_id=gym.facility_id,
        name=gym.name,
        history=[
            OccupancyRecord(
                timestamp=record.timestamp.astimezone(SGT),
                occupancy_percentage=record.occupancy_percentage,
                is_closed=record.is_closed
            )
            for record in results
        ]
    )
    
    

def get_anomaly(facility_id: str, db: Session) -> AnomalyResponse:
    gym = get_gym_by_id(facility_id=facility_id, db=db)
    
    latest = db.exec(
        select(GymOccupancyData)
        .where(GymOccupancyData.facility_id == facility_id)
        .order_by(GymOccupancyData.timestamp.desc())
        .limit(1)
    ).first()
    
    if latest is None:
        raise HTTPException(status_code=404, detail="No data found for this facility")
    
    
    local_ts = latest.timestamp.astimezone(SGT)
    dow = (local_ts.weekday())  # day of week
    hour = local_ts.hour    
    
    stats = db.exec(
        select(
            
            # Line 1: Compute average of all occupancy readings in this bucket
            func.avg(GymOccupancyData.occupancy_percentage).label("mean"),
            
            # Line 2: Compute standard deviation of all readings in this bucket 
            func.stddev(GymOccupancyData.occupancy_percentage).label("stddev")
            
            
        )
        # Filter to this gym only
        .where(GymOccupancyData.facility_id == facility_id)
        
        # Filter to matching day of week - Same DOW conversion as heatmap
        .where(
            ((extract("dow", func.timezone("Asia/Singapore", GymOccupancyData.timestamp)) + 6) % 7) == dow
        )
        
        # Filter to matching hour in SGT
        .where(
            extract("hour", func.timezone("Asia/Singapore", GymOccupancyData.timestamp)) == hour
        )
    ).first()
    
    if stats.stddev is None or stats.stddev == 0:
        z_score = 0.0
    else:
        z_score = (latest.occupancy_percentage - stats.mean) / stats.stddev
    
   
    if abs(z_score) < 2:
        severity = "Normal"
        is_anomaly = False
    elif 2 <= abs(z_score) <= 3:
        severity = "Busier than usual"
        is_anomaly = True
    else:
        severity = "Unusually crowded"
        is_anomaly = True
        
    
    return AnomalyResponse(
        facility_id=facility_id,
        name= gym.name,
        is_anomaly= is_anomaly,
        current_occupancy=latest.occupancy_percentage,
        historical_mean= stats.mean,
        z_score = z_score,
        severity=severity,
        timestamp= latest.timestamp.astimezone(SGT),
        day_of_week=dow,
        hour=hour,
    ) 
        

        
def get_day_over_day(facility_id: str, db: Session) -> DayOverDayResponse:
    gym = get_gym_by_id(facility_id, db)
    
    now_utc = datetime.now(timezone.utc)
    now_sgt = now_utc.astimezone(SGT)
    today_start = now_sgt.replace(hour=0, minute=0, second=0, microsecond=0)
    last_week_start = today_start - timedelta(days=7)

    today_results = db.exec(
        select(
            extract("hour", func.timezone("Asia/Singapore", GymOccupancyData.timestamp)).label("hour"),
            func.avg(GymOccupancyData.occupancy_percentage).label("avg_occupancy")
        )
        .where(GymOccupancyData.facility_id == facility_id)
        .where(GymOccupancyData.timestamp >= today_start) # lower bound of time
        .where(GymOccupancyData.timestamp < today_start + timedelta(days=1)) # upper bound of time
        .group_by("hour")
        .order_by("hour")
    ).all()
    
    last_week_results = db.exec(
        select(
            extract("hour", func.timezone("Asia/Singapore", GymOccupancyData.timestamp)).label("hour"),
            func.avg(GymOccupancyData.occupancy_percentage).label("avg_occupancy")
        )
        .where(GymOccupancyData.facility_id == facility_id)
        .where(GymOccupancyData.timestamp >= last_week_start) # lower bound of time
        .where(GymOccupancyData.timestamp < last_week_start + timedelta(days=1)) # upper bound of time
        .group_by("hour")
        .order_by("hour")
    ).all()
    
    return DayOverDayResponse(
        facility_id = facility_id,
        name = gym.name,
        today_label= today_start.strftime("%a %d %b"),
        last_week_label= last_week_start.strftime("%a %d %b"),
        today= [
            HourlyReading(
                hour= t.hour, occupancy_percentage= t.avg_occupancy,
            )
            for t in today_results
        ],
        last_week=[
            HourlyReading(
                hour = l.hour, occupancy_percentage= l.avg_occupancy
            )
            for l in last_week_results
        ]
    )
    
    
def compare_history(facility_ids: list[str], range: str, db: Session) -> CompareHistoryResponse:
    if len(facility_ids) > 3:
        raise HTTPException(status_code=422, detail="Cannot compare more than 3 gyms at once")
    
    if range not in RANGE_DICT:
        raise HTTPException(status_code=422, detail="Invalid range. Must be 1D, 3D, 7D, 30D")

    delta = RANGE_DICT[range]
    cutoff = datetime.now(timezone.utc) - delta
    
    result = []
    
    for id in facility_ids:
        gym = get_gym_by_id(facility_id = id, db = db)
        gym_history = _query_history(facility_id=id, cutoff=cutoff, db=db)
        result.append(
            GymHistorySeries(
                facility_id=id,
                name=gym.name,
                history=
                [
                    OccupancyRecord(
                        timestamp= gymhistory.timestamp.astimezone(SGT),
                        occupancy_percentage= gymhistory.occupancy_percentage,
                        is_closed=gymhistory.is_closed
                        
                    ) for gymhistory in gym_history
                ]   
            )
        )
    return CompareHistoryResponse(gyms=result)
        

def compare_heatmap(facility_ids: list[str], db:Session) -> CompareHeatmapResponse:
    
    if len(facility_ids) > 3:
        raise HTTPException(status_code=422, detail="Cannot compare more than 3 gyms at once")
    
    result = []
    for id in facility_ids:
        gym = get_gym_by_id(facility_id=id, db=db)
        gym_heatmap = _query_heatmap(facility_id=id, db=db)
        result.append(
            GymHeatmapSeries(
                facility_id=id,
                name = gym.name,
                data = [
                    HeatmapCell(
                        day_of_week=_.day_of_week,
                        hour = _.hour,
                        avg_occupancy= _.avg_occupancy,
                    )
                    for _ in gym_heatmap
                ]
            )
        )
    
    return CompareHeatmapResponse(gyms=result)


# Helper function    
def get_gym_by_id(facility_id:str, db: Session) -> GymMetaData:
    gym = db.exec(select(GymMetaData).where(GymMetaData.facility_id == facility_id)).first()
    if gym is None:
        raise HTTPException(status_code=404, detail="Facility not found")
    return gym
        

def _query_history(facility_id: str, cutoff: datetime, db: Session) -> list[GymOccupancyData]:
    
    results = db.exec(
        select(GymOccupancyData)
        .where(GymOccupancyData.facility_id == facility_id)
        .where(GymOccupancyData.timestamp >= cutoff)
        .order_by(GymOccupancyData.timestamp.asc())
    ).all()
    
    return results
    
def _query_heatmap(facility_id: str, db: Session) -> list[HeatmapRow]:
    results = db.exec(
        select(
            ((extract("dow", func.timezone("Asia/Singapore", GymOccupancyData.timestamp)) + 6) % 7).label("day_of_week"),
            extract("hour", func.timezone("Asia/Singapore", GymOccupancyData.timestamp)).label("hour"),
            func.avg(GymOccupancyData.occupancy_percentage).label("avg_occupancy")
        )
        .where(GymOccupancyData.facility_id == facility_id)
        .group_by("day_of_week", "hour")
        .order_by("day_of_week", "hour")
    ).all()
    
    return results