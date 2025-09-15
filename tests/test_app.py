import pytest
import json
from datetime import datetime
from app import app, tasks

class TestTaskCreation:
    """Test task creation functionality."""
    
    def test_create_task_with_all_fields(self, client, sample_task):
        """Test creating a task with all fields."""
        response = client.post('/tasks', 
                             data=json.dumps(sample_task),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Task created successfully'
        assert data['task']['title'] == sample_task['title']
        assert data['task']['description'] == sample_task['description']
        assert data['task']['priority'] == sample_task['priority']
        assert data['task']['due_date'] == sample_task['due_date']
        assert data['task']['completed'] is False
        assert data['task']['completed_at'] is None
        assert data['task']['created_at'] is not None
        assert data['task']['id'] == 1

    def test_create_task_with_minimal_fields(self, client):
        """Test creating a task with only required fields."""
        task_data = {"title": "Simple Task"}
        response = client.post('/tasks',
                             data=json.dumps(task_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['task']['title'] == "Simple Task"
        assert data['task']['description'] == ""
        assert data['task']['priority'] == "medium"  # default
        assert data['task']['due_date'] is None
        assert data['task']['completed'] is False

    def test_create_task_missing_title(self, client):
        """Test creating a task without required title."""
        task_data = {"description": "No title task"}
        response = client.post('/tasks',
                             data=json.dumps(task_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Missing task title'

    def test_create_task_invalid_due_date_format(self, client):
        """Test creating a task with invalid due date format."""
        task_data = {
            "title": "Test Task",
            "due_date": "invalid-date"
        }
        response = client.post('/tasks',
                             data=json.dumps(task_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid due_date format' in data['error']

    def test_create_task_with_different_priorities(self, client):
        """Test creating tasks with different priority levels."""
        priorities = ['high', 'medium', 'low']
        
        for priority in priorities:
            task_data = {
                "title": f"Task with {priority} priority",
                "priority": priority
            }
            response = client.post('/tasks',
                                 data=json.dumps(task_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['task']['priority'] == priority

class TestTaskRetrieval:
    """Test task retrieval functionality."""
    
    def test_get_all_tasks_empty(self, client):
        """Test getting all tasks when none exist."""
        response = client.get('/tasks')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['tasks'] == []
        assert data['total'] == 0
        assert data['total_all'] == 0

    def test_get_all_tasks_with_data(self, client, sample_tasks):
        """Test getting all tasks when tasks exist."""
        # Create tasks
        for task_data in sample_tasks:
            client.post('/tasks',
                       data=json.dumps(task_data),
                       content_type='application/json')
        
        response = client.get('/tasks')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['tasks']) == 3
        assert data['total'] == 3
        assert data['total_all'] == 3

    def test_get_tasks_filter_by_status_completed(self, client, sample_tasks):
        """Test filtering tasks by completed status."""
        # Create tasks
        for task_data in sample_tasks:
            client.post('/tasks',
                       data=json.dumps(task_data),
                       content_type='application/json')
        
        # Complete first task
        client.post('/tasks/1/complete')
        
        response = client.get('/tasks?status=completed')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['completed'] is True

    def test_get_tasks_filter_by_status_pending(self, client, sample_tasks):
        """Test filtering tasks by pending status."""
        # Create tasks
        for task_data in sample_tasks:
            client.post('/tasks',
                       data=json.dumps(task_data),
                       content_type='application/json')
        
        # Complete first task
        client.post('/tasks/1/complete')
        
        response = client.get('/tasks?status=pending')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['tasks']) == 2
        for task in data['tasks']:
            assert task['completed'] is False

    def test_get_tasks_filter_by_priority(self, client, sample_tasks):
        """Test filtering tasks by priority."""
        # Create tasks
        for task_data in sample_tasks:
            client.post('/tasks',
                       data=json.dumps(task_data),
                       content_type='application/json')
        
        response = client.get('/tasks?priority=high')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['priority'] == 'high'

class TestTaskUpdate:
    """Test task update functionality."""
    
    def test_update_task_all_fields(self, client, sample_task):
        """Test updating all fields of a task."""
        # Create task
        client.post('/tasks',
                   data=json.dumps(sample_task),
                   content_type='application/json')
        
        # Update task
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "priority": "low",
            "completed": True
        }
        response = client.put('/tasks/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Task updated successfully'
        assert data['task']['title'] == "Updated Task Title"
        assert data['task']['description'] == "Updated description"
        assert data['task']['priority'] == "low"
        assert data['task']['completed'] is True
        assert data['task']['completed_at'] is not None

    def test_update_task_partial_fields(self, client, sample_task):
        """Test updating only some fields of a task."""
        # Create task
        client.post('/tasks',
                   data=json.dumps(sample_task),
                   content_type='application/json')
        
        # Update only title
        update_data = {"title": "Only Title Updated"}
        response = client.put('/tasks/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['task']['title'] == "Only Title Updated"
        assert data['task']['description'] == sample_task['description']  # unchanged
        assert data['task']['priority'] == sample_task['priority']  # unchanged

    def test_update_nonexistent_task(self, client):
        """Test updating a task that doesn't exist."""
        update_data = {"title": "Updated Title"}
        response = client.put('/tasks/999',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Task not found'

    def test_update_task_no_data(self, client, sample_task):
        """Test updating a task with no data provided."""
        # Create task
        client.post('/tasks',
                   data=json.dumps(sample_task),
                   content_type='application/json')
        
        response = client.put('/tasks/1',
                            data=json.dumps({}),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'No data provided'

class TestTaskDeletion:
    """Test task deletion functionality."""
    
    def test_delete_existing_task(self, client, sample_task):
        """Test deleting an existing task."""
        # Create task
        client.post('/tasks',
                   data=json.dumps(sample_task),
                   content_type='application/json')
        
        # Delete task
        response = client.delete('/tasks/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Task deleted successfully'
        assert data['deleted_task']['id'] == 1

    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist."""
        response = client.delete('/tasks/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Task not found'

    def test_delete_task_removes_from_list(self, client, sample_tasks):
        """Test that deleted task is removed from the tasks list."""
        # Create tasks
        for task_data in sample_tasks:
            client.post('/tasks',
                       data=json.dumps(task_data),
                       content_type='application/json')
        
        # Verify 3 tasks exist
        response = client.get('/tasks')
        assert len(json.loads(response.data)['tasks']) == 3
        
        # Delete middle task
        client.delete('/tasks/2')
        
        # Verify only 2 tasks remain
        response = client.get('/tasks')
        data = json.loads(response.data)
        assert len(data['tasks']) == 2
        task_ids = [task['id'] for task in data['tasks']]
        assert 2 not in task_ids

class TestTaskCompletion:
    """Test task completion functionality."""
    
    def test_complete_existing_task(self, client, sample_task):
        """Test completing an existing task."""
        # Create task
        client.post('/tasks',
                   data=json.dumps(sample_task),
                   content_type='application/json')
        
        # Complete task
        response = client.post('/tasks/1/complete')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Task marked as completed'
        assert data['task']['completed'] is True
        assert data['task']['completed_at'] is not None

    def test_complete_nonexistent_task(self, client):
        """Test completing a task that doesn't exist."""
        response = client.post('/tasks/999/complete')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Task not found'

class TestTaskStatistics:
    """Test task statistics functionality."""
    
    def test_get_stats_empty_tasks(self, client):
        """Test getting statistics when no tasks exist."""
        response = client.get('/tasks/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_tasks'] == 0
        assert data['completed_tasks'] == 0
        assert data['pending_tasks'] == 0
        assert data['overdue_tasks'] == 0
        assert data['completion_rate'] == 0

    def test_get_stats_with_tasks(self, client, sample_tasks):
        """Test getting statistics with various tasks."""
        # Create tasks
        for task_data in sample_tasks:
            client.post('/tasks',
                       data=json.dumps(task_data),
                       content_type='application/json')
        
        # Complete one task
        client.post('/tasks/1/complete')
        
        response = client.get('/tasks/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_tasks'] == 3
        assert data['completed_tasks'] == 1
        assert data['pending_tasks'] == 2
        assert data['completion_rate'] == 33.33

class TestAPIEndpoints:
    """Test basic API endpoint functionality."""
    
    def test_home_endpoint(self, client):
        """Test the home API endpoint."""
        response = client.get('/api')
        
        assert response.status_code == 200
        assert response.data.decode() == "Task Manager API - Use /tasks endpoint"

    def test_index_endpoint(self, client):
        """Test the index endpoint serves the frontend."""
        response = client.get('/')
        
        assert response.status_code == 200
        # Should serve the index.html file
        assert b'html' in response.data.lower()

class TestErrorHandling:
    """Test error handling functionality."""
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON in request."""
        response = client.post('/tasks',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400

    def test_missing_content_type(self, client):
        """Test handling of missing content type header."""
        response = client.post('/tasks',
                             data='{"title": "Test"}')
        
        # Flask should still process this, but it's good to test
        assert response.status_code in [200, 201, 400]
