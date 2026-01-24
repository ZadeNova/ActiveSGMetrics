import os
from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv


load_dotenv()

# Need to manually change it to SUPABASE_DEV_DATABASE_URL if testing in local
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
#DATABASE_URL = os.getenv("SUPABASE_DEV_DATABASE_URL")

# Nullpull forces a fresh new connection to supabase for every new request.

engine = create_engine(DATABASE_URL, poolclass=NullPool, connect_args={"connect_timeout":10})

"""Gives u a sesssion for supabase"""
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        
        session.close()