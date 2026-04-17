"""Tests for DELETE /activities/{activity_name}/signup endpoint"""
import pytest


class TestUnregisterFromActivity:
    """Test suite for unregistering from activities"""

    def test_unregister_existing_participant_returns_200(self, client, valid_activity_name, valid_email):
        """Test: Unregistering existing participant returns 200 OK"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email
        # First signup the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200

    def test_unregister_removes_participant_from_list(self, client, valid_activity_name, valid_email):
        """Test: Participant is removed from activity after unregister"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email
        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_unregister_returns_success_message(self, client, valid_activity_name, valid_email):
        """Test: Unregister returns confirmation message"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_invalid_activity_returns_404(self, client, invalid_activity_name, valid_email):
        """Test: Unregister from non-existent activity returns 404"""
        # Arrange
        activity_name = invalid_activity_name
        email = valid_email

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_invalid_activity_returns_error_detail(self, client, invalid_activity_name, valid_email):
        """Test: 404 error includes 'Activity not found' message"""
        # Arrange
        activity_name = invalid_activity_name
        email = valid_email

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_missing_email_parameter_returns_422(self, client, valid_activity_name):
        """Test: Missing email parameter returns 422 Unprocessable Entity"""
        # Arrange
        activity_name = valid_activity_name

        # Act
        response = client.delete(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422

    def test_unregister_non_participant_returns_404(self, client, valid_activity_name, valid_email):
        """Test: Unregister student who never signed up returns 404"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email
        # Note: not signing up - so email is not a participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_non_participant_returns_error_detail(self, client, valid_activity_name, valid_email):
        """Test: Non-participant unregister error includes 'Participant not found' message"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_unregister_does_not_affect_other_participants(self, client, valid_activity_name):
        """Test: Unregistering one participant doesn't affect others"""
        # Arrange
        activity_name = valid_activity_name
        email1 = "newstudent1@mergington.edu"
        email2 = "newstudent2@mergington.edu"
        # Sign up both students
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Act
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email1 not in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_unregister_then_re_signup_succeeds(self, client, valid_activity_name, valid_email):
        """Test: Student can re-signup after unregistering"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email
        # Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        # Unregister
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        state = client.get("/activities").json()

        # Assert
        assert response.status_code == 200
        assert email in state[activity_name]["participants"]

    def test_unregister_already_unregistered_returns_404(self, client, valid_activity_name, valid_email):
        """Test: Double unregister (already unregistered) returns 404"""
        # Arrange
        activity_name = valid_activity_name
        email = valid_email
        # Sign up then unregister
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
