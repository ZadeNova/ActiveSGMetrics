from fastapi import FastAPI
from routers import ingest, data, health
from sqlmodel import SQLModel



#fastapi dev main.py

app = FastAPI()

#app.include_router(data_ingest_router, prefix="/api/v1", tags=["Data_Ingestion"])
app.include_router(ingest.router, prefix="/api/v1", tags=["Ingest_Data"])
app.include_router(data.router, prefix="/api/v1", tags=["Data"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])