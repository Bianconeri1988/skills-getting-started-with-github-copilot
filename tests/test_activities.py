"""Tests for GET /activities endpoint"""
import pytest


class TestGetActivities:
    """Test suite for retrieving all activities"""

    def test_get_activities_returns_200(self, client):
        """Test: GET /activities returns 200 OK status"""
        # Arrange
        # (no setup needed - client fixture is pre-configured)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_nine_activities(self, client):
        """Test: GET /activities returns all 9 activities"""
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert len(activities) == expected_activity_count

    def test_get_activities_returns_correct_activity_names(self, client, sample_activities_list):
        """Test: GET /activities returns all expected activity names"""
        # Arrange
        expected_names = set(sample_activities_list)

        # Act
        response = client.get("/activities")
        activities = response.json()
        actual_names = set(activities.keys())

        # Assert
        assert actual_names == expected_names

    def test_activity_has_required_fields(self, client):
        """Test: Each activity has required fields (description, schedule, max_participants, participants)"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) >= required_fields, \
                f"Activity '{activity_name}' missing required fields"

    def test_participants_is_list(self, client):
        """Test: Participants field is a list"""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Activity '{activity_name}' participants should be a list"

    def test_chess_club_has_initial_participants(self, client):
        """Test: Chess Club has its initial 2 participants"""
        # Arrange
        expected_participants = {"michael@mergington.edu", "daniel@mergington.edu"}

        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_participants = set(activities["Chess Club"]["participants"])

        # Assert
        assert chess_participants == expected_participants
