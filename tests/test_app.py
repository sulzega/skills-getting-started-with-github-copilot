"""
Tests for the main application endpoints
"""
import pytest


def test_root_redirect(client):
    """Test that root endpoint redirects to static HTML"""
    response = client.get("/")
    assert response.status_code == 200
    # Check if it's a redirect response
    assert response.url.path.endswith("/static/index.html")


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    
    # Check structure of an activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Successfully signed up for Chess Club"
    assert data["activity"] == "Chess Club"
    assert data["email"] == "test@mergington.edu"
    assert data["total_participants"] == 3  # Original 2 + 1 new


def test_signup_nonexistent_activity(client):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_duplicate_participant(client):
    """Test signing up a participant who is already registered"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_signup_activity_full(client):
    """Test signup when activity is at max capacity"""
    # First fill up the Chess Club (max 12 participants, already has 2)
    for i in range(10):  # Add 10 more to reach the limit
        response = client.post(
            f"/activities/Chess%20Club/signup?email=student{i}@mergington.edu"
        )
        assert response.status_code == 200
    
    # Try to add one more (should fail)
    response = client.post(
        "/activities/Chess%20Club/signup?email=overflow@mergington.edu"
    )
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"] == "Activity is full"


def test_remove_participant_success(client):
    """Test successfully removing a participant from an activity"""
    response = client.delete(
        "/activities/Chess%20Club/remove?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Successfully removed from Chess Club"
    assert data["activity"] == "Chess Club"
    assert data["email"] == "michael@mergington.edu"
    assert data["total_participants"] == 1  # Original 2 - 1 removed


def test_remove_participant_nonexistent_activity(client):
    """Test removing participant from non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent%20Club/remove?email=test@mergington.edu"
    )
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_remove_participant_not_registered(client):
    """Test removing a participant who is not registered for the activity"""
    response = client.delete(
        "/activities/Chess%20Club/remove?email=notregistered@mergington.edu"
    )
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "Student not found in this activity"


def test_signup_and_remove_workflow(client):
    """Test a complete workflow of signing up and then removing a participant"""
    email = "workflow@mergington.edu"
    activity = "Programming Class"
    
    # Get initial participant count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert signup_response.status_code == 200
    assert signup_response.json()["total_participants"] == initial_count + 1
    
    # Verify participant was added
    check_response = client.get("/activities")
    participants = check_response.json()[activity]["participants"]
    assert email in participants
    assert len(participants) == initial_count + 1
    
    # Remove participant
    remove_response = client.delete(
        f"/activities/{activity}/remove?email={email}"
    )
    assert remove_response.status_code == 200
    assert remove_response.json()["total_participants"] == initial_count
    
    # Verify participant was removed
    final_response = client.get("/activities")
    final_participants = final_response.json()[activity]["participants"]
    assert email not in final_participants
    assert len(final_participants) == initial_count


def test_multiple_activities_signup(client):
    """Test that a student can sign up for multiple activities"""
    email = "multisport@mergington.edu"
    
    # Sign up for multiple activities
    activities_to_join = ["Chess Club", "Programming Class", "Art Club"]
    
    for activity in activities_to_join:
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        assert response.json()["email"] == email
    
    # Verify the student is in all activities
    all_activities_response = client.get("/activities")
    all_activities = all_activities_response.json()
    
    for activity in activities_to_join:
        assert email in all_activities[activity]["participants"]