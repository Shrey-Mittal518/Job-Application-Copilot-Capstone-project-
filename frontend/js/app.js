const API = 'http://127.0.0.1:8000';

// ── Auth helpers ──────────────────────────────────────────────
const Auth = {
  getToken:  () => localStorage.getItem('token'),
  setToken:  (t) => localStorage.setItem('token', t),
  getUser:   () => JSON.parse(localStorage.getItem('user') || 'null'),
  setUser:   (u) => localStorage.setItem('user', JSON.stringify(u)),
  clear:     () => { localStorage.removeItem('token'); localStorage.removeItem('user'); },
  isLoggedIn: () => !!localStorage.getItem('token'),
  requireAuth: () => {
    if (!Auth.isLoggedIn()) window.location.href = '/index.html';
  },
  redirectIfLoggedIn: () => {
    if (Auth.isLoggedIn()) window.location.href = '/pages/dashboard.html';
  }
};

// ── API fetch wrapper ─────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (res.status === 401) { Auth.clear(); window.location.href = '/index.html'; return; }
  const data = res.headers.get('content-type')?.includes('json') ? await res.json() : null;
  if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);
  return data;
}

// ── Toast ─────────────────────────────────────────────────────
function toast(msg, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${msg}</span>`;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ── Status badge ──────────────────────────────────────────────
const STATUS_META = {
  not_yet:     { label: 'Not Applied', cls: 'badge-gray'  },
  applied:     { label: 'Applied',     cls: 'badge-blue'  },
  interviewed: { label: 'Interviewed', cls: 'badge-amber' },
  rejected:    { label: 'Rejected',    cls: 'badge-red'   },
};
function statusBadge(status) {
  const m = STATUS_META[status] || STATUS_META.not_yet;
  return `<span class="badge ${m.cls}">${m.label}</span>`;
}

// ── Date helpers ──────────────────────────────────────────────
function fmtDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}
function followUpNote(date) {
  if (!date) return '';
  const diff = Math.ceil((new Date(date) - Date.now()) / 86400000);
  if (diff < 0)  return `<span class="follow-up">Follow-up overdue!</span>`;
  if (diff === 0) return `<span class="follow-up">Follow up today</span>`;
  return `<span class="follow-up">Follow up in ${diff}d</span>`;
}

// ── Sidebar ───────────────────────────────────────────────────
function initSidebar() {
  const user = Auth.getUser();
  if (user) {
    const nameEl   = document.getElementById('sidebar-user-name');
    const avatarEl = document.getElementById('sidebar-avatar');
    if (nameEl)   nameEl.textContent   = user.full_name;
    if (avatarEl) avatarEl.textContent = user.full_name?.[0]?.toUpperCase() || 'U';
  }
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.onclick = () => { Auth.clear(); window.location.href = '../index.html'; };
}

// ── Tabs ──────────────────────────────────────────────────────
function initTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = document.getElementById(tab.dataset.tab);
      if (panel) panel.classList.add('active');
    });
  });
}

// ── Diff renderer ─────────────────────────────────────────────
function renderDiff(beforeText, afterText) {
  return `
    <div class="diff-container">
      <div class="diff-panel">
        <div class="diff-panel-header before">✕ Original</div>
        <div class="diff-panel-body before">${escHtml(beforeText)}</div>
      </div>
      <div class="diff-panel">
        <div class="diff-panel-header after">✓ Rewritten</div>
        <div class="diff-panel-body after">${escHtml(afterText)}</div>
      </div>
    </div>`;
}

// ── Q&A renderer ─────────────────────────────────────────────
function renderQA(qaJson) {
  let questions = [];
  try {
    questions = typeof qaJson === 'string' ? JSON.parse(qaJson) : qaJson;
  } catch {
    return `<p class="text-muted">Could not parse Q&A. Try regenerating.</p>`;
  }
  return `<div class="qa-list">${questions.map((q, i) => `
    <div class="qa-item">
      <div class="qa-question" onclick="toggleQA(this)">
        <span class="qa-number">${i+1}</span>
        <span>${escHtml(q.question)}</span>
        <span class="qa-category">${escHtml(q.category || '')}</span>
      </div>
      <div class="qa-answer">${escHtml(q.answer)}</div>
    </div>`).join('')}</div>`;
}
function toggleQA(el) {
  el.nextElementSibling.classList.toggle('open');
}

// ── ATS renderer ──────────────────────────────────────────────
function renderATS(atsScore, atsMissingKw) {
  let ats = {};
  try { ats = JSON.parse(atsMissingKw || '{}'); } catch {}
  const score = atsScore || ats.score || 0;
  const color = score >= 75 ? 'var(--green)' : score >= 50 ? 'var(--amber)' : 'var(--red)';
  const bg    = score >= 75 ? 'var(--green-bg)' : score >= 50 ? 'var(--amber-bg)' : 'var(--red-bg)';

  const presentKw = (ats.present_keywords || []).map(k =>
    `<span class="kw-chip kw-present">${escHtml(k)}</span>`).join('');
  const missingKw = (ats.missing_keywords || []).map(k =>
    `<span class="kw-chip kw-missing">${escHtml(k)}</span>`).join('');
  const recs = (ats.recommendations || []).map(r =>
    `<li style="font-size:.85rem;margin-bottom:.3rem">${escHtml(r)}</li>`).join('');

  return `
    <div style="text-align:center">
      <div class="ats-ring" style="background:${bg};color:${color};border:4px solid ${color}">${score}</div>
      <div class="text-muted text-sm">ATS Score — ${ats.grade || ''}</div>
    </div>
    ${presentKw ? `<p class="text-sm text-muted" style="margin:.75rem 0 .4rem">✅ Present keywords</p><div class="kw-list">${presentKw}</div>` : ''}
    ${missingKw ? `<p class="text-sm text-muted" style="margin:.75rem 0 .4rem">❌ Missing keywords</p><div class="kw-list">${missingKw}</div>` : ''}
    ${recs ? `<p class="text-sm text-muted" style="margin:.75rem 0 .4rem">💡 Recommendations</p><ul style="padding-left:1.2rem">${recs}</ul>` : ''}`;
}

// ── Escape HTML ───────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Get role ID from URL ──────────────────────────────────────
function getRoleId() {
  return new URLSearchParams(window.location.search).get('role');
}