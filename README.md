# Task Manager API

A simple Flask REST API for managing tasks.

## Quick Start

```bash
# Install Flask
pip install -r requirements.txt

# Run the app
python app.py
```

API will be available at: http://localhost:5000

## API Endpoints

- `GET /tasks` - Get all tasks
- `POST /tasks` - Create new task

## Usage Examples

### Get All Tasks
```bash
curl http://localhost:5000/tasks
```

### Create New Task
```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, bread, eggs"}'
```

### Response Example
```json
{
  "message": "Task created successfully",
  "task": {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "completed": false,
    "created_at": "2025-08-01 12:30:00"
  }
}
```

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

## Project Files

- `app.py` - Main Flask application (single file!)
- `requirements.txt` - Dependencies
- `Dockerfile` - Container setup
- `docker-compose.yml` - Easy container orchestration
- `README.md` - This documentation