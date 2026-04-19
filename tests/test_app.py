import pytest
from fastapi.testclient import TestClient
import copy

from src.app import app, activities

# Initial activities data for resetting
INITIAL_ACTIVITIES = {
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
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Art Club": {
        "description": "Explore various art forms and create projects",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in plays and improve theatrical skills",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and learn about science",
        "schedule": "Thursdays, 3:00 PM - 4:30 PM",
        "max_participants": 14,
        "participants": []
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def test_root_redirect(client):
    """Test that GET / redirects to static/index.html"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client):
    """Test GET /activities returns all activities"""
    # Arrange - Activities are reset by fixture
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Signed up {email} for {activity_name}" == data["message"]
    
    # Verify the participant was added
    response = client.get("/activities")
    activities_data = response.json()
    assert email in activities_data[activity_name]["participants"]


def test_signup_duplicate(client):
    """Test that duplicate signup is prevented"""
    # Arrange
    email = "duplicate@mergington.edu"
    activity_name = "Chess Club"
    
    # Act - First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act - Second signup with same email
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" == data["detail"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "NonExistent Club"
    
    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" == data["detail"]


def test_unregister_success(client):
    """Test successful unregister from an activity"""
    # Arrange
    email = "removeme@mergington.edu"
    activity_name = "Basketball Team"
    
    # Act - First add a participant
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act - Then remove them
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Unregistered {email} from {activity_name}" == data["message"]
    
    # Verify they were removed
    response = client.get("/activities")
    activities_data = response.json()
    assert email not in activities_data[activity_name]["participants"]


def test_unregister_participant_not_found(client):
    """Test unregister for participant not in activity"""
    # Arrange
    email = "notenrolled@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" == data["detail"]


def test_unregister_activity_not_found(client):
    """Test unregister for non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "NonExistent Club"
    
    # Act
    response = client.delete(f"/activities/{invalid_activity}/participants/{email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" == data["detail"]