# For SQL 
# The SQL model for Gymrecords

from sqlmodel import SQLModel, Field, Relationship, Index
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



# Its time to optimize this.
"""
Optimization will be to add an index. SInce this is read heavy , adding an index would be better

EXplanation:
Problem: When the frontend requests a gym history ( give me last 72 hours for yishun ), the DB would normally have to read every single row , filter by ID, and then do an expensive in memory sort by timestamp ( there will be a full table scan )

The solution: Have a composite index , which creates a B-Tree structure sorted FIRST by facility_id, and SECOND by timestamp

THe result:
- Lookups from O(n) to O(log N)
- Database instantly finds the facility and grabs the pre-sorted timestamps
- Query times drop from seconds to miliseconds, saving CPU and RAM

Trade-off:
- SLightly slower inserts ( as the tree must be updated ) and extra disk space used. Given low write volume and high read potential due to the application purpose, this is a reasonable tradeoff.

Let me add it tomorrow, i wanna sleep
"""



class GymOccupancyData(SQLModel, table=True):    
    __tablename__ = "gym_occupancy"
    __table_args__ = (
        Index("ix_gym_occupancy_facility_id_timestamp", "facility_id", "timestamp"),
    )
    
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    facility_id: str = Field(foreign_key="gym_metadata.facility_id", index=True)
    
    occupancy_percentage: int = Field(index=True)
    
    is_closed: bool
    
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), index=True),
        default_factory=lambda: datetime.now(timezone.utc)
    )
    
    gym: Optional[GymMetaData] = Relationship(back_populates="occupancy_records")
    