from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__, static_folder='frontend', static_url_path='')

# Simple in-memory storage for tasks
tasks = []

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/api', methods=['GET'])
def home():
    return "Task Manager API - Use /tasks endpoint"

@app.route('/tasks', methods=['GET'])
def get_tasks():
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    
    filtered_tasks = tasks
    
    if status_filter:
        if status_filter.lower() == 'completed':
            filtered_tasks = [t for t in filtered_tasks if t['completed']]
        elif status_filter.lower() == 'pending':
            filtered_tasks = [t for t in filtered_tasks if not t['completed']]
    
    if priority_filter:
        filtered_tasks = [t for t in filtered_tasks if t.get('priority', '').lower() == priority_filter.lower()]
    
    return jsonify({
        "tasks": filtered_tasks,
        "total": len(filtered_tasks),
        "total_all": len(tasks)
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Missing task title"}), 400
    
    # Parse due_date if provided
    due_date = None
    if 'due_date' in data:
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"}), 400
    
    task = {
        "id": len(tasks) + 1,
        "title": data['title'],
        "description": data.get('description', ''),
        "priority": data.get('priority', 'medium'),
        "due_date": due_date,
        "completed": False,
        "completed_at": None,
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    tasks.append(task)
    
    return jsonify({
        "message": "Task created successfully",
        "task": task
    }), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update fields if provided
    if 'title' in data:
        task['title'] = data['title']
    if 'description' in data:
        task['description'] = data['description']
    if 'priority' in data:
        task['priority'] = data['priority']
    if 'completed' in data:
        task['completed'] = bool(data['completed'])
        if task['completed'] and not task['completed_at']:
            task['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif not task['completed']:
            task['completed_at'] = None
    
    # Handle due_date update
    if 'due_date' in data:
        if data['due_date'] is None:
            task['due_date'] = None
        else:
            try:
                task['due_date'] = datetime.strptime(data['due_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    task['due_date'] = datetime.strptime(data['due_date'], '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"}), 400
    
    return jsonify({
        "message": "Task updated successfully",
        "task": task
    })

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    tasks = [t for t in tasks if t['id'] != task_id]
    
    return jsonify({
        "message": "Task deleted successfully",
        "deleted_task": task
    })

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task['completed'] = True
    task['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        "message": "Task marked as completed",
        "task": task
    })

@app.route('/tasks/stats', methods=['GET'])
def get_stats():
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['completed']])
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = 0
    
    now = datetime.now()
    for task in tasks:
        if not task['completed'] and task['due_date']:
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d %H:%M:%S')
            if due_date < now:
                overdue_tasks += 1
    
    return jsonify({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
    })

if __name__ == '__main__':
    print("Starting Task Manager API with web UI...")
    print("Available endpoints:")
    print("   GET  /tasks               - Get all tasks (with filtering)")
    print("   POST /tasks              - Create new task")
    print("   PUT  /tasks/<id>         - Update specific task")
    print("   DELETE /tasks/<id>       - Delete specific task")
    print("   POST /tasks/<id>/complete - Mark task as completed")
    print("   GET  /tasks/stats        - Get task statistics")
    print("Web interface available at http://localhost:5125/")
    app.run(host='0.0.0.0', port=5125, debug=True)