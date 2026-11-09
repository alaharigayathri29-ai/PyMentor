/**
 * Centralised API client for PyMentor.
 * All requests automatically attach JWT. User identity is derived strictly
 * on the backend from the verified token.
 */

const isLocalhost = Boolean(
  typeof window !== 'undefined' && (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '[::1]'
  )
);

const API_BASE = (typeof window !== 'undefined' && window.API_BASE) || (
  isLocalhost && window.location.port !== '8000'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : ''
);

export function getToken() {
  return localStorage.getItem('token');
}

export function setToken(token) {
  localStorage.setItem('token', token);
}

export function clearToken() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  sessionStorage.clear();
}

export function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem('user'));
  } catch {
    return null;
  }
}

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    window.dispatchEvent(new CustomEvent('auth:expired'));
    throw new Error('Session expired or unauthorized. Please sign in again.');
  }

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {}
    throw new Error(detail);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

export async function apiFormPost(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: new URLSearchParams(formData),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Auth API ─────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data) => apiFetch('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login:    (username, password) => apiFormPost('/api/auth/login', { username, password }),
  me:       () => apiFetch('/api/auth/me'),
};

// ── Assessment API ───────────────────────────────────────────────────────────
export const assessmentApi = {
  questions: (course = 'python') => apiFetch(`/api/assessment/questions?course=${encodeURIComponent(course)}`),
  submit:    (answers, course = 'python') => apiFetch(`/api/assessment/submit?course=${encodeURIComponent(course)}`, { method: 'POST', body: JSON.stringify({ answers }) }),
  result:    () => apiFetch('/api/assessment/result'),
};

// ── Learning Path & Curriculum API ───────────────────────────────────────────
export const learningPathApi = {
  get:             () => apiFetch('/api/learning-path/'),
  setTopic:        (topicId) => apiFetch(`/api/learning-path/set-topic/${topicId}`, { method: 'POST' }),
  curriculum:      () => apiFetch('/api/learning-path/curriculum'),
  getTopicLesson:  (topicId) => apiFetch(`/api/learning-path/topics/${topicId}`),
  completeLesson:  (topicId) => apiFetch(`/api/learning-path/topics/${topicId}/complete-lesson`, { method: 'POST' }),
};

// ── AI Mentor API ────────────────────────────────────────────────────────────
export const mentorApi = {
  status:        () => apiFetch('/api/mentor/status'),
  sessions:      () => apiFetch('/api/mentor/sessions'),
  newSession:    (title) => apiFetch('/api/mentor/sessions', { method: 'POST', body: JSON.stringify({ title }) }),
  messages:      (id) => apiFetch(`/api/mentor/sessions/${id}/messages`),
  send:          (id, content, action = null, language = 'en') => apiFetch(`/api/mentor/sessions/${id}/message`, {
    method: 'POST', body: JSON.stringify({ content, action, language }),
  }),
  sendMessage:   (id, content, action = null, language = 'en') => apiFetch(`/api/mentor/sessions/${id}/message`, {
    method: 'POST', body: JSON.stringify({ content, action, language }),
  }),
  deleteSession: (id) => apiFetch(`/api/mentor/sessions/${id}`, { method: 'DELETE' }),
};

// ── Practice Lab API ─────────────────────────────────────────────────────────
export const practiceApi = {
  problems:      (topicId, difficulty) => {
    const params = new URLSearchParams();
    if (topicId) params.set('topic_id', topicId);
    if (difficulty) params.set('difficulty', difficulty);
    return apiFetch(`/api/practice/problems?${params}`);
  },
  recommended:   () => apiFetch('/api/practice/problems/recommended'),
  problem:       (id) => apiFetch(`/api/practice/problems/${id}`),
  testRun:       (problemId, code, language = 'python') => apiFetch(`/api/practice/test-run/${problemId}?language=${encodeURIComponent(language)}`, {
    method: 'POST', body: JSON.stringify({ code }),
  }),
  submit:        (problemId, code, language = 'python') => apiFetch(`/api/practice/submissions/${problemId}?language=${encodeURIComponent(language)}`, {
    method: 'POST', body: JSON.stringify({ code }),
  }),
  mySubmissions: (problemId = null) => {
    const qs = problemId ? `?problem_id=${problemId}` : '';
    return apiFetch(`/api/practice/submissions${qs}`);
  },
};

// ── Progress API ─────────────────────────────────────────────────────────────
export const progressApi = {
  get:         () => apiFetch('/api/progress/'),
  leaderboard: () => apiFetch('/api/progress/leaderboard'),
};

// ── Workspace & Playground API ───────────────────────────────────────────────
export const workspaceApi = {
  listPrograms:  () => apiFetch('/api/workspace/programs'),
  getProgram:    (id) => apiFetch(`/api/workspace/programs/${id}`),
  createProgram: (data) => apiFetch('/api/workspace/programs', { method: 'POST', body: JSON.stringify(data) }),
  updateProgram: (id, data) => apiFetch(`/api/workspace/programs/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProgram: (id) => apiFetch(`/api/workspace/programs/${id}`, { method: 'DELETE' }),
  runCode:       (code, stdinInput = '', language = 'python') => apiFetch('/api/workspace/run', {
    method: 'POST', body: JSON.stringify({ code, stdin_input: stdinInput, language }),
  }),
};

// ── Admin API ────────────────────────────────────────────────────────────────
export const adminApi = {
  stats:           () => apiFetch('/api/admin/stats'),
  users:           (params = {}) => {
    const q = new URLSearchParams();
    if (params.q) q.set('q', params.q);
    if (params.skill_level) q.set('skill_level', params.skill_level);
    if (params.is_active !== undefined && params.is_active !== '') q.set('is_active', params.is_active);
    const qs = q.toString();
    return apiFetch(`/api/admin/users${qs ? '?' + qs : ''}`);
  },
  detail:          (id) => apiFetch(`/api/admin/users/${id}/detail`),
  submissions:     (id) => apiFetch(`/api/admin/users/${id}/submissions`),
  sessions:        (id) => apiFetch(`/api/admin/users/${id}/sessions`),
  toggle:          (id) => apiFetch(`/api/admin/users/${id}/toggle-active`, { method: 'PATCH' }),
  seedDemo:        () => apiFetch('/api/admin/seed-demo-students', { method: 'POST' }),
  getContentItems: () => apiFetch('/api/admin/content-items'),
  createProblem:   (data) => apiFetch('/api/admin/problems', { method: 'POST', body: JSON.stringify(data) }),
  deleteProblem:   (id) => apiFetch(`/api/admin/problems/${id}`, { method: 'DELETE' }),
  createQuestion:  (data) => apiFetch('/api/admin/questions', { method: 'POST', body: JSON.stringify(data) }),
  deleteQuestion:  (id) => apiFetch(`/api/admin/questions/${id}`, { method: 'DELETE' }),
};
