"""
Tests for edge cases and error handling
"""
import pytest
from urllib.parse import quote


def test_special_characters_in_email(client):
    """Test handling emails with special characters"""
    special_emails = [
        "test.user+tag@mergington.edu",
        "test-user@sub.mergington.edu",
        "test_user@mergington.edu"
    ]
    
    for email in special_emails:
        response = client.post(
            f"/activities/Chess%20Club/signup?email={quote(email)}"
        )
        assert response.status_code == 200
        assert response.json()["email"] == email


def test_special_characters_in_activity_name(client):
    """Test handling activity names with special characters"""
    # Since we're using URL encoding, test with encoded characters
    response = client.post(
        "/activities/Chess%20Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200


def test_empty_email(client):
    """Test signup with empty email"""
    response = client.post("/activities/Chess%20Club/signup?email=")
    # FastAPI should handle this gracefully
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == ""


def test_malformed_requests(client):
    """Test various malformed requests"""
    # Missing email parameter
    response = client.post("/activities/Chess%20Club/signup")
    assert response.status_code == 422  # Unprocessable Entity
    
    # Missing email parameter for remove
    response = client.delete("/activities/Chess%20Club/remove")
    assert response.status_code == 422  # Unprocessable Entity


def test_case_sensitive_activity_names(client):
    """Test that activity names are case-sensitive"""
    response = client.post(
        "/activities/chess%20club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_concurrent_signups(client):
    """Test multiple signups happening simultaneously"""
    # Simulate concurrent signups by rapidly signing up multiple students
    emails = [f"student{i}@mergington.edu" for i in range(5)]
    
    responses = []
    for email in emails:
        response = client.post(
            f"/activities/Gym%20Class/signup?email={email}"
        )
        responses.append(response)
    
    # All should succeed since Gym Class has 30 max participants
    for response in responses:
        assert response.status_code == 200
    
    # Verify all students were added
    activities_response = client.get("/activities")
    gym_participants = activities_response.json()["Gym Class"]["participants"]
    
    for email in emails:
        assert email in gym_participants


def test_activity_capacity_edge_cases(client):
    """Test edge cases around activity capacity"""
    # Test an activity with very low capacity
    activity = "Science Olympiad"  # Has max 14 participants, currently 2
    
    # Fill it to exactly max capacity
    for i in range(12):  # 14 - 2 current = 12 more needed
        response = client.post(
            f"/activities/{activity}/signup?email=student{i}@mergington.edu"
        )
        assert response.status_code == 200
    
    # Verify it's exactly at capacity
    check_response = client.get("/activities")
    participants = check_response.json()[activity]["participants"]
    assert len(participants) == 14
    
    # Try to add one more (should fail)
    response = client.post(
        f"/activities/{activity}/signup?email=overflow@mergington.edu"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_remove_and_re_add_participant(client):
    """Test removing a participant and then adding them back"""
    email = "flipflop@mergington.edu"
    activity = "Art Club"
    
    # Add participant
    add_response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert add_response.status_code == 200
    
    # Remove participant
    remove_response = client.delete(
        f"/activities/{activity}/remove?email={email}"
    )
    assert remove_response.status_code == 200
    
    # Add them back
    re_add_response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert re_add_response.status_code == 200
    
    # Verify they're in the activity
    final_response = client.get("/activities")
    participants = final_response.json()[activity]["participants"]
    assert email in participants


def test_data_consistency_after_operations(client):
    """Test that data remains consistent after multiple operations"""
    # Get initial state
    initial_response = client.get("/activities")
    initial_data = initial_response.json()
    
    # Perform multiple operations
    test_email = "consistency@mergington.edu"
    
    # Sign up for multiple activities
    for activity_name in ["Chess Club", "Programming Class"]:
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert response.status_code == 200
    
    # Remove from one activity
    response = client.delete(
        f"/activities/Chess%20Club/remove?email={test_email}"
    )
    assert response.status_code == 200
    
    # Check final state
    final_response = client.get("/activities")
    final_data = final_response.json()
    
    # Verify data integrity
    for activity_name, activity_data in final_data.items():
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)
        assert activity_data["max_participants"] == initial_data[activity_name]["max_participants"]
        assert len(activity_data["participants"]) <= activity_data["max_participants"]
    
    # Verify specific changes
    assert test_email not in final_data["Chess Club"]["participants"]
    assert test_email in final_data["Programming Class"]["participants"]