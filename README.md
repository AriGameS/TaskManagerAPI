# Task Manager API

A Flask REST API for managing collaborative tasks with room-based workspaces, priorities, and due dates.

## Features

- **Room-based Collaboration** - Create and join rooms for team task management
- **Task Management** - Create, read, update, and delete tasks
- **Priority Levels** - High, medium, and low priority tasks
- **Due Dates** - Schedule tasks with deadline tracking
- **Status Tracking** - Mark tasks as completed with timestamps
- **Filtering** - Filter tasks by status and priority
- **Statistics** - Track task completion and overdue items
- **Web Interface** - Modern UI for easy task management

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open http://localhost:5125 in your browser to use the web interface.

### Docker

```bash
# Build and run with Docker
docker-compose up -d
```

Access the app at http://localhost:5125

## API Endpoints

### Room Management
- `POST /rooms` - Create a new room
- `GET /rooms/<code>` - Get room information
- `POST /rooms/<code>/join` - Join an existing room

### Task Management
- `GET /tasks?room=<code>` - Get all tasks in a room
- `POST /tasks?room=<code>` - Create new task
- `PUT /tasks/<id>?room=<code>` - Update specific task
- `DELETE /tasks/<id>?room=<code>` - Delete specific task
- `POST /tasks/<id>/complete?room=<code>` - Mark task as completed
- `GET /tasks/stats?room=<code>` - Get task statistics

### Health Check
- `GET /health` - Health check endpoint for monitoring

## Usage Examples

### 1. Create a Room
```bash
curl -X POST http://localhost:5125/rooms \
  -H "Content-Type: application/json" \
  -d '{"username": "Alice"}'
```

Response:
```json
{
  "room_code": "ABC123",
  "room": {
    "code": "ABC123",
    "owner": "Alice",
    "members": ["Alice"],
    "created_at": "2025-09-30 12:00:00",
    "tasks": []
  }
}
```

### 2. Create a Task
```bash
curl -X POST "http://localhost:5125/tasks?room=ABC123" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the quarterly report",
    "priority": "high",
    "due_date": "2025-12-31 23:59:59"
  }'
```

### 3. Get All Tasks
```bash
curl "http://localhost:5125/tasks?room=ABC123"
```

### 4. Mark Task as Completed
```bash
curl -X POST "http://localhost:5125/tasks/1/complete?room=ABC123"
```

### 5. Get Statistics
```bash
curl "http://localhost:5125/tasks/stats?room=ABC123"
```

## Project Structure

```
.
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Docker Compose setup
├── pytest.ini                  # Pytest configuration
├── frontend/                   # Web interface
│   ├── index.html             # Landing page
│   ├── tasks.html             # Task management page
│   ├── home-styles.css        # Landing page styles
│   ├── styles.css             # Task page styles
│   ├── script.js              # Landing page logic
│   └── tasks.js               # Task page logic
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Test fixtures
│   ├── test_app.py            # Unit tests
│   └── test_api_integration.py # Integration tests
└── .github/workflows/          # CI/CD pipelines
    ├── ci.yml                 # Continuous Integration
    └── deploy.yml             # Deployment pipeline
```

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=term-missing
```

### Run Specific Tests
```bash
# Unit tests only
pytest tests/test_app.py

# Integration tests only
pytest tests/test_api_integration.py
```

## Docker

### Build Image
```bash
docker build -t taskmanager-api .
```

### Run Container
```bash
docker run -d -p 5125:5125 taskmanager-api
```

### Using Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## CI/CD

The project includes GitHub Actions workflows for:

- **Continuous Integration** - Automated testing on push/PR
- **Deployment** - Automated deployment to production

### CI Pipeline
- Python 3.10 and 3.11 compatibility testing
- Code linting with flake8
- Unit and integration tests
- Security scanning
- Docker image build and test

## Task Properties

- **id**: Unique task identifier (auto-generated)
- **title**: Task title (required)
- **description**: Detailed task description (optional)
- **priority**: Task priority - "high", "medium", or "low" (default: "medium")
- **due_date**: Task deadline in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format (optional)
- **completed**: Task completion status (boolean)
- **completed_at**: Timestamp when task was completed (auto-set)
- **created_at**: Task creation timestamp (auto-set)

## Room Properties

- **code**: Unique 6-character room code (auto-generated)
- **owner**: Username of room creator
- **members**: List of usernames in the room
- **created_at**: Room creation timestamp
- **tasks**: Array of tasks in the room

## Environment Variables

- `FLASK_ENV` - Environment mode (development/production)
- `PYTHONUNBUFFERED` - Python unbuffered output
- `FLASK_APP` - Flask application entry point

## Development

### Prerequisites
- Python 3.10 or 3.11
- Docker (optional)
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/AriGameS/TaskManagerAPI.git
cd TaskManagerAPI

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development server
python app.py
```

## Production Deployment

The application uses Gunicorn as the production WSGI server:

```bash
gunicorn --bind 0.0.0.0:5125 --workers 4 app:app
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (missing required fields, invalid data)
- `404` - Not Found (room or task doesn't exist)
- `500` - Internal Server Error

Example error response:
```json
{
  "error": "room is required. Provide ?room=ROOM_CODE"
}
```

## Security

- Non-root user in Docker container
- Health checks for monitoring
- CORS support for web clients
- Input validation on all endpoints

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

For issues and questions:
- Check GitHub Issues
- Review API documentation
- Check application logs# CI/CD Test - Fri Oct  3 06:30:34 IDT 2025
