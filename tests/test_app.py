import pytest
import json
from datetime import datetime
from app import app, rooms

class TestRoomManagement:
    """Test room creation and management."""
    
    def test_create_room(self, client):
        """Test creating a new room."""
        response = client.post('/rooms', 
                             data=json.dumps({"username": "Alice"}),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'room_code' in data
        assert len(data['room_code']) == 6
        assert data['room']['owner'] == "Alice"
        assert "Alice" in data['room']['members']
    
    def test_get_room(self, client, test_room):
        """Test getting room information."""
        response = client.get(f'/rooms/{test_room}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == test_room
        assert 'members' in data
        assert 'tasks' in data
    
    def test_join_room(self, client, test_room):
        """Test joining an existing room."""
        response = client.post(f'/rooms/{test_room}/join',
                             data=json.dumps({"username": "Bob"}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "Bob" in data['room']['members']

class TestTaskCreation:
    """Test task creation functionality."""
    
    def test_create_task_with_all_fields(self, client, test_room, sample_task):
        """Test creating a task with all fields."""
        sample_task['room_code'] = test_room
        response = client.post(f'/tasks?room={test_room}', 
                             data=json.dumps(sample_task),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Task created successfully'
        assert data['task']['title'] == sample_task['title']
        assert data['task']['description'] == sample_task['description']
        assert data['task']['priority'] == sample_task['priority']
        assert data['task']['completed'] is False
    
    def test_create_task_minimal_fields(self, client, test_room):
        """Test creating a task with minimal fields."""
        task_data = {"title": "Simple Task", "room_code": test_room}
        response = client.post(f'/tasks?room={test_room}',
                             data=json.dumps(task_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['task']['title'] == "Simple Task"
        assert data['task']['priority'] == "medium"
    
    def test_create_task_missing_title(self, client, test_room):
        """Test creating a task without required title."""
        task_data = {"description": "No title", "room_code": test_room}
        response = client.post(f'/tasks?room={test_room}',
                             data=json.dumps(task_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

class TestTaskRetrieval:
    """Test task retrieval functionality."""
    
    def test_get_all_tasks(self, client, test_room):
        """Test getting all tasks in a room."""
        # Create some tasks
        tasks_data = [
            {"title": "Task 1", "room_code": test_room},
            {"title": "Task 2", "room_code": test_room}
        ]
        for task in tasks_data:
            client.post(f'/tasks?room={test_room}',
                       data=json.dumps(task),
                       content_type='application/json')
        
        response = client.get(f'/tasks?room={test_room}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['tasks']) == 2
    
    def test_filter_tasks_by_priority(self, client, test_room):
        """Test filtering tasks by priority."""
        # Create tasks with different priorities
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "High Priority", "priority": "high", "room_code": test_room}),
                   content_type='application/json')
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "Low Priority", "priority": "low", "room_code": test_room}),
                   content_type='application/json')
        
        response = client.get(f'/tasks?room={test_room}&priority=high')
        data = json.loads(response.data)
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['priority'] == 'high'
    
    def test_filter_tasks_by_status(self, client, test_room):
        """Test filtering tasks by completion status."""
        # Create and complete one task
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "Task 1", "room_code": test_room}),
                   content_type='application/json')
        client.post(f'/tasks/1/complete?room={test_room}')
        
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "Task 2", "room_code": test_room}),
                   content_type='application/json')
        
        # Test completed filter
        response = client.get(f'/tasks?room={test_room}&status=completed')
        data = json.loads(response.data)
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['completed'] is True
        
        # Test pending filter
        response = client.get(f'/tasks?room={test_room}&status=pending')
        data = json.loads(response.data)
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['completed'] is False

class TestTaskUpdate:
    """Test task update functionality."""
    
    def test_update_task(self, client, test_room):
        """Test updating a task."""
        # Create a task
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "Original", "room_code": test_room}),
                   content_type='application/json')
        
        # Update the task
        update_data = {"title": "Updated", "priority": "high"}
        response = client.put(f'/tasks/1?room={test_room}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['task']['title'] == "Updated"
        assert data['task']['priority'] == "high"
    
    def test_complete_task(self, client, test_room):
        """Test marking a task as completed."""
        # Create a task
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "To Complete", "room_code": test_room}),
                   content_type='application/json')
        
        # Complete the task
        response = client.post(f'/tasks/1/complete?room={test_room}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['task']['completed'] is True
        assert data['task']['completed_at'] is not None

class TestTaskDeletion:
    """Test task deletion functionality."""
    
    def test_delete_task(self, client, test_room):
        """Test deleting a task."""
        # Create a task
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "To Delete", "room_code": test_room}),
                   content_type='application/json')
        
        # Delete the task
        response = client.delete(f'/tasks/1?room={test_room}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Task deleted successfully'
        
        # Verify task is deleted
        response = client.get(f'/tasks?room={test_room}')
        data = json.loads(response.data)
        assert len(data['tasks']) == 0

class TestStatistics:
    """Test task statistics functionality."""
    
    def test_get_stats(self, client, test_room):
        """Test getting task statistics."""
        # Create some tasks
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "Task 1", "room_code": test_room}),
                   content_type='application/json')
        client.post(f'/tasks?room={test_room}',
                   data=json.dumps({"title": "Task 2", "room_code": test_room}),
                   content_type='application/json')
        
        # Complete one task
        client.post(f'/tasks/1/complete?room={test_room}')
        
        # Get stats
        response = client.get(f'/tasks/stats?room={test_room}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_tasks'] == 2
        assert data['completed_tasks'] == 1
        assert data['pending_tasks'] == 1
        assert data['completion_rate'] == 50.0

class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

class TestErrorHandling:
    """Test error handling."""
    
    def test_room_not_found(self, client):
        """Test error when room doesn't exist."""
        response = client.get('/tasks?room=INVALID')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_task_not_found(self, client, test_room):
        """Test error when task doesn't exist."""
        response = client.get(f'/tasks/999?room={test_room}')
        
        # This should return 404 for non-existent task operations
        # Note: Current implementation doesn't have GET /tasks/<id>, so this tests update/delete
        response = client.put(f'/tasks/999?room={test_room}',
                            data=json.dumps({"title": "Update"}),
                            content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data