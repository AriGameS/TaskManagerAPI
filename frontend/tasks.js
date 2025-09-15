/* ========== Basic helpers ========== */
function showError(message) {
  const el = document.getElementById('error');
  if (!el) return;
  if (message) {
    el.textContent = message;
    el.style.display = 'block';
  } else {
    el.textContent = '';
    el.style.display = 'none';
  }
}

async function fetchJSON(url, options) {
  try {
    const res = await fetch(url, options);
    let data = null;
    try { data = await res.json(); } catch {}
    if (!res.ok) {
      const msg = data?.error || res.statusText || 'Request failed';
      throw new Error(msg);
    }
    return data ?? {};
  } catch (err) {
    showError(err.message);
    throw err;
  }
}

function escapeHTML(s) {
  if (!s) return '';
  return s.replaceAll('&', '&amp;')
          .replaceAll('<', '&lt;')
          .replaceAll('>', '&gt;')
          .replaceAll('"', '&quot;')
          .replaceAll("'", '&#39;');
}

/* ========== Room/Name handling (URL or localStorage) ========== */
const urlParams = new URLSearchParams(location.search);
let ROOM = (urlParams.get('room') || localStorage.getItem('tm_room') || '').toUpperCase();
let USER = urlParams.get('name') || localStorage.getItem('tm_name') || '';

if (urlParams.get('room')) localStorage.setItem('tm_room', ROOM);
if (urlParams.get('name')) localStorage.setItem('tm_name', USER);

// Keep the nav "Tasks" link carrying room/name
(function setTasksLinkFromStorage() {
  const tasksLink = document.querySelector('nav a[href="/tasks.html"]');
  const r = localStorage.getItem('tm_room');
  const n = localStorage.getItem('tm_name');
  if (tasksLink && r && n) {
    tasksLink.href = `/tasks.html?room=${encodeURIComponent(r)}&name=${encodeURIComponent(n)}`;
  }
})();

function withRoom(url) {
  const u = new URL(url, location.origin);
  if (ROOM) u.searchParams.set('room', ROOM);
  return u.pathname + u.search;
}

/* ========== Date helpers ========== */
function parseDueDate(raw) {
  if (!raw) return null;
  let s = String(raw).trim();
  if (s.includes(' ') && !s.includes('T')) s = s.replace(' ', 'T');
  if (s.includes('/') && !s.includes('-')) {
    const [dd, mm, yyyy] = s.split('/');
    if (dd && mm && yyyy) return new Date(Number(yyyy), Number(mm) - 1, Number(dd));
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
  const MIN = 60 * 1000, HOUR = 60 * MIN, DAY = 24 * HOUR;

  if (abs < HOUR) {
    const m = Math.max(1, Math.round(abs / MIN));
    return ms >= 0 ? `${plural(m, 'minute')} left` : `Overdue by ${plural(m, 'minute')}`;
  }
  if (abs < DAY) {
    const h = Math.round(abs / HOUR);
    return ms >= 0 ? `${plural(h, 'hour')} left (today)` : `Overdue by ${plural(h, 'hour')}`;
  }
  const d = Math.round(abs / DAY);
  return ms >= 0 ? `${plural(d, 'day')} left` : `Overdue by ${plural(d, 'day')}`;
}

function formatDateDMY(dateObj) {
  const dd = String(dateObj.getDate()).padStart(2, '0');
  const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
  const yyyy = dateObj.getFullYear();
  return `${dd}-${mm}-${yyyy}`;
}

/* ========== Clipboard fallback ========== */
function copyTextFallback(text) {
  const input = document.createElement("textarea");
  input.value = text;
  input.style.position = "fixed";
  input.style.opacity = "0";
  document.body.appendChild(input);
  input.focus();
  input.select();
  try {
    document.execCommand("copy");
  } catch (err) {
    console.error("Fallback copy failed", err);
  }
  document.body.removeChild(input);
}

/* ========== Load room & members (sidebar) ========== */
async function loadRoomInfo() {
  const codeEl = document.getElementById('room-code');
  const listEl = document.getElementById('member-list');
  const copyBtn = document.getElementById('copy-code');

  if (!ROOM) {
    if (codeEl) codeEl.textContent = 'Room: —';
    if (listEl) listEl.innerHTML = '<li>Join or create a room from the home page.</li>';
    return;
  }

  try {
    const room = await fetchJSON(`/rooms/${encodeURIComponent(ROOM)}`);
    if (codeEl) codeEl.textContent = `Room: ${room.code || ROOM}`;

    if (copyBtn) {
      copyBtn.onclick = async () => {
        const text = room.code || ROOM;
        try {
          if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
          } else {
            copyTextFallback(text);
          }
          copyBtn.textContent = "Copied!";
        } catch (err) {
          console.error("Copy failed:", err);
          copyBtn.textContent = "Copy failed";
        }
        setTimeout(() => (copyBtn.textContent = "Copy"), 1200);
      };
    }

    const members = Array.isArray(room.members) ? room.members : [];
    if (listEl) {
      if (members.length === 0) {
        listEl.innerHTML = '<li>No members yet.</li>';
      } else {
        listEl.innerHTML = members
          .map(name => {
            const me = USER && name && name.toLowerCase() === USER.toLowerCase();
            return `<li class="${me ? 'me' : ''}">
                      <span>${escapeHTML(name || 'Unknown')}</span>
                      ${me ? '<span class="badge">You</span>' : ''}
                    </li>`;
          })
          .join('');
      }
    }
  } catch (err) {
    if (listEl) listEl.innerHTML = `<li>${escapeHTML(err.message || 'Failed to load room')}</li>`;
  }
}

/* ========== Load tasks (main grid) ========== */
async function loadTasks() {
  if (!ROOM) {
    showError('Missing room code. Please enter via the landing page.');
    return;
  }
  showError('');
  try {
    const data = await fetchJSON(withRoom('/tasks'));
    const groups = {
      high: document.getElementById('high-body'),
      medium: document.getElementById('medium-body'),
      low: document.getElementById('low-body'),
      completed: document.getElementById('completed-body')
    };
    Object.values(groups).forEach(t => t && (t.innerHTML = ''));

    const now = new Date();

    (data.tasks || []).forEach(task => {
      let buttons = '';
      if (!task.completed) {
        buttons += `<button class="action-btn complete" data-action="complete">Complete</button>`;
      }
      buttons += `<button class="action-btn delete" data-action="delete">Delete</button>`;

      const row = document.createElement('tr');
      row.dataset.id = task.id;
      row.className = 'task-row' + (task.completed ? ' completed' : '');
      row.innerHTML = `<td><div class="task-title">${escapeHTML(task.title)}</div></td>`;

      const descRow = document.createElement('tr');
      descRow.className = 'desc-row';
      descRow.style.display = 'none';

      let dueInfo = '';
      if (task.due_date) {
        const dueDate = parseDueDate(task.due_date);
        if (dueDate) {
          const overdue = (!task.completed && dueDate < now);
          if (overdue) { row.classList.add('overdue'); descRow.classList.add('overdue'); }

          const tl = formatTimeLeft(dueDate);
          const tlClass = overdue ? 'time-left overdue' : 'time-left';
          const formattedDate = formatDateDMY(dueDate);

          dueInfo = `
            <div class="due-info">
              <span class="due-date"><small>Due: ${formattedDate}</small></span>
              <span class="${tlClass}">(${escapeHTML(tl)})</span>
            </div>
          `;
        }
      }

      descRow.innerHTML = `
        <td>
          <div class="desc-box">
            <div class="desc-content">${escapeHTML(task.description || '')}</div>
            ${dueInfo}
            <div class="actions below-title">${buttons}</div>
          </div>
        </td>
      `;

      const group = task.completed ? groups.completed : (groups[task.priority] || groups.medium);
      (group || groups.medium).appendChild(row);
      (group || groups.medium).appendChild(descRow);
    });

    const stats = await fetchJSON(withRoom('/tasks/stats'));
    const statsEl = document.getElementById('stats');
    if (statsEl) {
      statsEl.textContent = `Total: ${stats.total_tasks}, Completed: ${stats.completed_tasks}, Pending: ${stats.pending_tasks}, Overdue: ${stats.overdue_tasks}`;
    }
  } catch (err) {
    console.error(err);
  }
}

/* ========== Modal create task (if present) ========== */
const openModalBtn = document.getElementById('open-modal');
const closeModalBtn = document.getElementById('close-modal');
const modal = document.getElementById('task-modal');

if (openModalBtn && modal) {
  openModalBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
  });
}
if (closeModalBtn && modal) {
  closeModalBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
  });
}
const taskForm = document.getElementById('task-form');
if (taskForm) {
  taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const priority = document.getElementById('priority').value;
    const due_date = document.getElementById('due_date').value || null;

    try {
      await fetchJSON(withRoom('/tasks'), {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ title, description, priority, due_date })
      });
      e.target.reset();
      if (modal) {
        modal.classList.add('hidden');
        modal.setAttribute('aria-hidden', 'true');
      }
      loadTasks();
    } catch (err) {
      console.error(err);
    }
  });
}

/* ========== Click handling for rows & action buttons ========== */
document.getElementById('task-tables')?.addEventListener('click', async (e) => {
  const actionEl = e.target.closest('[data-action]');
  if (actionEl) {
    const descTr = actionEl.closest('tr');
    const parentRow = descTr?.previousElementSibling;
    const id = parentRow?.dataset.id;
    if (!id) return;

    const action = actionEl.dataset.action;
    try {
      if (action === 'delete') {
        await fetchJSON(withRoom(`/tasks/${id}`), { method: 'DELETE' });
      } else if (action === 'complete') {
        await fetchJSON(withRoom(`/tasks/${id}/complete`), { method: 'POST' });
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
      descRow.style.display = (descRow.style.display === 'table-row') ? 'none' : 'table-row';
    }
  }
});

/* ========== Init & live refresh ========== */
loadRoomInfo();
loadTasks();

setInterval(() => {
  loadRoomInfo();
  loadTasks();
}, 60000);
