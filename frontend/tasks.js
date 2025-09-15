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
            low: document.getElementById('low-body'),
            completed: document.getElementById('completed-body')
        };
        Object.values(groups).forEach(t => t.innerHTML = '');
        data.tasks.forEach(task => {
            let buttons = `<button class="action-btn" data-action="delete"><i class="fa-solid fa-trash"></i> Delete</button>`;
            if (!task.completed) {
                buttons = `<button class="action-btn" data-action="complete"><i class="fa-solid fa-check"></i> Complete</button>` + buttons;
            }
            const row = document.createElement('tr');
            row.dataset.id = task.id;
            row.className = 'task-row' + (task.completed ? ' completed' : '');
            row.innerHTML = `<td>${task.title}<span class="actions">${buttons}</span></td>`;
            const descRow = document.createElement('tr');
            descRow.className = 'desc-row hidden';
            descRow.innerHTML = `<td>${task.description || ''}</td>`;
            const group = task.completed ? groups.completed : (groups[task.priority] || groups.medium);
            group.appendChild(row);
            group.appendChild(descRow);
        });
        const stats = await fetchJSON('/tasks/stats');
        document.getElementById('stats').textContent = `Total: ${stats.total_tasks}, Completed: ${stats.completed_tasks}, Pending: ${stats.pending_tasks}, Overdue: ${stats.overdue_tasks}`;
    } catch (err) {
        console.error(err);
    }
}

document.getElementById('open-modal').addEventListener('click', () => {
    document.getElementById('task-modal').classList.remove('hidden');
});

document.getElementById('close-modal').addEventListener('click', () => {
    document.getElementById('task-modal').classList.add('hidden');
});

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
        document.getElementById('task-modal').classList.add('hidden');
        loadTasks();
    } catch (err) {
        console.error(err);
    }
});

document.getElementById('task-tables').addEventListener('click', async (e) => {
    const actionEl = e.target.closest('[data-action]');
    if (actionEl) {
        const action = actionEl.dataset.action;
        const id = actionEl.closest('tr').dataset.id;
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
        return;
    }
    const taskRow = e.target.closest('tr.task-row');
    if (taskRow) {
        const descRow = taskRow.nextElementSibling;
        if (descRow && descRow.classList.contains('desc-row')) {
            descRow.classList.toggle('hidden');
        }
    }
});

loadTasks();
