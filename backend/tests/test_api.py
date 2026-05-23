# test_api.py

class TestHealth:
    # Simplest possible test — confirms the app boots and DB is reachable
    def test_health_returns_ok(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestGetGyms:
    # No gym fixture = empty DB, should still return 200 with empty list
    def test_returns_empty_list_when_no_gyms(self, client):
        response = client.get("/api/v1/gyms")
        assert response.status_code == 200
        assert response.json() == []

    # gym fixture seeds one gym — verify it appears in the response
    def test_returns_gym_when_exists(self, client, gym):
        response = client.get("/api/v1/gyms")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["facility_id"] == "GYM_001"
        assert data[0]["name"] == "Test Gym"


class TestGetHistory:
    # Happy path — valid gym, valid range
    def test_returns_history_for_valid_gym(self, client, occupancy_records):
        response = client.get("/api/v1/gyms/GYM_001/history?range=30D")
        assert response.status_code == 200
        data = response.json()
        assert data["facility_id"] == "GYM_001"
        # We seeded 10 records within 30D, all should be returned
        assert len(data["history"]) == 10

    # Unknown gym — should get 404, not 500
    def test_returns_404_for_unknown_facility(self, client):
        response = client.get("/api/v1/gyms/DOES_NOT_EXIST/history")
        assert response.status_code == 404

    # Invalid range string — should get 422 Unprocessable Entity
    def test_returns_422_for_invalid_range(self, client, gym):
        response = client.get("/api/v1/gyms/GYM_001/history?range=INVALID")
        assert response.status_code == 422

    # Default range is 1D — no query param needed
    def test_default_range_is_1D(self, client, gym):
        response = client.get("/api/v1/gyms/GYM_001/history")
        assert response.status_code == 200


class TestGetHeatmap:
    def test_returns_heatmap_for_valid_gym(self, client, occupancy_records):
        response = client.get("/api/v1/gyms/GYM_001/heatmap")
        assert response.status_code == 200
        data = response.json()
        assert data["facility_id"] == "GYM_001"
        # After — validates data exists without assuming exact slot count
        assert len(data["data"]) >= 1

    def test_returns_404_for_unknown_facility(self, client):
        response = client.get("/api/v1/gyms/DOES_NOT_EXIST/heatmap")
        assert response.status_code == 404


class TestGetBestTime:
    def test_returns_slots_for_valid_gym(self, client, occupancy_records):
        response = client.get("/api/v1/gyms/GYM_001/best-time")
        assert response.status_code == 200
        data = response.json()
        assert "quietest_slots" in data
        # Default limit is 5 but we only have 2 distinct slots
        assert len(data["quietest_slots"]) >= 1
        # Ensure that the quietest comes first.        
        assert data["quietest_slots"][0]["avg_occupancy"] <= data["quietest_slots"][-1]["avg_occupancy"]


    def test_returns_404_for_unknown_facility(self, client):
        response = client.get("/api/v1/gyms/DOES_NOT_EXIST/best-time")
        assert response.status_code == 404


class TestGetAnomaly:
    def test_returns_anomaly_response_for_valid_gym(self, client, occupancy_records):
        response = client.get("/api/v1/gyms/GYM_001/anomaly")
        assert response.status_code == 200
        data = response.json()
        # Verify the shape — all these fields must be present
        assert "z_score" in data
        assert "severity" in data
        assert "current_occupancy" in data
        assert "is_anomaly" in data

    def test_returns_404_for_unknown_facility(self, client):
        response = client.get("/api/v1/gyms/DOES_NOT_EXIST/anomaly")
        assert response.status_code == 404


class TestGetDayOverDay:
    def test_returns_day_over_day_for_valid_gym(self, client, occupancy_records):
        response = client.get("/api/v1/gyms/GYM_001/day-over-day")
        assert response.status_code == 200
        data = response.json()
        assert "today" in data
        assert "last_week" in data
        assert "today_label" in data


class TestCompare:
    # Business rule: max 3 gyms. 4 should fail.
    def test_compare_history_rejects_more_than_3_gyms(self, client, gym):
        response = client.get("/api/v1/gyms/compare/history?ids=A,B,C,D&range=7D")
        assert response.status_code == 422

    def test_compare_history_rejects_invalid_range(self, client, gym):
        response = client.get("/api/v1/gyms/compare/history?ids=GYM_001&range=INVALID")
        assert response.status_code == 422

    def test_compare_heatmap_rejects_more_than_3_gyms(self, client, gym):
        response = client.get("/api/v1/gyms/compare/heatmap?ids=A,B,C,D")
        assert response.status_code == 422


