from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from sqlalchemy import text
from database import get_session

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_session)):
    "endpoint for health check and to verify the DB connection"
    
    try:
        db.exec(text("SELECT 1"))
        return {"status": "ok", "database": "online"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")
    

