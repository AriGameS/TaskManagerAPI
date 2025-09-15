// ----- Modal helpers -----
function openModal(id) {
  document.getElementById(id).classList.remove('hidden');
}
function closeModal(el) {
  el.closest('.modal').classList.add('hidden');
}

// Open modals
document.getElementById('join-btn').addEventListener('click', () => openModal('join-modal'));
document.getElementById('create-btn').addEventListener('click', () => openModal('create-modal'));

// Close with [x]
document.querySelectorAll('[data-close]').forEach(btn => {
  btn.addEventListener('click', () => closeModal(btn));
});
// Close by clicking backdrop
document.querySelectorAll('.modal').forEach(modal => {
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.add('hidden');
  });
});

// ----- API helper -----
async function postJSON(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body || {})
  });
  let data = null;
  try { data = await res.json(); } catch {}
  if (!res.ok) {
    const msg = data?.error || res.statusText || 'Request failed';
    throw new Error(msg);
  }
  return data;
}

// ----- Actions -----
async function handleCreate() {
  const nameEl = document.getElementById('create-name');
  const name = nameEl.value.trim();
  if (!name) { alert('Please enter your name.'); nameEl.focus(); return; }

  const btn = document.getElementById('create-room');
  btn.disabled = true;

  try {
    const data = await postJSON('/rooms', { username: name });
    const code = data.room_code;
    if (!code) throw new Error('No room code returned');

    // Persist for later navigations/refreshes
    localStorage.setItem('tm_room', code);
    localStorage.setItem('tm_name', name);

    // Redirect with params too (nice to have)
    window.location.href = `/tasks.html?room=${encodeURIComponent(code)}&name=${encodeURIComponent(name)}`;
  } catch (err) {
    alert(err.message || 'Failed to create room');
  } finally {
    btn.disabled = false;
  }
}

async function handleJoin() {
  const nameEl = document.getElementById('join-name');
  const codeEl = document.getElementById('join-code');
  const name = nameEl.value.trim();
  const code = codeEl.value.trim().toUpperCase();
  if (!name || !code) {
    alert('Please enter your name and the room code.');
    (!name ? nameEl : codeEl).focus();
    return;
  }

  const btn = document.getElementById('join-room');
  btn.disabled = true;

  try {
    await postJSON('/rooms/join', { username: name, room_code: code });

    // Persist
    localStorage.setItem('tm_room', code);
    localStorage.setItem('tm_name', name);

    window.location.href = `/tasks.html?room=${encodeURIComponent(code)}&name=${encodeURIComponent(name)}`;
  } catch (err) {
    alert(err.message || 'Failed to join room');
  } finally {
    btn.disabled = false;
  }
}

// Bind buttons
document.getElementById('create-room').addEventListener('click', handleCreate);
document.getElementById('join-room').addEventListener('click', handleJoin);

// Enter-to-submit in modals
document.getElementById('create-modal').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); handleCreate(); }
});
document.getElementById('join-modal').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); handleJoin(); }
});

// ----- Make the "Tasks" nav link smart -----
(function setTasksLinkFromStorage() {
  const tasksLink = document.querySelector('nav a[href="/tasks.html"]');
  const r = localStorage.getItem('tm_room');
  const n = localStorage.getItem('tm_name');
  if (tasksLink && r && n) {
    tasksLink.href = `/tasks.html?room=${encodeURIComponent(r)}&name=${encodeURIComponent(n)}`;
  }
})();
