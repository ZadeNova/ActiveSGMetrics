from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from database import get_session



router = APIRouter()