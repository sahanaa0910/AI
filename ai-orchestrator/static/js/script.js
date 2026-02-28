const $ = (sel) => document.querySelector(sel);

function toast(message) {
  const node = document.createElement('div');
  node.className = 'toast';
  node.textContent = message;
  $('#toast-container')?.appendChild(node);
  setTimeout(() => node.remove(), 3200);
}

function setLoading(isLoading) {
  const loader = $('#loader');
  if (!loader) return;
  loader.classList.toggle('hidden', !isLoading);
}

async function apiFetch(url, options = {}) {
  try {
    setLoading(true);
    const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  } finally {
    setLoading(false);
  }
}

async function loadDashboardStats() {
  if (!$('#total-students')) return;
  const data = await apiFetch('/api/dashboard/stats');
  $('#total-students').textContent = data.total_students;
  $('#pending-grading').textContent = data.pending_grading;
  $('#time-saved').textContent = `${data.weekly_saved_hours} hrs`;
  if ($('#workload-reduction')) $('#workload-reduction').textContent = `${data.workload_reduction_pct}%`;
  $('#progress-bar').style.width = `${data.progress_pct}%`;
  $('#progress-label').textContent = `${data.progress_pct}%`;
  const ul = $('#notifications');
  ul.innerHTML = '';
  if (!data.notifications.length) {
    ul.innerHTML = '<li>No new notifications</li>';
  }
  data.notifications.forEach((n) => {
    const li = document.createElement('li');
    li.textContent = n.message;
    ul.appendChild(li);
  });
}

async function handleLogin() {
  const form = $('#login-form');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    try {
      await apiFetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(Object.fromEntries(formData.entries())),
      });
      location.href = '/dashboard';
    } catch (err) { toast(err.message); }
  });
}

function setupTabs() {
  document.querySelectorAll('.sidebar nav a').forEach((a) => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      document.querySelectorAll('.panel').forEach((p) => p.classList.remove('visible'));
      $(`#${a.dataset.section}`)?.classList.add('visible');
    });
  });
}

function setupTheme() {
  $('#theme-toggle')?.addEventListener('click', () => {
    const html = document.documentElement;
    html.dataset.theme = html.dataset.theme === 'dark' ? 'light' : 'dark';
  });
}

function setupLogout() {
  $('#logout-btn')?.addEventListener('click', async () => {
    await apiFetch('/api/auth/logout', { method: 'POST' });
    location.href = '/login';
  });
}

function setupForms() {
  $('#grading-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    try {
      const data = await apiFetch('/api/grading/auto-grade', { method: 'POST', body: JSON.stringify(payload) });
      $('#grading-result').textContent = `Score: ${data.score}\nFeedback: ${data.feedback}`;
      toast('Assignment graded successfully');
      loadDashboardStats();
    } catch (err) { toast(err.message); }
  });

  $('#attendance-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    try {
      const data = await apiFetch('/api/attendance/mark', { method: 'POST', body: JSON.stringify(payload) });
      toast(data.message);
      e.target.reset();
      loadDashboardStats();
    } catch (err) { toast(err.message); }
  });

  $('#csv-upload-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    setLoading(true);
    try {
      const res = await fetch('/api/attendance/upload-csv', { method: 'POST', body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Upload failed');
      toast(data.message);
      loadDashboardStats();
    } catch (err) { toast(err.message); }
    setLoading(false);
  });

  $('#resource-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    try {
      const data = await apiFetch('/api/resources/recommend', { method: 'POST', body: JSON.stringify(payload) });
      const list = $('#resource-results');
      list.innerHTML = data.recommendations.map((r) => `<li>${r}</li>`).join('');
    } catch (err) { toast(err.message); }
  });

  $('#iep-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    try {
      const data = await apiFetch('/api/iep/generate', { method: 'POST', body: JSON.stringify(payload) });
      $('#iep-result').textContent = data.report;
      toast('IEP report generated');
    } catch (err) { toast(err.message); }
  });
}

(async function init() {
  handleLogin();
  setupTabs();
  setupTheme();
  setupLogout();
  setupForms();
  if ($('#total-students')) {
    try {
      await loadDashboardStats();
    } catch (err) {
      toast(err.message);
    }
  }
})();
