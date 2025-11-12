"""
Integration tests for frontend-backend interaction
"""
import pytest


def test_static_files_served(client):
    """Test that static files are properly served"""
    # Test that the main HTML file is accessible
    response = client.get("/static/index.html")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_javascript_file_served(client):
    """Test that JavaScript file is accessible"""
    response = client.get("/static/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers.get("content-type", "") or "text/plain" in response.headers.get("content-type", "")


def test_css_file_served(client):
    """Test that CSS file is accessible"""
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert "css" in response.headers.get("content-type", "") or "text/plain" in response.headers.get("content-type", "")


def test_api_response_format_for_frontend(client):
    """Test that API responses are in the format expected by the frontend"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    
    # Check that each activity has the required fields for frontend
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Check data types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        
        # Check that all participants are strings (emails)
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant  # Basic email validation


def test_signup_response_format(client):
    """Test that signup response format matches frontend expectations"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=frontend@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    required_fields = ["message", "activity", "email", "total_participants"]
    
    for field in required_fields:
        assert field in data
    
    assert isinstance(data["message"], str)
    assert isinstance(data["activity"], str)
    assert isinstance(data["email"], str)
    assert isinstance(data["total_participants"], int)


def test_remove_response_format(client):
    """Test that remove response format matches frontend expectations"""
    # First add a participant
    client.post(
        "/activities/Chess%20Club/signup?email=toremove@mergington.edu"
    )
    
    # Then remove them
    response = client.delete(
        "/activities/Chess%20Club/remove?email=toremove@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    required_fields = ["message", "activity", "email", "total_participants"]
    
    for field in required_fields:
        assert field in data
    
    assert isinstance(data["message"], str)
    assert isinstance(data["activity"], str)
    assert isinstance(data["email"], str)
    assert isinstance(data["total_participants"], int)


def test_error_response_format(client):
    """Test that error responses are properly formatted for frontend handling"""
    # Test 404 error
    response = client.post(
        "/activities/Nonexistent/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)
    
    # Test 400 error
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )  # Already registered
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)


def test_url_encoding_compatibility(client):
    """Test that URL encoding works correctly with frontend requests"""
    # Test activity name with spaces (URL encoded)
    response = client.post(
        "/activities/Programming%20Class/signup?email=urltest@mergington.edu"
    )
    assert response.status_code == 200
    
    # Test email with special characters (URL encoded)
    email = "test%2Btag@mergington.edu"  # URL encoded version of test+tag@mergington.edu
    response = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )
    assert response.status_code == 200
    # FastAPI automatically decodes URL parameters
    assert response.json()["email"] == "test+tag@mergington.edu"


def test_cors_headers_if_needed(client):
    """Test CORS headers if they're configured"""
    response = client.get("/activities")
    # This test will pass regardless of CORS configuration
    # You can add specific CORS assertions if CORS is configured
    assert response.status_code == 200


def test_activity_data_consistency_after_frontend_operations(client):
    """Test data consistency after typical frontend operations"""
    # Simulate a typical frontend workflow
    test_email = "frontend_workflow@mergington.edu"
    activity = "Drama Club"
    
    # 1. Get initial activities (frontend loads data)
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # 2. Sign up for activity (user clicks sign up)
    signup_response = client.post(
        f"/activities/{activity}/signup?email={test_email}"
    )
    assert signup_response.status_code == 200
    
    # 3. Refresh activities list (frontend refreshes after signup)
    refresh_response = client.get("/activities")
    after_signup_count = len(refresh_response.json()[activity]["participants"])
    assert after_signup_count == initial_count + 1
    assert test_email in refresh_response.json()[activity]["participants"]
    
    # 4. Remove participant (user clicks delete button)
    remove_response = client.delete(
        f"/activities/{activity}/remove?email={test_email}"
    )
    assert remove_response.status_code == 200
    
    # 5. Final refresh (frontend refreshes after removal)
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity]["participants"])
    assert final_count == initial_count
    assert test_email not in final_response.json()[activity]["participants"]