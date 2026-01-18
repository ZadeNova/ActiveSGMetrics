from fastapi import APIRouter, HTTPException


router = APIRouter()

@router.get("/health")

def health_check():
    "endpoint for health check and to wake up the backend"
    return {"status": "ok"}
