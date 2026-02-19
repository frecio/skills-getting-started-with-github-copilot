"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Test cases for the activities endpoints"""

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "test@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]

    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant to the activity"""
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])

        # Sign up a new participant
        client.post(
            "/activities/Programming Class/signup?email=newstudent@mergington.edu"
        )

        # Check that participant was added
        response = client.get("/activities")
        new_count = len(response.json()["Programming Class"]["participants"])
        assert new_count == initial_count + 1
        assert "newstudent@mergington.edu" in response.json()[
            "Programming Class"
        ]["participants"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_from_activity(self):
        """Test unregistering from an activity"""
        # First, sign up
        client.post(
            "/activities/Gym Class/signup?email=unreg@mergington.edu"
        )

        # Then unregister
        response = client.delete(
            "/activities/Gym Class/unregister?email=unreg@mergington.edu"
        )
        assert response.status_code == 200
        result = response.json()
        assert "unreg@mergington.edu" in result["message"]
        assert "Unregistered" in result["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        # Sign up
        client.post(
            "/activities/Chess Club/signup?email=tempstudent@mergington.edu"
        )

        # Get count after signup
        response = client.get("/activities")
        count_after_signup = len(response.json()["Chess Club"]["participants"])

        # Unregister
        client.delete(
            "/activities/Chess Club/unregister?email=tempstudent@mergington.edu"
        )

        # Check count after unregister
        response = client.get("/activities")
        count_after_unregister = len(response.json()["Chess Club"]["participants"])
        assert count_after_unregister == count_after_signup - 1
        assert "tempstudent@mergington.edu" not in response.json()[
            "Chess Club"
        ]["participants"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Fake Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant who isn't registered"""
        response = client.delete(
            "/activities/Gym Class/unregister?email=nobody@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Participant not found" in result["detail"]

    def test_root_redirect(self):
        """Test that root path redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
