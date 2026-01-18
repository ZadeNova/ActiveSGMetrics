from datetime import datetime, timezone
from sqlalchemy import select
from models import GymMetaData , GymOccupancyData

def ingest_gym_data(payload, db):
    
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
        return len(payload)
    except Exception as e:
        print(f"Error occured in ingest_service function: {e}")
        db.rollback()
    
    