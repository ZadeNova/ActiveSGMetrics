from sqlalchemy import func, extract
from sqlmodel import select, Session
from models.gym import GymOccupancyData
from schemas.schemas import HeatmapCell, QuietSlot
from datetime import timezone, timedelta

"""
Business Logic: For SQL querying the database.
"""

SGT_OFFSET = 8

def get_heatmap(facility_id: str, db: Session) -> list[HeatmapCell]:
    results = db.exec(
        select(
            
            
            extract("dow", func.timezone("Asia/Singapore", GymOccupancyData.timestamp)).label("day_of_week"),
            extract("hour", func.timezone("Asia/Singapore", GymOccupancyData.timestamp)).label("hour"),
            func.avg(GymOccupancyData.occupancy_percentage).label("avg_occupancy")
        )
        .where(GymOccupancyData.facility_id == facility_id)
        .group_by("day_of_week", "hour")
        .order_by("day_of_week", "hour")
        
        
        
        
    ).all()
    
    
    return [
        HeatmapCell(day_of_week=int(row.day_of_week), hour=int(row.hour), avg_occupancy=row.avg_occupancy)
        for row in results
    ]


def get_best_time(facility_id: str, db: Session, limit: int = 5) -> list[QuietSlot]:
    results = get_heatmap(facility_id=facility_id, db=db)
    # Sorts by the avg_occupancy in ASC order and then slices it by the limit..
    sorted(results, key=lambda x: x.avg_occupancy)[:limit]
    
    return [
        QuietSlot(day_of_week=int(row.day_of_week), hour=int(row.hour), avg_occupancy=row.avg_occupancy)
        for row in results
    ]
    
# write the get_history and get_all_gyms functions
    
    