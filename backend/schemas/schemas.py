from typing import List
from pydantic import BaseModel, Field

# For fastAPI pydantic models


class GymData(BaseModel):
    id: str
    name: str
    capacityPercentage: int = Field(..., ge=0, le=100)
    type: str
    isClosed: bool

class Gym_Data_From_Scraper(BaseModel):
    gym: List[GymData]
