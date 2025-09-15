function showError(message) {
    const errorDiv = document.getElementById('error');
    if (message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    } else {
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }
}

async function fetchJSON(url, options) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            let msg = response.statusText;
            try {
                const data = await response.json();
                msg = data.error || msg;
            } catch (e) {}
            throw new Error(msg);
        }
        return await response.json();
    } catch (err) {
        showError(err.message);
        throw err;
    }
}

async function loadTasks() {
    showError('');
    try {
        const data = await fetchJSON('/tasks');
        const groups = {
            high: document.getElementById('high-body'),
            medium: document.getElementById('medium-body'),
            low: document.getElementById('low-body')
        };
        Object.values(groups).forEach(t => t.innerHTML = '');
        data.tasks.forEach(task => {
            const row = document.createElement('tr');
            row.dataset.id = task.id;
            row.className = task.completed ? 'completed' : '';
            let actions = '';
            if (!task.completed) {
                actions += `<button data-action="complete">Complete</button>`;
            }
            actions += `<button data-action="delete">Delete</button>`;
            row.innerHTML = `<td>${task.title}</td><td>${task.description || ''}</td><td>${actions}</td>`;
            const group = groups[task.priority] || groups.medium;
            group.appendChild(row);
        });
        const stats = await fetchJSON('/tasks/stats');
        document.getElementById('stats').textContent = `Total: ${stats.total_tasks}, Completed: ${stats.completed_tasks}, Pending: ${stats.pending_tasks}, Overdue: ${stats.overdue_tasks}`;
    } catch (err) {
        console.error(err);
    }
}

document.getElementById('task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const priority = document.getElementById('priority').value;
    try {
        await fetchJSON('/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title, description, priority })
        });
        e.target.reset();
        loadTasks();
    } catch (err) {
        console.error(err);
    }
});

document.getElementById('task-tables').addEventListener('click', async (e) => {
    const action = e.target.dataset.action;
    if (!action) return;
    const id = e.target.closest('tr').dataset.id;
    try {
        if (action === 'delete') {
            await fetchJSON(`/tasks/${id}`, { method: 'DELETE' });
        } else if (action === 'complete') {
            await fetchJSON(`/tasks/${id}/complete`, { method: 'POST' });
        }
        loadTasks();
    } catch (err) {
        console.error(err);
    }
});

loadTasks();
