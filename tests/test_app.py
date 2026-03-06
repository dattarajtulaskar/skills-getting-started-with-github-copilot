"""
Test suite for Mergington High School Activities API
Uses AAA (Arrange-Act-Assert) pattern for clarity and maintainability
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_200(self, client, reset_activities):
        """
        Arrange: Fresh activities data
        Act: Call GET /activities
        Assert: Response is 200 with all activities
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """
        Arrange: Fresh activities data
        Act: Call GET /activities
        Assert: Each activity has required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success_adds_participant(self, client, reset_activities):
        """
        Arrange: Valid activity and new student email
        Act: Call POST /activities/{activity}/signup
        Assert: Response is 200 and participant is added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    def test_signup_increments_participant_count(self, client, reset_activities):
        """
        Arrange: Chess Club has 2 participants
        Act: Sign up a new student
        Assert: Participant count increments to 3
        """
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        final_count = len(response.json()[activity_name]["participants"])
        
        # Assert
        assert final_count == initial_count + 1
        assert email in response.json()[activity_name]["participants"]
    
    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        Arrange: Student already signed up for Chess Club
        Act: Try to sign up again
        Assert: Response is 400 with error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Activity that doesn't exist
        Act: Try to sign up for invalid activity
        Assert: Response is 404
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_full_activity_returns_400(self, client, reset_activities):
        """
        Arrange: Activity at max capacity
        Act: Try to sign up for full activity
        Assert: Response is 400 with capacity error
        """
        # Arrange  - Tennis Club has max 10, currently has 2
        activity_name = "Tennis Club"
        from src.app import activities
        
        # Fill the activity to max capacity
        activities[activity_name]["participants"] = [
            f"participant{i}@mergington.edu" for i in range(10)
        ]
        
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success_removes_participant(self, client, reset_activities):
        """
        Arrange: Student registered for Chess Club
        Act: Call DELETE /activities/{activity}/unregister
        Assert: Response is 200 and participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert f"Unregistered {email}" in response.json()["message"]
    
    def test_unregister_decrements_participant_count(self, client, reset_activities):
        """
        Arrange: Chess Club has participants
        Act: Unregister a student
        Assert: Participant count decrements
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        response = client.get("/activities")
        final_count = len(response.json()[activity_name]["participants"])
        
        # Assert
        assert final_count == initial_count - 1
        assert email not in response.json()[activity_name]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Activity that doesn't exist
        Act: Try to unregister from invalid activity
        Assert: Response is 404
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_unregistered_student_returns_400(self, client, reset_activities):
        """
        Arrange: Student not registered for Chess Club
        Act: Try to unregister them
        Assert: Response is 400
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
