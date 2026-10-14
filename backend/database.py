from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool
from config import settings



DATABASE_URL = settings.DATABASE_URL


# NullPool forces a fresh new connection to the database for every new request.

engine = create_engine(DATABASE_URL, poolclass=NullPool, connect_args={"connect_timeout":30}, pool_pre_ping=True, pool_recycle=300)

"""Gives a session for the database"""
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.rollback()
        session.close()