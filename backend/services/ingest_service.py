from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from models import GymMetaData , GymOccupancyData

def ingest_gym_data(payload, db):
    
    batch_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    
    try:
        
                
        if payload:
            metadata_list = [
                {"facility_id": item.id, "name": item.name, "facility_type": item.type}
                for item in payload
            ]        
        
            stmt = insert(GymMetaData).values(metadata_list)
            upsert_stmt = stmt.on_conflict_do_nothing(index_elements=["facility_id"])
            db.exec(upsert_stmt)
        
        
            # Check the gym metadata table first before uploading the gym occupancy data
            

                
        occupancy_records = [
            
            GymOccupancyData(
                facility_id=item.id,
                occupancy_percentage=item.capacityPercentage,
                is_closed=item.isClosed,
                timestamp=batch_time
            ) for item in payload
        ]
            
        
        
        db.add_all(occupancy_records)
        
        db.commit()
        return len(payload)
    except Exception as e:
        print(f"Error occured in ingest_service function: {e}")
        db.rollback()
        raise e
    
    