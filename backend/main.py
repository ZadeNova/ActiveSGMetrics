from fastapi import FastAPI
from ingest_data import router as data_ingest_router
from sqlmodel import SQLModel



#fastapi dev main.py

app = FastAPI()

app.include_router(data_ingest_router, prefix="/api/v1", tags=["Data_Ingestion"])