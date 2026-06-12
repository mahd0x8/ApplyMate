// ── Theme ──
function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeBtns(saved);
}
function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('theme', t);
  updateThemeBtns(t);
}
function updateThemeBtns(t) {
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === t);
  });
}

// ── Sidebar collapse ──
function initSidebar() {
  const collapsed = localStorage.getItem('sidebar') === '1';
  if (collapsed) document.querySelector('.sidebar')?.classList.add('collapsed');
}
function toggleSidebar() {
  const sb = document.querySelector('.sidebar');
  sb.classList.toggle('collapsed');
  localStorage.setItem('sidebar', sb.classList.contains('collapsed') ? '1' : '0');
}

// ── Modal ──
function openModal(id) {
  document.getElementById(id)?.classList.add('open');
}
function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
}
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
  }
});

// ── Toast ──
function showToast(message, type = 'success') {
  const colors = { success: '#22C55E', error: '#EF4444', info: '#94A3B8', ai: '#10B981', warning: '#F59E0B' };
  const color = colors[type] || '#10B981';
  const container = document.getElementById('toast-container') || (() => {
    const el = document.createElement('div');
    el.id = 'toast-container';
    el.className = 'toast-container';
    document.body.appendChild(el);
    return el;
  })();
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span class="toast-dot" style="background:${color}"></span>${message}`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ── Drag & Drop for Kanban ──
let dragCardId = null;
let dragCardEl = null;

function cardDragStart(e, cardId) {
  dragCardId = cardId;
  dragCardEl = e.currentTarget;
  e.currentTarget.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', cardId);
}
function cardDragEnd(e) {
  e.currentTarget.classList.remove('dragging');
  document.querySelectorAll('.kanban-col').forEach(c => c.classList.remove('drag-over'));
}
function colDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  e.currentTarget.classList.add('drag-over');
}
function colDragLeave(e) {
  if (!e.currentTarget.contains(e.relatedTarget)) {
    e.currentTarget.classList.remove('drag-over');
  }
}
function colDrop(e, status) {
  e.preventDefault();
  e.currentTarget.classList.remove('drag-over');
  const cardId = e.dataTransfer.getData('text/plain') || dragCardId;
  if (!cardId) return;

  const form = document.createElement('form');
  form.method = 'POST';
  form.action = `/applications/${cardId}/move/`;
  form.innerHTML = `<input name="csrfmiddlewaretoken" value="${getCsrf()}">
                    <input name="status" value="${status}">`;
  document.body.appendChild(form);
  form.submit();
}

function getCsrf() {
  return document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
}

// ── HTMX config ──
document.addEventListener('htmx:configRequest', (e) => {
  e.detail.headers['X-CSRFToken'] = getCsrf();
});

document.addEventListener('htmx:afterSwap', (e) => {
  // Auto-scroll chat to bottom
  const chat = document.querySelector('.chat-messages');
  if (chat) chat.scrollTop = chat.scrollHeight;
});

// ── Auto-resize textarea ──
document.addEventListener('input', (e) => {
  if (e.target.matches('.chat-input')) {
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  }
});

// ── Chat: submit on Enter (not Shift+Enter) ──
document.addEventListener('keydown', (e) => {
  if (e.target.matches('.chat-input') && e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    e.target.closest('form')?.requestSubmit();
  }
});

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebar();
});
