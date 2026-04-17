"""Tests for POST /activities/{activity_name}/signup endpoint"""
import pytest


class TestSignupForActivity:
    """Test suite for signing up for activities"""

    def test_signup_valid_student_returns_200(self, client, valid_activity_name, valid_email):
        """Test: Valid student signup returns 200 OK"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

    def test_signup_adds_student_to_participants(self, client, valid_activity_name, valid_email):
        """Test: Student is added to activity participants after signup"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email in activities[activity_name]["participants"]

    def test_signup_returns_success_message(self, client, valid_activity_name, valid_email):
        """Test: Signup returns confirmation message"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_invalid_activity_returns_404(self, client, invalid_activity_name, valid_email):
        """Test: Signup for non-existent activity returns 404"""
        # Arrange
        activity_name = invalid_activity_name
        email = valid_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

    def test_signup_invalid_activity_returns_error_detail(self, client, invalid_activity_name, valid_email):
        """Test: 404 error includes 'Activity not found' message"""
        # Arrange
        activity_name = invalid_activity_name
        email = valid_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_missing_email_parameter_returns_422(self, client, valid_activity_name):
        """Test: Missing email parameter returns 422 Unprocessable Entity"""
        # Arrange
        activity_name = valid_activity_name

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422

    def test_signup_duplicate_student_returns_400(self, client, valid_activity_name, valid_email):
        """Test: Duplicate signup (same student) returns 400 Bad Request"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email

        # Act - first signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # second signup attempt with same email
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400

    def test_signup_duplicate_returns_error_detail(self, client, valid_activity_name, valid_email):
        """Test: Duplicate signup error includes 'already signed up' message"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_cross_activity_signup_both_succeed(self, client, valid_email):
        """Test: Same student can signup for multiple activities independently"""
        # Arrange
        email = valid_email
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        state = client.get("/activities").json()

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in state[activity1]["participants"]
        assert email in state[activity2]["participants"]

    def test_signup_does_not_remove_existing_participants(self, client, valid_activity_name, valid_email):
        """Test: New signup doesn't affect existing participants"""
        # Arrange
        activity_name = valid_activity_name
        new_email = valid_email
        # Get initial participants
        initial_state = client.get("/activities").json()
        initial_participants = initial_state[activity_name]["participants"].copy()

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        final_state = client.get("/activities").json()
        final_participants = final_state[activity_name]["participants"]

        # Assert
        # All initial participants should still be there
        for participant in initial_participants:
            assert participant in final_participants
        # Plus the new participant
        assert new_email in final_participants
        assert len(final_participants) == len(initial_participants) + 1
