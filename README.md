# Task Manager API

A comprehensive Flask REST API for managing tasks with priorities, due dates, and completion tracking.

## Features

- Create, read, update, and delete tasks
- Mark tasks as completed with completion timestamps
- Set task priorities (high, medium, low)
- Schedule tasks with due dates and times
- Filter tasks by status and priority
- Track overdue tasks automatically
- Get comprehensive task statistics
- RESTful API design with proper HTTP methods

## Quick Start

```bash
# Install Flask
pip install -r requirements.txt

# Run the app
python app.py
```

API will be available at: http://localhost:5000

## API Endpoints

### Task Management
- `GET /tasks` - Get all tasks (with optional filtering)
- `POST /tasks` - Create new task
- `PUT /tasks/<id>` - Update specific task
- `DELETE /tasks/<id>` - Delete specific task

### Task Actions
- `POST /tasks/<id>/complete` - Mark task as completed
- `GET /tasks/stats` - Get task statistics

### Filtering Options
- `GET /tasks?status=completed` - Get only completed tasks
- `GET /tasks?status=pending` - Get only pending tasks
- `GET /tasks?priority=high` - Get tasks by priority level

## Usage Examples

### Create New Task
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project report",
    "description": "Finish the quarterly analysis report",
    "priority": "high",
    "due_date": "2025-08-15 17:00:00"
  }'
```

### Create Simple Task
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs"
  }'
```

### Get All Tasks
```bash
curl http://localhost:5000/tasks
```

### Get Completed Tasks Only
```bash
curl "http://localhost:5000/tasks?status=completed"
```

### Get High Priority Tasks
```bash
curl "http://localhost:5000/tasks?priority=high"
```

### Mark Task as Completed
```bash
curl -X POST http://localhost:5000/tasks/1/complete
```

### Update Task
```bash
curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task title",
    "priority": "medium",
    "completed": true
  }'
```

### Delete Task
```bash
curl -X DELETE http://localhost:5000/tasks/1
```

### Get Task Statistics
```bash
curl http://localhost:5000/tasks/stats
```

## Response Examples

### Task Object
```json
{
  "id": 1,
  "title": "Complete project report",
  "description": "Finish the quarterly analysis report",
  "priority": "high",
  "due_date": "2025-08-15 17:00:00",
  "completed": false,
  "completed_at": null,
  "created_at": "2025-08-01 12:30:00"
}
```

### Completed Task
```json
{
  "id": 1,
  "title": "Complete project report",
  "description": "Finish the quarterly analysis report",
  "priority": "high",
  "due_date": "2025-08-15 17:00:00",
  "completed": true,
  "completed_at": "2025-08-15 16:45:00",
  "created_at": "2025-08-01 12:30:00"
}
```

### Task Statistics
```json
{
  "total_tasks": 10,
  "completed_tasks": 6,
  "pending_tasks": 4,
  "overdue_tasks": 1,
  "completion_rate": 60.0
}
```

## Task Properties

- **id**: Unique task identifier (auto-generated)
- **title**: Task title (required)
- **description**: Detailed task description (optional)
- **priority**: Task priority - "high", "medium", or "low" (default: "medium")
- **due_date**: Task deadline in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format (optional)
- **completed**: Task completion status (boolean)
- **completed_at**: Timestamp when task was completed (auto-set)
- **created_at**: Task creation timestamp (auto-set)

## Priority Levels

- **high**: Urgent tasks requiring immediate attention
- **medium**: Standard priority tasks (default)
- **low**: Tasks that can be completed when time permits

## Due Date Formats

The API accepts due dates in two formats:
- `YYYY-MM-DD` (e.g., "2025-08-15") - Sets time to 00:00:00
- `YYYY-MM-DD HH:MM:SS` (e.g., "2025-08-15 17:30:00") - Specific date and time

## Docker

### Option 1: Docker Compose (Recommended)
```bash
# Start the service
docker-compose up -d

# Stop the service
docker-compose down
```

### Option 2: Manual Docker
```bash
# Build image
docker build -t task-manager .

# Run container
docker run -p 5000:5000 task-manager
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing required fields, invalid data)
- `404` - Not Found (task doesn't exist)
- `500` - Internal Server Error

Example error response:
```json
{
  "error": "Task not found"
}
```

## Project Files

- `app.py` - Main Flask application with all endpoints
- `requirements.txt` - Dependencies
- `Dockerfile` - Container setup
- `docker-compose.yml` - Easy container orchestration
- `README.md` - This documentation

## Development Notes

- Tasks are stored in memory and will be lost when the application restarts
- For production use, integrate with a database (PostgreSQL, MongoDB, etc.)
- The API automatically tracks overdue tasks based on current time
- Task IDs are sequential and auto-generated
- Completion timestamps are automatically set when marking tasks complete