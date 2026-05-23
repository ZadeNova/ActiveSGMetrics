import os
import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://user:password@localhost:5433/activesg_test_db")

# Set env vars BEFORE importing app — config.py creates Settings() at module level,
# so these must exist in the environment at import time
os.environ.setdefault("SUPABASE_DATABASE_URL", TEST_DATABASE_URL)
os.environ.setdefault("ACTIVE_SG_API", "http://test-placeholder")

from main import app
from database import get_session
from models.gym import GymMetaData, GymOccupancyData

from sqlmodel import delete

from sqlmodel import delete

# autouse=True — runs automatically after every single test, no need to request it explicitly.
# Deletes all rows in dependency order (child table first, then parent)
# so foreign key constraints don't block the delete.
@pytest.fixture(autouse=True)
def clean_tables(test_engine):
    yield   # run the test first
    with Session(test_engine) as cleanup_session:
        cleanup_session.exec(delete(GymOccupancyData))
        cleanup_session.exec(delete(GymMetaData))
        cleanup_session.commit()


# RUns only once. 
# Creates tables and drops them once.
@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    
    
@pytest.fixture()
def db(test_engine):
    with Session(test_engine) as session:
        yield session
        session.rollback()
    

@pytest.fixture
def client(db):
    def override_get_session():
        yield db

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def gym(db):
    g = GymMetaData(facility_id="GYM_001", name="Test Gym", facility_type="Gym")
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@pytest.fixture
def occupancy_records(db, gym):
    now = datetime.now(timezone.utc)
    records = []

    # Seed records spread across the past 4 weeks so they fall within 30D range
    offsets_days = [1, 3, 8, 10, 15, 17, 22, 24, 27, 29]
    occupancies = [30, 80, 30, 80, 30, 80, 30, 80, 30, 80]

    for days_ago, pct in zip(offsets_days, occupancies):
        records.append(GymOccupancyData(
            facility_id="GYM_001",
            occupancy_percentage=pct,
            is_closed=False,
            timestamp=now - timedelta(days=days_ago)
        ))

    for r in records:
        db.add(r)
    db.commit()
    return records


