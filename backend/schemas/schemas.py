from typing import List
from pydantic import BaseModel, Field
from datetime import datetime 

# For fastAPI pydantic models
"""
Request/response pydantic models shared between layers.
"""


class GymData(BaseModel):
    id: str
    name: str
    capacityPercentage: int = Field(..., ge=0, le=100)
    type: str
    isClosed: bool

class Gym_Data_From_Scraper(BaseModel):
    gym: List[GymData]

# Also for my backend to have a strict contract with the frontend. 
# New Schemas for outgoing API responses

"""
Do not return the raw database model, instead define new 'contracts' for the frontend to receive.
"""

class GymResponse(BaseModel):
    """Schema for returning a list of available gyms"""
    facility_id: str
    name: str
    facility_type: str


# For /gyms/{facility_id}/history
class OccupancyRecord(BaseModel):
    """Schema for returning a single point in time for a gym"""
    timestamp: datetime
    occupancy_percentage: int
    is_closed: bool

class OccupancyHistoryResponse(BaseModel):
    """Schema for returning the historical trend of a specific gym"""
    facility_id: str
    name: str
    history: List[OccupancyRecord]
    
# New - for /gyms/{facility_id}/heatmap
class HeatmapCell(BaseModel):
    day_of_week: int   # 0 = Monday, 6 = Sunday ( the DAY - 1)
    hour: int
    avg_occupancy: float
    
class HeatmapResponse(BaseModel):
    facility_id: str
    name: str
    data: List[HeatmapCell]

# for /gyms/{facility_id}/best-time
class QuietSlot(BaseModel):
    day_of_week: int
    hour: int
    avg_occupancy: float
    
class BestTimeResponse(BaseModel):
    facility_id: str
    name: str
    quietest_slots: List[QuietSlot]  # top N, sorted ascending by the avg_occupancy 
    
    
class AnomalyResponse(BaseModel):
    facility_id: str
    name: str
    is_anomaly: bool
    current_occupancy: int
    historical_mean: float
    z_score: float
    severity: str
    timestamp: datetime
    day_of_week: int
    hour: int
    
class HourlyReading(BaseModel):
    """A single hour's average occupancy used in day over day comparison"""
    hour: int
    occupancy_percentage: float
    
class DayOverDayResponse(BaseModel):
    """Compares today's hourly occupancy against the same day last week"""
    facility_id: str
    name: str
    today_label: str
    last_week_label: str
    today: list[HourlyReading]
    last_week: list[HourlyReading]
        
