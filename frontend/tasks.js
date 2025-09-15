// ---------- Errors & fetch ----------
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

// ---------- Date helpers ----------
function parseDueDate(raw) {
    if (!raw) return null;
    let s = String(raw).trim();

    // "YYYY-MM-DD HH:mm:ss" -> "YYYY-MM-DDTHH:mm:ss"
    if (s.includes(' ') && !s.includes('T')) s = s.replace(' ', 'T');

    // DD/MM/YYYY
    if (s.includes('/') && !s.includes('-')) {
        const [dd, mm, yyyy] = s.split('/');
        if (dd && mm && yyyy) {
            return new Date(Number(yyyy), Number(mm) - 1, Number(dd)); // local midnight
        }
    }

    const d = new Date(s);
    return isNaN(d.getTime()) ? null : d;
}

function plural(n, word) {
    return `${n} ${word}${n === 1 ? '' : 's'}`;
}

function formatTimeLeft(dueDate) {
    if (!dueDate) return '';
    const now = new Date();
    const ms = dueDate - now;
    const abs = Math.abs(ms);

    const MIN = 60 * 1000;
    const HOUR = 60 * MIN;
    const DAY = 24 * HOUR;

    if (abs < HOUR) {
        const minutes = Math.max(1, Math.round(abs / MIN));
        return ms >= 0 ? `${plural(minutes, 'minute')} left` : `Overdue by ${plural(minutes, 'minute')}`;
    }
    if (abs < DAY) {
        const hours = Math.round(abs / HOUR);
        return ms >= 0 ? `${plural(hours, 'hour')} left (today)` : `Overdue by ${plural(hours, 'hour')}`;
    }
    const days = Math.round(abs / DAY);
    return ms >= 0 ? `${plural(days, 'day')} left` : `Overdue by ${plural(days, 'day')}`;
}

function escapeHTML(s) {
    if (!s) return '';
    return s
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

// ---------- App ----------
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

        const now = new Date();

        data.tasks.forEach(task => {
            // Build actions (TEXT ONLY)
            let buttons = '';
            if (!task.completed) {
                buttons += `<button class="action-btn complete" data-action="complete">Complete</button>`;
            }
            buttons += `<button class="action-btn delete" data-action="delete">Delete</button>`;

            // Main row
            const row = document.createElement('tr');
            row.dataset.id = task.id;
            row.className = 'task-row' + (task.completed ? ' completed' : '');

            row.innerHTML = `
                <td>
                    <div class="task-title">${escapeHTML(task.title)}</div>
                </td>
            `;

            // Desc row
            const descRow = document.createElement('tr');
            descRow.className = 'desc-row hidden';

            let timeInfo = '';
            let dueInfo = '';
            if (task.due_date) {
                const dueDate = parseDueDate(task.due_date);
                if (dueDate) {
                    if (!task.completed && dueDate < now) {
                        row.classList.add('overdue');
                        descRow.classList.add('overdue');
                    }
                    const tl = formatTimeLeft(dueDate);
                    const tlClass = (!task.completed && dueDate < now) ? 'time-left overdue' : 'time-left';

                    // format to YYYY-MM-DD only
                   const formattedDate = `${String(dueDate.getDate()).padStart(2, '0')}-${String(dueDate.getMonth() + 1).padStart(2, '0')}-${dueDate.getFullYear()}`;

                    dueInfo = `
                    <div class="due-info">
                        <span class="due-date"><small>Due: ${formattedDate}</small></span>
                        <span class="${tlClass}">(${tl})</span>
                    </div>
                    `;

                }
            }


            descRow.innerHTML = `
                <td>
                    <div class="desc-box">
                        <div class="desc-content">${escapeHTML(task.description || '')}</div>
                        ${timeInfo}
                        ${dueInfo}
                        <div class="actions below-title">
                            ${buttons}
                        </div>
                    </div>
                </td>
            `;


            const group = task.completed ? groups.completed : (groups[task.priority] || groups.medium);
            group.appendChild(row);
            group.appendChild(descRow);
        });

        // Stats
        const stats = await fetchJSON('/tasks/stats');
        document.getElementById('stats').textContent =
            `Total: ${stats.total_tasks}, Completed: ${stats.completed_tasks}, Pending: ${stats.pending_tasks}, Overdue: ${stats.overdue_tasks}`;
    } catch (err) {
        console.error(err);
    }
}

// Modal open/close
document.getElementById('open-modal').addEventListener('click', () => {
    document.getElementById('task-modal').classList.remove('hidden');
    document.getElementById('task-modal').setAttribute('aria-hidden', 'false');
});
document.getElementById('close-modal').addEventListener('click', () => {
    document.getElementById('task-modal').classList.add('hidden');
    document.getElementById('task-modal').setAttribute('aria-hidden', 'true');
});

// Create task
document.getElementById('task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const priority = document.getElementById('priority').value;
    const due_date = document.getElementById('due_date').value || null; // YYYY-MM-DD from input

    try {
        await fetchJSON('/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title, description, priority, due_date })
        });
        e.target.reset();
        document.getElementById('task-modal').classList.add('hidden');
        document.getElementById('task-modal').setAttribute('aria-hidden', 'true');
        loadTasks();
    } catch (err) {
        console.error(err);
    }
});

// Row interactions
document.getElementById('task-tables').addEventListener('click', async (e) => {
    const actionEl = e.target.closest('[data-action]');
    if (actionEl) {
        const action = actionEl.dataset.action;
        const parentRow = actionEl.closest('tr').previousElementSibling;
        const id = parentRow?.dataset.id;

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

// Initial + periodic refresh (so "time left" updates live)
loadTasks();
setInterval(loadTasks, 60000);
