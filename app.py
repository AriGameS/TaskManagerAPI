from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Simple in-memory storage for tasks
tasks = []

@app.route('/', methods=['GET'])
def home():
    return "Task Manager API - Use /tasks endpoint"

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify({
        "tasks": tasks,
        "total": len(tasks)
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Missing task title"}), 400
    
    task = {
        "id": len(tasks) + 1,
        "title": data['title'],
        "description": data.get('description', ''),
        "completed": False,
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    tasks.append(task)
    
    return jsonify({
        "message": "Task created successfully",
        "task": task
    }), 201

if __name__ == '__main__':
    print("Starting Task Manager API...")
    print("Available endpoints:")
    print("   GET  /tasks  - Get all tasks")
    print("   POST /tasks  - Create new task")
    print("Server running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)