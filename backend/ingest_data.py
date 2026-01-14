from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel, Field
from typing import List
from models.gym import GymMetaData, GymOccupancyData
from sqlmodel import Session, select
from database import get_session
from datetime import datetime, timezone


# Pydantic Model
# Create a new file for this too
class GymData(BaseModel):
    id: str
    name: str
    capacityPercentage: int = Field(..., ge=0, le=100)
    type: str
    isClosed: bool

class Gym_Data_From_Scraper(BaseModel):
    gym: List[GymData]


router = APIRouter()


@router.get("/")
def home():
    return {"message": "hello world"}
    

@router.post("/ingestdata", status_code=status.HTTP_201_CREATED)
async def ingest_data(
    payload: List[GymData],
    db: Session = Depends(get_session)
):
    print(f"DEBUG: Received {len(payload)} gym")
    
    batch_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    
    try:
        for item in payload:
            # Check the gym metadata table first before uploading the gym occupancy data
            does_gym_exist = db.exec(
                select(GymMetaData).where(GymMetaData.facility_id == item.id)
            ).first()
            
            if not does_gym_exist:
                # If there is a new gym added, add it to the gym metadata table
                
                new_metadata = GymMetaData(
                    facility_id= item.id,
                    name= item.name,
                    facility_type=item.type
                )
                db.add(new_metadata)
            
            # Start recording the gym occupancy data into the table. INSERT operation
            occupancy_record = GymOccupancyData(
                facility_id= item.id,
                occupancy_percentage= item.capacityPercentage,
                is_closed=item.isClosed,
                timestamp=batch_time
            )
            db.add(occupancy_record)
            
        db.commit()
            
        return {
                "status" : "success",
                "message": f"Successfully processed {len(payload)} gyms"
            }
            
            
    except Exception as e:
        # THis function will undo the entire batch if there is anything wrong. 
        # THis follows the ACID principle, where I will not end up with half finished data
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    
    