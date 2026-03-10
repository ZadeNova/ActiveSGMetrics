from typing import List
from pydantic import BaseModel, Field
from datetime import datetime 

# For fastAPI pydantic models



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