"""
Tests for the Mergington High School API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original data
    original_activities = {
        "Soccer Team": {
            "description": "Join our competitive soccer team and participate in inter-school matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and compete in tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "emily@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["lily@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and musicals, develop acting and stage skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "william@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and conduct exciting experiments",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        assert "Programming Class" in data
    
    def test_activities_have_correct_structure(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
            assert isinstance(activity["max_participants"], int)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """Test successful signup for a new student"""
        response = client.post(
            "/activities/Soccer%20Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Soccer Team" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_duplicate_student_fails(self, client):
        """Test that signing up the same student twice fails"""
        email = "alex@mergington.edu"  # Already in Soccer Team
        response = client.post(
            f"/activities/Soccer%20Team/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_multiple_different_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for Soccer Team
        response1 = client.post(
            f"/activities/Soccer%20Team/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Basketball Club
        response2 = client.post(
            f"/activities/Basketball%20Club/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Soccer Team"]["participants"]
        assert email in activities_data["Basketball Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student_success(self, client):
        """Test successful unregistration of an existing student"""
        email = "alex@mergington.edu"  # Already in Soccer Team
        response = client.delete(
            f"/activities/Soccer%20Team/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Soccer Team" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Soccer Team"]["participants"]
    
    def test_unregister_non_registered_student_fails(self, client):
        """Test that unregistering a student not in the activity fails"""
        email = "notregistered@mergington.edu"
        response = client.delete(
            f"/activities/Soccer%20Team/unregister?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from a non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_then_unregister_then_signup_again(self, client):
        """Test the full cycle: signup, unregister, signup again"""
        email = "cycletest@mergington.edu"
        activity = "Chess Club"
        
        # Initial signup
        response1 = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Signup again
        response3 = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert response3.status_code == 200
        
        # Verify final state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]


class TestActivityCapacity:
    """Tests for activity capacity limits"""
    
    def test_activity_tracks_participants_correctly(self, client):
        """Test that participant count is tracked correctly"""
        response = client.get("/activities")
        data = response.json()
        
        soccer_team = data["Soccer Team"]
        initial_count = len(soccer_team["participants"])
        max_participants = soccer_team["max_participants"]
        
        # Verify spots calculation would be correct
        spots_left = max_participants - initial_count
        assert spots_left > 0
        assert initial_count == 2  # alex and sarah


class TestDataPersistence:
    """Tests for data persistence within a session"""
    
    def test_changes_persist_across_requests(self, client):
        """Test that changes persist across multiple requests"""
        email = "persistent@mergington.edu"
        
        # Add student
        client.post(f"/activities/Art%20Studio/signup?email={email}")
        
        # Make another request and verify student is still there
        response = client.get("/activities")
        data = response.json()
        assert email in data["Art Studio"]["participants"]
        
        # Remove student
        client.delete(f"/activities/Art%20Studio/unregister?email={email}")
        
        # Verify student is gone
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Art Studio"]["participants"]
