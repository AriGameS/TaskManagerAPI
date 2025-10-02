from flask import Flask, request, jsonify
from datetime import datetime
import random
import string

app = Flask(__name__, static_folder='frontend', static_url_path='')

# ---------------- In-memory stores ----------------
# rooms: { ROOM_CODE: {
#   "code": str, "owner": str, "members": [str], "created_at": str,
#   "tasks": [ {id, title, description, priority, due_date, completed, completed_at, created_at} ]
# }}
rooms = {}

# ---------------- Helpers ----------------
def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def generate_room_code(length: int = 6) -> str:
    # Uppercase letters + digits, unique across rooms
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(alphabet, k=length))
        if code not in rooms:
            return code

def parse_due_date_str(s: str | None):
    """Accept 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'. Return normalized 'YYYY-MM-DD HH:MM:SS' or None."""
    if not s:
        return None
    try:
        return datetime.strptime(s, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            # normalize date-only to midnight
            return datetime.strptime(s, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

def require_room(room_code: str | None):
    if not room_code:
        return None, (jsonify({"error": "room is required. Provide ?room=ROOM_CODE or body.room_code"}), 400)
    room = rooms.get(room_code)
    if not room:
        return None, (jsonify({"error": f"room '{room_code}' not found"}), 404)
    return room, None

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/api', methods=['GET'])
def home():
    return "Task Manager API - Use /tasks endpoint"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for monitoring and load balancers."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "version": "1.0.0",
        "uptime": "running"
    })

# ---------------- Rooms ----------------
@app.route('/rooms', methods=['POST'])
def create_room():
    """
    Create a new room.
    Body: { "username": "Alice" }
    Returns: { room_code, room }
    """
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    if not username:
        return jsonify({"error": "username is required"}), 400

    code = generate_room_code()
    room = {
        "code": code,
        "owner": username,
        "members": [username],
        "created_at": now_str(),
        "tasks": []
    }
    rooms[code] = room
    return jsonify({
        "room_code": code,
        "room": room
    }), 201

@app.route('/rooms/<room_code>', methods=['GET'])
def get_room(room_code):
    """Get room info."""
    room, err = require_room(room_code)
    if err:
        return err
    return jsonify(room)

# Existing route: still works with /rooms/<room_code>/join
@app.route('/rooms/<room_code>/join', methods=['POST'])
def join_room(room_code):
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    if not username:
        return jsonify({"error": "username is required"}), 400

    if username not in rooms[room_code]['members']:
        rooms[room_code]['members'].append(username)
    return jsonify({"message": "Joined room", "room": rooms[room_code]})


# New shortcut route: allows POST /rooms/join with body {room_code, username}
@app.route('/rooms/join', methods=['POST'])
def join_room_short():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    room_code = (data.get('room_code') or request.args.get('room') or '').strip()

    if not username:
        return jsonify({"error": "username is required"}), 400
    if not room_code:
        return jsonify({"error": "room_code is required"}), 400

    room, err = require_room(room_code)
    if err:
        return err

    if username not in room['members']:
        room['members'].append(username)
    return jsonify({"message": "Joined room", "room": room})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    
    room_code = request.args.get('room')
    room, err = require_room(room_code)
    if err:
        return err
    
    filtered_tasks = room['tasks'].copy()
    
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
        "total_all": len(room['tasks'])
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Missing task title"}), 400
    
    room_code = data.get('room_code') or request.args.get('room')
    room, err = require_room(room_code)
    if err:
        return err
    
    # Parse due_date if provided
    due_date = parse_due_date_str(data.get('due_date'))
    if data.get('due_date') and not due_date:
        return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"}), 400
    
    task = {
        "id": len(room['tasks']) + 1,
        "title": data['title'],
        "description": data.get('description', ''),
        "priority": data.get('priority', 'medium'),
        "due_date": due_date,
        "completed": False,
        "completed_at": None,
        "created_at": now_str()
    }
    
    room['tasks'].append(task)
    
    return jsonify({
        "message": "Task created successfully",
        "task": task
    }), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    room_code = request.args.get('room')
    room, err = require_room(room_code)
    if err:
        return err
    
    task = next((t for t in room['tasks'] if t['id'] == task_id), None)
    
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
            due_date = parse_due_date_str(data['due_date'])
            if not due_date:
                return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"}), 400
            task['due_date'] = due_date
    
    return jsonify({
        "message": "Task updated successfully",
        "task": task
    })

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    room_code = request.args.get('room')
    room, err = require_room(room_code)
    if err:
        return err
    
    task = next((t for t in room['tasks'] if t['id'] == task_id), None)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    room['tasks'] = [t for t in room['tasks'] if t['id'] != task_id]
    
    return jsonify({
        "message": "Task deleted successfully",
        "deleted_task": task
    })

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    room_code = request.args.get('room')
    room, err = require_room(room_code)
    if err:
        return err
    
    task = next((t for t in room['tasks'] if t['id'] == task_id), None)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task['completed'] = True
    task['completed_at'] = now_str()
    
    return jsonify({
        "message": "Task marked as completed",
        "task": task
    })

@app.route('/tasks/stats', methods=['GET'])
def get_stats():
    room_code = request.args.get('room')
    room, err = require_room(room_code)
    if err:
        return err
    
    total_tasks = len(room['tasks'])
    completed_tasks = len([t for t in room['tasks'] if t['completed']])
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = 0
    
    now = datetime.now()
    for task in room['tasks']:
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
    print("   POST /rooms               - Create new room")
    print("   GET  /rooms/<code>        - Get room info")
    print("   POST /rooms/<code>/join   - Join room")
    print("   POST /rooms/join          - Join room (shortcut)")
    print("   GET  /tasks               - Get all tasks (with filtering)")
    print("   POST /tasks              - Create new task")
    print("   PUT  /tasks/<id>         - Update specific task")
    print("   DELETE /tasks/<id>       - Delete specific task")
    print("   POST /tasks/<id>/complete - Mark task as completed")
    print("   GET  /tasks/stats        - Get task statistics")
    print("   GET  /health             - Health check endpoint")
    print("Web interface available at http://localhost:5125/")
    app.run(host='0.0.0.0', port=5125, debug=True)