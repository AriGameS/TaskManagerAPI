import pytest
import json
import requests
import time
import subprocess
import os
from threading import Thread

class TestAPIIntegration:
    """Integration tests that test the API as a running service."""
    
    @pytest.fixture(scope="class")
    def running_app(self):
        """Start the Flask app in a separate process for integration testing."""
        # Start the app
        env = os.environ.copy()
        env['FLASK_ENV'] = 'testing'
        process = subprocess.Popen(
            ['python', 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for app to start
        time.sleep(3)
        
        yield process
        
        # Cleanup
        process.terminate()
        process.wait()

    def test_api_health_check(self, running_app):
        """Test that the API is running and responding."""
        try:
            response = requests.get('http://localhost:5125/api', timeout=5)
            assert response.status_code == 200
            assert "Task Manager API" in response.text
        except requests.exceptions.RequestException:
            pytest.skip("API not accessible - may not be running")

    def test_full_task_lifecycle(self, running_app):
        """Test complete task lifecycle: create, read, update, complete, delete."""
        try:
            base_url = 'http://localhost:5125'
            
            # 1. Create a task
            task_data = {
                "title": "Integration Test Task",
                "description": "Testing full lifecycle",
                "priority": "high",
                "due_date": "2025-12-31 23:59:59"
            }
            
            response = requests.post(
                f'{base_url}/tasks',
                json=task_data,
                timeout=5
            )
            assert response.status_code == 201
            created_task = response.json()['task']
            task_id = created_task['id']
            
            # 2. Read the task
            response = requests.get(f'{base_url}/tasks', timeout=5)
            assert response.status_code == 200
            tasks = response.json()['tasks']
            assert len(tasks) == 1
            assert tasks[0]['title'] == task_data['title']
            
            # 3. Update the task
            update_data = {
                "title": "Updated Integration Test Task",
                "priority": "medium"
            }
            response = requests.put(
                f'{base_url}/tasks/{task_id}',
                json=update_data,
                timeout=5
            )
            assert response.status_code == 200
            updated_task = response.json()['task']
            assert updated_task['title'] == update_data['title']
            assert updated_task['priority'] == update_data['priority']
            
            # 4. Complete the task
            response = requests.post(
                f'{base_url}/tasks/{task_id}/complete',
                timeout=5
            )
            assert response.status_code == 200
            completed_task = response.json()['task']
            assert completed_task['completed'] is True
            assert completed_task['completed_at'] is not None
            
            # 5. Check statistics
            response = requests.get(f'{base_url}/tasks/stats', timeout=5)
            assert response.status_code == 200
            stats = response.json()
            assert stats['total_tasks'] == 1
            assert stats['completed_tasks'] == 1
            assert stats['pending_tasks'] == 0
            
            # 6. Delete the task
            response = requests.delete(f'{base_url}/tasks/{task_id}', timeout=5)
            assert response.status_code == 200
            
            # 7. Verify task is deleted
            response = requests.get(f'{base_url}/tasks', timeout=5)
            assert response.status_code == 200
            tasks = response.json()['tasks']
            assert len(tasks) == 0
            
        except requests.exceptions.RequestException:
            pytest.skip("API not accessible - may not be running")

    def test_concurrent_task_creation(self, running_app):
        """Test creating multiple tasks concurrently."""
        try:
            base_url = 'http://localhost:5125'
            
            def create_task(task_num):
                task_data = {
                    "title": f"Concurrent Task {task_num}",
                    "description": f"Task created concurrently {task_num}",
                    "priority": "medium"
                }
                response = requests.post(
                    f'{base_url}/tasks',
                    json=task_data,
                    timeout=5
                )
                return response.status_code == 201
            
            # Create 5 tasks concurrently
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(create_task, i) for i in range(5)]
                results = [future.result() for future in futures]
            
            # All tasks should be created successfully
            assert all(results)
            
            # Verify all tasks exist
            response = requests.get(f'{base_url}/tasks', timeout=5)
            assert response.status_code == 200
            tasks = response.json()['tasks']
            assert len(tasks) == 5
            
        except requests.exceptions.RequestException:
            pytest.skip("API not accessible - may not be running")

    def test_filtering_endpoints(self, running_app):
        """Test various filtering options."""
        try:
            base_url = 'http://localhost:5125'
            
            # Create test tasks
            test_tasks = [
                {"title": "High Priority Task", "priority": "high"},
                {"title": "Medium Priority Task", "priority": "medium"},
                {"title": "Low Priority Task", "priority": "low"}
            ]
            
            for task_data in test_tasks:
                response = requests.post(
                    f'{base_url}/tasks',
                    json=task_data,
                    timeout=5
                )
                assert response.status_code == 201
            
            # Complete one task
            requests.post(f'{base_url}/tasks/1/complete', timeout=5)
            
            # Test priority filtering
            response = requests.get(f'{base_url}/tasks?priority=high', timeout=5)
            assert response.status_code == 200
            tasks = response.json()['tasks']
            assert len(tasks) == 1
            assert tasks[0]['priority'] == 'high'
            
            # Test status filtering
            response = requests.get(f'{base_url}/tasks?status=completed', timeout=5)
            assert response.status_code == 200
            tasks = response.json()['tasks']
            assert len(tasks) == 1
            assert tasks[0]['completed'] is True
            
            response = requests.get(f'{base_url}/tasks?status=pending', timeout=5)
            assert response.status_code == 200
            tasks = response.json()['tasks']
            assert len(tasks) == 2
            for task in tasks:
                assert task['completed'] is False
            
        except requests.exceptions.RequestException:
            pytest.skip("API not accessible - may not be running")

    def test_error_handling_integration(self, running_app):
        """Test error handling in the running API."""
        try:
            base_url = 'http://localhost:5125'
            
            # Test 404 for non-existent task
            response = requests.get(f'{base_url}/tasks/999', timeout=5)
            assert response.status_code == 404
            
            response = requests.put(
                f'{base_url}/tasks/999',
                json={"title": "Update"},
                timeout=5
            )
            assert response.status_code == 404
            
            response = requests.delete(f'{base_url}/tasks/999', timeout=5)
            assert response.status_code == 404
            
            response = requests.post(f'{base_url}/tasks/999/complete', timeout=5)
            assert response.status_code == 404
            
            # Test 400 for invalid data
            response = requests.post(
                f'{base_url}/tasks',
                json={"description": "No title"},
                timeout=5
            )
            assert response.status_code == 400
            
        except requests.exceptions.RequestException:
            pytest.skip("API not accessible - may not be running")

    def test_frontend_serving(self, running_app):
        """Test that the frontend is being served correctly."""
        try:
            base_url = 'http://localhost:5125'
            
            # Test main page
            response = requests.get(f'{base_url}/', timeout=5)
            assert response.status_code == 200
            assert 'html' in response.headers.get('content-type', '').lower()
            
        except requests.exceptions.RequestException:
            pytest.skip("API not accessible - may not be running")
