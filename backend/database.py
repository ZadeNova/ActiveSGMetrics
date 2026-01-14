import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

"""Gives u a sesssion for supabase"""
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        
        session.close()