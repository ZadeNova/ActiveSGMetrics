# For SQL 
# The SQL model for Gymrecords

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from typing import Optional, List

class GymMetaData(SQLModel, table=True):
    
    __tablename__ = "gym_metadata"
    facility_id: str = Field(primary_key=True)
    name: str = Field(index=True)
    facility_type: str = Field(default="gym")
    
    # Relationship with GymOccupancyData.
    # One gym has many gym data records.
    occupancy_records: List["GymOccupancyData"] = Relationship(back_populates="gym")


class GymOccupancyData(SQLModel, table=True):    
    __tablename__ = "gym_occupancy"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    facility_id: str = Field(foreign_key="gym_metadata.facility_id", index=True)
    
    occupancy_percentage: int = Field(index=True)
    
    is_closed: bool
    
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), index=True),
        default_factory=lambda: datetime.now(timezone.utc)
    )
    
    gym: Optional[GymMetaData] = Relationship(back_populates="occupancy_records")
    