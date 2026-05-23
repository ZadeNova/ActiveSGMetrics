# test_analytics.py

import pytest
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta

from models.gym import GymMetaData, GymOccupancyData
from services import analytics_service

class TestGetHistory:
    # Range validation happens before any DB query, so facility_id doesn't matter here
    def test_raises_422_for_invalid_range(self, db):
        with pytest.raises(HTTPException) as exc_info:
            analytics_service.get_history("ANY_ID", "INVALID", db)
        assert exc_info.value.status_code == 422

    # Valid range but facility doesn't exist — should get 404
    def test_raises_404_for_unknown_facility(self, db):
        with pytest.raises(HTTPException) as exc_info:
            analytics_service.get_history("DOES_NOT_EXIST", "1D", db)
        assert exc_info.value.status_code == 404


class TestGetBestTime:
    def test_quietest_slot_is_first(self, db):
        # Seed a gym with two records at very different occupancy levels
        gym = GymMetaData(facility_id="SORT_TEST", name="Sort Gym", facility_type="Gym")
        db.add(gym)

        now = datetime.now(timezone.utc)
        # 10% occupancy — should be the quietest slot
        db.add(GymOccupancyData(
            facility_id="SORT_TEST",
            occupancy_percentage=10,
            is_closed=False,
            timestamp=now - timedelta(days=2, hours=3)   # different day+hour bucket
        ))
        # 90% occupancy — should be the busiest slot
        db.add(GymOccupancyData(
            facility_id="SORT_TEST",
            occupancy_percentage=90,
            is_closed=False,
            timestamp=now - timedelta(days=3, hours=5)   # different day+hour bucket
        ))
        db.commit()

        result = analytics_service.get_best_time("SORT_TEST", db, limit=5)
        slots = result.quietest_slots

        assert len(slots) >= 1
        # First slot must have the lowest avg_occupancy
        assert slots[0].avg_occupancy <= slots[-1].avg_occupancy


class TestGetAnomaly:
    def test_z_score_is_zero_when_single_data_point(self, db):
        # Seed a gym with exactly one record — stddev will be NULL/None
        # The code should handle this gracefully and return z_score = 0.0
        gym = GymMetaData(facility_id="ANOMALY_TEST", name="Anomaly Gym", facility_type="Gym")
        db.add(gym)
        db.add(GymOccupancyData(
            facility_id="ANOMALY_TEST",
            occupancy_percentage=50,
            is_closed=False,
            timestamp=datetime.now(timezone.utc)
        ))
        db.commit()

        result = analytics_service.get_anomaly("ANOMALY_TEST", db)

        assert result.z_score == 0.0
        assert result.severity == "Normal"
        assert result.is_anomaly is False

    def test_severity_is_normal_when_current_matches_historical(self, db):
        # Seed many records at ~50% so the mean is 50 and stddev is low
        # Then the "current" (most recent) record at 50% should score as Normal
        gym = GymMetaData(facility_id="NORMAL_TEST", name="Normal Gym", facility_type="Gym")
        db.add(gym)

        now = datetime.now(timezone.utc)
        # Seed 10 historical records at consistent 50% occupancy
        # All at the same day-of-week and hour so they land in the same statistical bucket
        for i in range(1, 11):
            db.add(GymOccupancyData(
                facility_id="NORMAL_TEST",
                occupancy_percentage=50,
                is_closed=False,
                timestamp=now - timedelta(weeks=i)  # same DOW and hour as now, n weeks ago
            ))
        # Current reading — also at 50%, right in line with history
        db.add(GymOccupancyData(
            facility_id="NORMAL_TEST",
            occupancy_percentage=50,
            is_closed=False,
            timestamp=now
        ))
        db.commit()

        result = analytics_service.get_anomaly("NORMAL_TEST", db)

        assert result.severity == "Normal"
        assert result.is_anomaly is False


class TestCompareHistory:
    # The 3-gym cap is a business rule — verify it's enforced at the service layer too,
    # not just the HTTP layer
    def test_raises_422_for_more_than_3_gyms(self, db):
        with pytest.raises(HTTPException) as exc_info:
            analytics_service.compare_history(["A", "B", "C", "D"], "7D", db)
        assert exc_info.value.status_code == 422
