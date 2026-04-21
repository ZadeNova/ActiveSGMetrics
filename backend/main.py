from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingest, data, health
from sqlmodel import SQLModel
from config import settings


#fastapi dev main.py

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,   # Change this to production URL
    allow_credentials=True,
    allow_methods=["*"], # Allow all request methods
    allow_headers=["*"],  # Allow all headers
)



app.include_router(data.router, prefix="/api/v1", tags=["Data"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])