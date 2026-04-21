import os
from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool
from config import settings



DATABASE_URL = settings.SUPABASE_DATABASE_URL


# Nullpull forces a fresh new connection to supabase for every new request.

engine = create_engine(DATABASE_URL, poolclass=NullPool, connect_args={"connect_timeout":30}, pool_pre_ping=True, pool_recycle=300)

"""Gives u a sesssion for supabase"""
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        
        session.close()