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

# ---------------- Static index ----------------
@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/api', methods=['GET'])
def api_root():
    return "Task Manager API - Use /rooms and /tasks endpoints"

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
        "message": "room created",
        "room_code": code,
        "room": room
    }), 201

@app.route('/rooms/join', methods=['POST'])
def join_room():
    """
    Join an existing room.
    Body: { "username": "Bob", "room_code": "ABC123" }
    """
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    room_code = (data.get('room_code') or '').strip().upper()

    if not username or not room_code:
        return jsonify({"error": "username and room_code are required"}), 400

    room, err = require_room(room_code)
    if err:
        return err

    if username not in room["members"]:
        room["members"].append(username)

    return jsonify({
        "message": "joined room",
        "room_code": room_code,
        "room": room
    })

@app.route('/rooms/<room_code>', methods=['GET'])
def get_room(room_code):
    room, err = require_room(room_code.upper())
    if err:
        return err
    # you can redact tasks here if you only want meta; leaving as-is for now
    return jsonify(room)

# ---------------- Tasks (scoped to a room) ----------------
@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Query params:
      ?room=ROOM_CODE
      optional: ?status=pending|completed  &  ?priority=low|medium|high
    """
    room_code = request.args.get('room', type=str)
    room, err = require_room((room_code or '').upper())
    if err:
        return err

    status_filter = request.args.get('status', type=str)
    priority_filter = request.args.get('priority', type=str)

    filtered = list(room["tasks"])

    if status_filter:
        s = status_filter.lower()
        if s == 'completed':
            filtered = [t for t in filtered if t['completed']]
        elif s == 'pending':
            filtered = [t for t in filtered if not t['completed']]

    if priority_filter:
        filtered = [t for t in filtered if t.get('priority', '').lower() == priority_filter.lower()]

    return jsonify({
        "tasks": filtered,
        "total": len(filtered),
        "total_all": len(room["tasks"])
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Body: { title, description?, priority?, due_date?, room_code? }
    or query param ?room=ROOM_CODE
    """
    data = request.get_json(silent=True) or {}
    room_code = (request.args.get('room') or data.get('room_code') or '').upper()
    room, err = require_room(room_code)
    if err:
        return err

    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({"error": "Missing task title"}), 400

    due_norm = parse_due_date_str(data.get('due_date'))
    if data.get('due_date') and not due_norm:
        return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"}), 400

    task = {
        "id": len(room["tasks"]) + 1,
        "title": title,
        "description": data.get('description', ''),
        "priority": (data.get('priority') or 'medium').lower(),
        "due_date": due_norm,            # normalized 'YYYY-MM-DD HH:MM:SS' or None
        "completed": False,
        "completed_at": None,
        "created_at": now_str()
    }
    room["tasks"].append(task)

    return jsonify({"message": "Task created successfully", "task": task}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Update within a room:
      ?room=ROOM_CODE  OR body.room_code
    """
    data = request.get_json(silent=True) or {}
    room_code = (request.args.get('room') or data.get('room_code') or '').upper()
    room, err = require_room(room_code)
    if err:
        return err

    task = next((t for t in room["tasks"] if t['id'] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if 'title' in data:
        task['title'] = data['title']
    if 'description' in data:
        task['description'] = data['description']
    if 'priority' in data:
        task['priority'] = (data['priority'] or 'medium').lower()
    if 'completed' in data:
        task['completed'] = bool(data['completed'])
        task['completed_at'] = now_str() if task['completed'] else None

    if 'due_date' in data:
        if data['due_date'] is None:
            task['due_date'] = None
        else:
            due_norm = parse_due_date_str(data['due_date'])
            if not due_norm:
                return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"}), 400
            task['due_date'] = due_norm

    return jsonify({"message": "Task updated successfully", "task": task})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    room_code = (request.args.get('room') or '').upper()
    room, err = require_room(room_code)
    if err:
        return err

    task = next((t for t in room["tasks"] if t['id'] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    room["tasks"] = [t for t in room["tasks"] if t['id'] != task_id]
    return jsonify({"message": "Task deleted successfully", "deleted_task": task})

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    room_code = (request.args.get('room') or '').upper()
    room, err = require_room(room_code)
    if err:
        return err

    task = next((t for t in room["tasks"] if t['id'] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task['completed'] = True
    task['completed_at'] = now_str()
    return jsonify({"message": "Task marked as completed", "task": task})

@app.route('/tasks/stats', methods=['GET'])
def get_stats():
    room_code = (request.args.get('room') or '').upper()
    room, err = require_room(room_code)
    if err:
        return err

    total_tasks = len(room["tasks"])
    completed_tasks = len([t for t in room["tasks"] if t['completed']])
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = 0

    now = datetime.now()
    for t in room["tasks"]:
        if not t['completed'] and t.get('due_date'):
            try:
                due_dt = datetime.strptime(t['due_date'], '%Y-%m-%d %H:%M:%S')
                if due_dt < now:
                    overdue_tasks += 1
            except ValueError:
                # ignore malformed due dates (shouldn't happen; we normalize on write)
                pass

    return jsonify({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
    })

# ---------------- Run ----------------
if __name__ == '__main__':
    print("Starting Task Manager API with web UI...")
    print("Rooms:")
    print("   POST /rooms                 - Create a room {username}")
    print("   POST /rooms/join            - Join a room {username, room_code}")
    print("   GET  /rooms/<room_code>     - Get room info")
    print("Tasks (all require ?room=ROOM_CODE or body.room_code):")
    print("   GET  /tasks                 - Get room tasks (filters: status, priority)")
    print("   POST /tasks                 - Create task")
    print("   PUT  /tasks/<id>            - Update task")
    print("   DELETE /tasks/<id>          - Delete task")
    print("   POST /tasks/<id>/complete   - Complete task")
    print("   GET  /tasks/stats           - Room task stats")
    print("Web UI at http://localhost:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True)
