import pytest
import json
from app import app, rooms

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "due_date": "2025-12-31 23:59:59"
    }

@pytest.fixture
def sample_tasks():
    """Create multiple sample tasks for testing."""
    return [
        {
            "title": "High Priority Task",
            "description": "Urgent task",
            "priority": "high",
            "due_date": "2025-12-31 23:59:59"
        },
        {
            "title": "Medium Priority Task",
            "description": "Normal task",
            "priority": "medium",
            "due_date": "2025-12-30 12:00:00"
        },
        {
            "title": "Low Priority Task",
            "description": "Low priority task",
            "priority": "low"
        }
    ]

@pytest.fixture
def test_room(client):
    """Create a test room for testing."""
    response = client.post('/rooms', json={"username": "testuser"})
    return response.json['room_code']

@pytest.fixture(autouse=True)
def reset_rooms():
    """Reset the rooms dict before each test."""
    rooms.clear()
    yield
    rooms.clear()
