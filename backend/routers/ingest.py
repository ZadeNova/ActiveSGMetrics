from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from schemas import Gym_Data_From_Scraper, GymData
from database import get_session
from sqlmodel import Session

