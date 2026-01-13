from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List


# Pydantic Model
class GymData(BaseModel):
    id: str
    name: str
    capacityPercentage: int = Field(..., ge=0, le=100)
    type: str
    isClosed: bool

class Gym_Data_From_Scraper(BaseModel):
    gym: List[GymData]


app = FastAPI()


@app.post("/api/v1/ingestdata")
def ingest_data():
    pass