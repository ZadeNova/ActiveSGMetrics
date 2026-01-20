from datetime import datetime, timezone
from sqlalchemy import select
from models import GymMetaData , GymOccupancyData

def ingest_gym_data(payload, db):
    
    batch_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    
    try:
        existing_gym_ids = db.exec(select(GymMetaData.facility_id)).all()
        existing_gym_ids_set = set(existing_gym_ids)
        
        for item in payload:
            # Check the gym metadata table first before uploading the gym occupancy data
            
            
            if item.id not in existing_gym_ids_set:
                # If there is a new gym added, add it to the gym metadata table
                
                new_metadata = GymMetaData(
                    facility_id= item.id,
                    name= item.name,
                    facility_type=item.type
                )
                
                db.add(new_metadata)
                existing_gym_ids_set.add(item.id)
            
            # Start recording the gym occupancy data into the table. INSERT operation
            occupancy_records = [
              GymOccupancyData(
                facility_id= item.id,
                occupancy_percentage= item.capacityPercentage,
                is_closed=item.isClosed,
                timestamp=batch_time
            ) for item in payload
            ]
            
        db.addall(occupancy_records)
            
        db.commit()
        return len(payload)
    except Exception as e:
        print(f"Error occured in ingest_service function: {e}")
        db.rollback()
        raise e
    
    