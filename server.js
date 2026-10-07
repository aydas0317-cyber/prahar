/**
 * PRAHAR Fullstack Server
 * Express + Socket.IO + SQLite + Authentication
 */
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const crypto = require('crypto');
const sqlite3 = require('better-sqlite3');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] },
  maxHttpBufferSize: 2e6,
});

app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname)));

// ===== DATABASE =====
const db = sqlite3(path.join(__dirname, 'prahar.db'));
db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT DEFAULT 'trainee',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE IF NOT EXISTS sessions (
    visitor_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
  CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT DEFAULT 'OP DEEP FOG',
    instructor_id INTEGER NOT NULL,
    status TEXT DEFAULT 'created',
    config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES users(id)
  );
  CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(exercise_id, user_id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
  CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    source TEXT,
    data TEXT,
    timestamp TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
  );
  CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    rationale TEXT,
    confidence INTEGER DEFAULT 50,
    intel_snapshot TEXT,
    info_count INTEGER,
    conflict_count INTEGER,
    comms_degraded_count INTEGER,
    timestamp TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
  CREATE TABLE IF NOT EXISTS aar_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
  );
  CREATE TABLE IF NOT EXISTS reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL,
    expires_at TIMESTAMP,
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
`);

// ===== AUTH HELPERS =====
const INSTRUCTOR_ACCESS_CODE = 'PRAHAR-2024'; // Demo instructor access code

function hashPassword(password, salt) {
  return crypto.scryptSync(password, salt, 64).toString('hex');
}
function generateSalt() {
  return crypto.randomBytes(16).toString('hex');
}
function generateCode() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}
function generateResetToken() {
  return crypto.randomBytes(16).toString('hex');
}

// Get visitor ID from request (proxy header or fallback)
function getVisitorId(req) {
  return (req.query && req.query.visitorId) ||
    (req.body && req.body.visitorId) ||
    req.headers['x-visitor-id'] ||
    (req.handshake && req.handshake.query && req.handshake.query.visitorId) ||
    `local-${req.ip}`;
}

// Get current user from session
function getCurrentUser(req) {
  const vid = getVisitorId(req);
  const session = db.prepare('SELECT user_id FROM sessions WHERE visitor_id = ?').get(vid);
  if (!session) return null;
  return db.prepare('SELECT id, username, role FROM users WHERE id = ?').get(session.user_id);
}

// Auth middleware
function requireAuth(req, res, next) {
  const user = getCurrentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  req.user = user;
  next();
}

// ===== IN-MEMORY EXERCISE STATE (for real-time sync) =====
const exerciseState = {}; // exerciseId -> { active, paused, startTime, duration, intelFeed, commsStatus, ... }

function getExerciseState(exId) {
  if (!exerciseState[exId]) {
    exerciseState[exId] = {
      active: false, paused: false, startTime: null, duration: 0,
      intelFeed: [], decisions: [], commsFailures: [],
      commsStatus: { alpha: 'normal', bravo: 'normal', air: 'normal' },
      weatherActive: false, threatUnits: [], phantomTracks: [], ewRings: [],
      cascades: [], falseFlagActive: false,
      reliabilityScore: 85, uncertaintyIndex: 15,
      flowStep: 1, config: { tempo: 'normal', infoLoss: 20, domains: { land: true, air: true, cyber: true, ew: true } },
      teamStatus: { commander: 'standby', cyber: 'standby', air: 'standby', intel: 'standby' },
    };
  }
  return exerciseState[exId];
}

function broadcastState(exId) {
  const state = getExerciseState(exId);
  io.to(`exercise-${exId}`).emit('state-update', { exerciseId: exId, ...state });
}

// ===== AUTH ROUTES =====
app.post('/api/auth/register', (req, res) => {
  const { username, password, role, instructorCode } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'Username and password required' });
  if (username.length < 3) return res.status(400).json({ error: 'Username must be at least 3 characters' });
  if (password.length < 4) return res.status(400).json({ error: 'Password must be at least 4 characters' });

  const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
  if (existing) return res.status(409).json({ error: 'Username already taken' });

  const userRole = role === 'instructor' ? 'instructor' : 'trainee';

  // Verify instructor access code
  if (userRole === 'instructor') {
    if (!instructorCode || instructorCode !== INSTRUCTOR_ACCESS_CODE) {
      return res.status(403).json({ error: 'Invalid instructor access code' });
    }
  }

  const salt = generateSalt();
  const hash = hashPassword(password, salt);

  const result = db.prepare('INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)').run(username, hash, salt, userRole);

  // Create session
  const vid = getVisitorId(req);
  db.prepare('INSERT OR REPLACE INTO sessions (visitor_id, user_id) VALUES (?, ?)').run(vid, result.lastInsertRowid);

  res.status(201).json({ id: result.lastInsertRowid, username, role: userRole });
});

// Get instructor access code (for demo — shown on login page)
app.get('/api/auth/instructor-code', (req, res) => {
  res.json({ code: INSTRUCTOR_ACCESS_CODE });
});

// Forgot password — request reset
app.post('/api/auth/forgot-password', (req, res) => {
  const { username } = req.body;
  if (!username) return res.status(400).json({ error: 'Username required' });

  const user = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
  if (!user) return res.status(404).json({ error: 'User not found' });

  // Generate reset token (valid for 30 minutes)
  const token = generateResetToken();
  const expires = new Date(Date.now() + 30 * 60 * 1000).toISOString();
  db.prepare('INSERT INTO reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)').run(user.id, token, expires);

  // For demo: return the token directly (in production this would be emailed)
  res.json({ success: true, message: 'Reset token generated', resetToken: token });
});

// Reset password with token
app.post('/api/auth/reset-password', (req, res) => {
  const { username, newPassword, resetToken } = req.body;
  if (!username || !newPassword) return res.status(400).json({ error: 'Username and new password required' });
  if (newPassword.length < 4) return res.status(400).json({ error: 'Password must be at least 4 characters' });

  const user = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
  if (!user) return res.status(404).json({ error: 'User not found' });

  // Verify reset token
  const tokenRow = db.prepare('SELECT * FROM reset_tokens WHERE user_id = ? AND token = ? AND used = 0 ORDER BY created_at DESC LIMIT 1').get(user.id, resetToken);
  if (!tokenRow) return res.status(401).json({ error: 'Invalid or expired reset token' });

  // Check expiry
  if (new Date(tokenRow.expires_at) < new Date()) {
    return res.status(401).json({ error: 'Reset token has expired' });
  }

  // Update password
  const salt = generateSalt();
  const hash = hashPassword(newPassword, salt);
  db.prepare('UPDATE users SET password_hash = ?, salt = ? WHERE id = ?').run(hash, salt, user.id);

  // Mark token as used
  db.prepare('UPDATE reset_tokens SET used = 1 WHERE id = ?').run(tokenRow.id);

  // Invalidate all sessions for this user
  db.prepare('DELETE FROM sessions WHERE user_id = ?').run(user.id);

  res.json({ success: true, message: 'Password reset successful. Please login with new password.' });
});

app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'Username and password required' });

  // Demo shortcut: if password matches the instructor access code,
  // auto-register, upgrade, or login as instructor with the given username
  if (password === INSTRUCTOR_ACCESS_CODE) {
    let user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
    if (!user) {
      const salt = generateSalt();
      const hash = hashPassword(password, salt);
      const result = db.prepare('INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)').run(username, hash, salt, 'instructor');
      user = { id: result.lastInsertRowid, username, role: 'instructor' };
    } else {
      // Upgrade existing trainee to instructor if not already
      if (user.role !== 'instructor') {
        db.prepare('UPDATE users SET role = ? WHERE id = ?').run('instructor', user.id);
        user.role = 'instructor';
      }
    }
    const vid = getVisitorId(req);
    db.prepare('INSERT OR REPLACE INTO sessions (visitor_id, user_id) VALUES (?, ?)').run(vid, user.id);
    return res.json({ id: user.id, username: user.username, role: user.role });
  }

  const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });

  const hash = hashPassword(password, user.salt);
  if (hash !== user.password_hash) return res.status(401).json({ error: 'Invalid credentials' });

  // Create session
  const vid = getVisitorId(req);
  db.prepare('INSERT OR REPLACE INTO sessions (visitor_id, user_id) VALUES (?, ?)').run(vid, user.id);

  res.json({ id: user.id, username: user.username, role: user.role });
});

app.get('/api/auth/me', (req, res) => {
  const user = getCurrentUser(req);
  if (!user) return res.status(401).json({ error: 'Not authenticated' });
  res.json(user);
});

app.post('/api/auth/logout', (req, res) => {
  const vid = getVisitorId(req);
  db.prepare('DELETE FROM sessions WHERE visitor_id = ?').run(vid);
  res.json({ success: true });
});

// ===== EXERCISE ROUTES =====
app.post('/api/exercises', requireAuth, (req, res) => {
  const { name, config } = req.body;
  const code = generateCode();
  const result = db.prepare('INSERT INTO exercises (code, name, instructor_id, config) VALUES (?, ?, ?, ?)').run(
    code, name || 'OP DEEP FOG', req.user.id, JSON.stringify(config || {})
  );
  const exId = result.lastInsertRowid;
  // Instructor auto-joins
  db.prepare('INSERT INTO participants (exercise_id, user_id, role) VALUES (?, ?, ?)').run(exId, req.user.id, 'instructor');
  getExerciseState(exId); // init state
  const exercise = db.prepare('SELECT * FROM exercises WHERE id = ?').get(exId);
  res.status(201).json({ ...exercise, code, state: getExerciseState(exId) });
});

app.get('/api/exercises', requireAuth, (req, res) => {
  const created = db.prepare(`
    SELECT e.*, p.role FROM exercises e
    JOIN participants p ON p.exercise_id = e.id
    WHERE p.user_id = ? ORDER BY e.created_at DESC
  `).all(req.user.id);
  res.json(created);
});

// List all available (non-ended) exercises for trainees to join
app.get('/api/exercises/available', requireAuth, (req, res) => {
  const exercises = db.prepare(`
    SELECT e.id, e.code, e.name, e.status, e.created_at,
           u.username AS instructor_name,
           (SELECT COUNT(*) FROM participants WHERE exercise_id = e.id) AS participant_count
    FROM exercises e
    JOIN users u ON u.id = e.instructor_id
    WHERE e.status != 'ended'
    ORDER BY e.created_at DESC
  `).all();
  res.json(exercises);
});

app.get('/api/exercises/:id', requireAuth, (req, res) => {
  const exId = parseInt(req.params.id);
  const exercise = db.prepare('SELECT * FROM exercises WHERE id = ?').get(exId);
  if (!exercise) return res.status(404).json({ error: 'Exercise not found' });
  const participants = db.prepare('SELECT p.*, u.username FROM participants p JOIN users u ON u.id = p.user_id WHERE p.exercise_id = ?').all(exId);
  const state = getExerciseState(exId);
  res.json({ ...exercise, participants, state });
});

app.post('/api/exercises/join', requireAuth, (req, res) => {
  const { code, role } = req.body;
  if (!code) return res.status(400).json({ error: 'Code required' });
  const exercise = db.prepare('SELECT * FROM exercises WHERE code = ?').get(code.toUpperCase());
  if (!exercise) return res.status(404).json({ error: 'Exercise not found' });
  if (exercise.status === 'ended') return res.status(400).json({ error: 'Exercise has ended' });

  // Check if already joined
  const existing = db.prepare('SELECT * FROM participants WHERE exercise_id = ? AND user_id = ?').get(exercise.id, req.user.id);
  if (existing) {
    // Update role
    db.prepare('UPDATE participants SET role = ? WHERE exercise_id = ? AND user_id = ?').run(role || existing.role, exercise.id, req.user.id);
  } else {
    db.prepare('INSERT INTO participants (exercise_id, user_id, role) VALUES (?, ?, ?)').run(exercise.id, req.user.id, role || 'commander');
  }

  const state = getExerciseState(exercise.id);
  res.json({ ...exercise, state });
});

// ===== EXERCISE CONTROL (Socket.IO events) =====
app.post('/api/exercises/:id/start', requireAuth, (req, res) => {
  const exId = parseInt(req.params.id);
  const exercise = db.prepare('SELECT * FROM exercises WHERE id = ?').get(exId);
  if (!exercise) return res.status(404).json({ error: 'Not found' });
  if (exercise.instructor_id !== req.user.id) return res.status(403).json({ error: 'Only instructor can start' });

  // Reset state
  const state = getExerciseState(exId);
  state.active = true; state.paused = false;
  state.startTime = Date.now(); state.duration = 0;
  state.intelFeed = []; state.decisions = []; state.commsFailures = [];
  state.commsStatus = { alpha: 'normal', bravo: 'normal', air: 'normal' };
  state.weatherActive = false; state.threatUnits = []; state.phantomTracks = []; state.ewRings = [];
  state.cascades = []; state.falseFlagActive = false;
  state.reliabilityScore = 85; state.uncertaintyIndex = 15; state.flowStep = 1;
  state.teamStatus = { commander: 'active', cyber: 'active', air: 'active', intel: 'active' };

  db.prepare('UPDATE exercises SET status = ?, started_at = CURRENT_TIMESTAMP WHERE id = ?').run('active', exId);
  db.prepare('INSERT INTO events (exercise_id, type, source, data, timestamp) VALUES (?, ?, ?, ?, ?)').run(exId, 'start', 'instructor', '{}', 'T+00:00:00');

  io.to(`exercise-${exId}`).emit('exercise-started', { exerciseId: exId, state });
  res.json({ success: true, state });
});

app.post('/api/exercises/:id/pause', requireAuth, (req, res) => {
  const exId = parseInt(req.params.id);
  const exercise = db.prepare('SELECT * FROM exercises WHERE id = ?').get(exId);
  if (!exercise || exercise.instructor_id !== req.user.id) return res.status(403).json({ error: 'Not authorized' });
  const state = getExerciseState(exId);
  state.paused = !state.paused;
  io.to(`exercise-${exId}`).emit('exercise-paused', { paused: state.paused });
  res.json({ success: true, paused: state.paused });
});

app.post('/api/exercises/:id/end', requireAuth, (req, res) => {
  const exId = parseInt(req.params.id);
  const exercise = db.prepare('SELECT * FROM exercises WHERE id = ?').get(exId);
  if (!exercise || exercise.instructor_id !== req.user.id) return res.status(403).json({ error: 'Not authorized' });
  const state = getExerciseState(exId);
  state.active = false;

  db.prepare('UPDATE exercises SET status = ?, ended_at = CURRENT_TIMESTAMP WHERE id = ?').run('ended', exId);
  db.prepare('INSERT INTO events (exercise_id, type, source, data, timestamp) VALUES (?, ?, ?, ?, ?)').run(exId, 'end', 'instructor', '{}', `T+${Math.floor(state.duration/3600).toString().padStart(2,'0')}:${Math.floor((state.duration%3600)/60).toString().padStart(2,'0')}:${(state.duration%60).toString().padStart(2,'0')}`);

  // Generate and persist AAR
  const aarData = generateAAR(exId, state, exercise);
  db.prepare('INSERT INTO aar_reports (exercise_id, data) VALUES (?, ?)').run(exId, JSON.stringify(aarData));

  io.to(`exercise-${exId}`).emit('exercise-ended', { exerciseId: exId, aar: aarData });
  res.json({ success: true, aar: aarData });
});

// ===== INJECT ROUTES =====
app.post('/api/exercises/:id/inject', requireAuth, (req, res) => {
  const exId = parseInt(req.params.id);
  const exercise = db.prepare('SELECT * FROM exercises WHERE id = ?').get(exId);
  if (!exercise || exercise.instructor_id !== req.user.id) return res.status(403).json({ error: 'Not authorized' });
  const state = getExerciseState(exId);
  if (!state.active) return res.status(400).json({ error: 'Exercise not active' });
  const { type } = req.body;
  if (!type) return res.status(400).json({ error: 'Type required' });

  const result = applyInject(exId, state, type);
  db.prepare('INSERT INTO events (exercise_id, type, source, data, timestamp) VALUES (?, ?, ?, ?, ?)').run(exId, 'inject', type, JSON.stringify(result), `T+${fmtClock(state.duration)}`);

  io.to(`exercise-${exId}`).emit('inject', { type, result, state });
  res.json({ success: true, result, state });
});

// ===== DECISION ROUTES =====
app.post('/api/exercises/:id/decision', requireAuth, (req, res) => {
  const exId = parseInt(req.params.id);
  const { action, rationale, confidence, intelSnapshot, infoCount, conflictCount, commsDegradedCount } = req.body;
  if (!action) return res.status(400).json({ error: 'Action required' });

  // Check for existing decision by this user in this exercise (prevent duplicates)
  const existing = db.prepare('SELECT * FROM decisions WHERE exercise_id = ? AND user_id = ? ORDER BY id DESC LIMIT 1').get(exId, req.user.id);
  if (existing) {
    // Return the existing decision instead of creating a duplicate
    const existingDecision = {
      id: existing.id, exerciseId: exId, userId: existing.user_id,
      username: req.user.username, action: existing.action, rationale: existing.rationale,
      confidence: existing.confidence, infoCount: existing.info_count, conflictCount: existing.conflict_count,
      commsDegradedCount: existing.comms_degraded_count, intelSnapshot: JSON.parse(existing.intel_snapshot || '[]'),
      timestamp: existing.timestamp,
      role: db.prepare('SELECT role FROM participants WHERE exercise_id = ? AND user_id = ?').get(exId, req.user.id)?.role || 'instructor',
    };
    return res.status(200).json({ success: true, decision: existingDecision, state: getExerciseState(exId), duplicate: true });
  }

  const state = getExerciseState(exId);
  const timestamp = `T+${fmtClock(state.duration)}`;

  const result = db.prepare('INSERT INTO decisions (exercise_id, user_id, action, rationale, confidence, intel_snapshot, info_count, conflict_count, comms_degraded_count, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)').run(
    exId, req.user.id, action, rationale || '', confidence || 50,
    JSON.stringify(intelSnapshot || []), infoCount || 0, conflictCount || 0, commsDegradedCount || 0, timestamp
  );

  // Look up participant role for team attribution
  const participant = db.prepare('SELECT role FROM participants WHERE exercise_id = ? AND user_id = ?').get(exId, req.user.id);
  const userRole = participant?.role || 'instructor';

  const decision = {
    id: result.lastInsertRowid, exerciseId: exId, userId: req.user.id,
    username: req.user.username, action, rationale, confidence: confidence || 50,
    infoCount: infoCount || 0, conflictCount: conflictCount || 0, commsDegradedCount: commsDegradedCount || 0,
    intelSnapshot: intelSnapshot || [], timestamp, role: userRole,
  };
  state.decisions.push(decision);
  state.flowStep = Math.max(state.flowStep, 4);

  db.prepare('INSERT INTO events (exercise_id, type, source, data, timestamp) VALUES (?, ?, ?, ?, ?)').run(exId, 'decision', req.user.username, JSON.stringify(decision), timestamp);

  io.to(`exercise-${exId}`).emit('decision-made', { decision, state });
  res.status(201).json({ success: true, decision, state });
});

// ===== AAR ROUTES =====
app.get('/api/aar/:id', requireAuth, (req, res) => {
  const exId = parseInt(req.params.id);
  const report = db.prepare('SELECT * FROM aar_reports WHERE exercise_id = ? ORDER BY created_at DESC LIMIT 1').get(exId);
  if (!report) return res.status(404).json({ error: 'AAR not found' });
  res.json({ ...JSON.parse(report.data), generatedAt: report.created_at });
});

app.get('/api/exercises/:id/events', requireAuth, (req, res) => {
  const exId = parseInt(req.params.id);
  const events = db.prepare('SELECT * FROM events WHERE exercise_id = ? ORDER BY id').all(exId);
  res.json(events);
});

// ===== AAR GENERATION =====
function generateAAR(exId, state, exercise) {
  const participants = db.prepare('SELECT p.*, u.username FROM participants p JOIN users u ON u.id = p.user_id WHERE p.exercise_id = ?').all(exId);
  const decisions = db.prepare('SELECT d.*, u.username, p.role FROM decisions d JOIN users u ON u.id = d.user_id LEFT JOIN participants p ON p.exercise_id = d.exercise_id AND p.user_id = d.user_id WHERE d.exercise_id = ? ORDER BY d.id').all(exId);
  const events = db.prepare('SELECT * FROM events WHERE exercise_id = ? ORDER BY id').all(exId);

  const has = decisions.length > 0;
  const fd = decisions[0] || {};
  const decScore = has ? Math.min(100, 60 + (fd.confidence || 50) * 0.3 + (fd.rationale && fd.rationale.length > 20 ? 10 : 0)) : 0;
  const resScore = has ? Math.max(20, 100 - Math.floor(state.duration / decisions.length / 2)) : 0;
  const infScore = has ? Math.min(100, 40 + (fd.info_count || 0) * 8) : 0;
  const cooScore = has ? Math.min(100, 50 + (state.cascades.length === 0 ? 30 : 10) + ((fd.confidence || 0) > 50 ? 20 : 0)) : 0;
  const avgScore = has ? Math.round((decScore + resScore + infScore + cooScore) / 4) : 0;

  return {
    scenario: exercise.name,
    exerciseId: exId,
    code: exercise.code,
    duration: `T+${fmtClock(state.duration)}`,
    participants: participants.map(p => ({ username: p.username, role: p.role })),
    scores: { decision: Math.round(decScore), response: Math.round(resScore), info: Math.round(infScore), coordination: Math.round(cooScore) },
    decisions: decisions.map(d => ({
      time: d.timestamp, action: d.action, confidence: d.confidence, rationale: d.rationale,
      infoCount: d.info_count, conflictCount: d.conflict_count, commsDegraded: d.comms_degraded_count,
      username: d.username, role: d.role || 'instructor', intelSnapshot: JSON.parse(d.intel_snapshot || '[]')
    })),
    commsFailures: state.commsFailures,
    cascades: state.cascades,
    intelFeed: state.intelFeed,
    events: events.map(e => ({ type: e.type, source: e.source, timestamp: e.timestamp, data: JSON.parse(e.data || '{}') })),
    generatedBy: 'PRAHAR Server',
  };
}

// ===== INJECT LOGIC =====
function fmtClock(s) {
  const h = Math.floor(s/3600).toString().padStart(2,'0');
  const m = Math.floor((s%3600)/60).toString().padStart(2,'0');
  const ss = (s%60).toString().padStart(2,'0');
  return `${h}:${m}:${ss}`;
}

function applyInject(exId, state, type) {
  const timestamp = `T+${fmtClock(state.duration)}`;

  // Comms degradation
  const commsMap = {
    delay: { label: 'COMMS DELAY', desc: '3-5s latency on all feeds', dur: 8000, status: 'delay' },
    blackout: { label: 'SIGNAL BLACKOUT', desc: 'Complete comms loss', dur: 10000, status: 'blackout' },
    packetloss: { label: 'PACKET LOSS', desc: '30% data drops', dur: 6000, status: 'packetloss' },
  };
  if (commsMap[type]) {
    const cfg = commsMap[type];
    state.commsStatus.alpha = cfg.status;
    state.commsStatus.bravo = cfg.status;
    state.commsStatus.air = cfg.status;
    state.commsFailures.push({ time: timestamp, type: cfg.label, description: cfg.desc });
    state.flowStep = Math.max(state.flowStep, 2);
    addIntel(state, 'warn', 'COMMS-NET', cfg.desc + ' — all channels affected.', 45);
    setTimeout(() => {
      if (state.active) {
        state.commsStatus.alpha = 'normal'; state.commsStatus.bravo = 'normal'; state.commsStatus.air = 'normal';
        addIntel(state, 'normal', 'COMMS-NET', 'Communications restored. All channels nominal.', 85);
        io.to(`exercise-${exId}`).emit('state-update', { exerciseId: exId, ...state });
      }
    }, cfg.dur);
    return { type: 'comms', ...cfg };
  }

  // Conflicts
  const conflictMap = {
    'conflict-air': {
      reports: [
        { source: 'AIR-1', msg: 'Radar: 2 hostile aircraft, bearing 270, range 40km.', rel: 85 },
        { source: 'SIGINT', msg: 'ELINT: 4 enemy aircraft, bearing 270, range 38km.', rel: 60 },
      ],
    },
    'conflict-cyber': {
      reports: [
        { source: 'CYBER-1', msg: 'EW threat: Adversary jamming rated LOW.', rel: 72 },
        { source: 'SIGINT', msg: 'SIGINT: ACTIVE jamming. EW threat HIGH.', rel: 55 },
      ],
    },
    'conflict-land': {
      reports: [
        { source: 'ALPHA-1', msg: 'Enemy at grid Golf-7-Bravo. Strength: platoon.', rel: 80 },
        { source: 'BRAVO-1', msg: 'No movement at Golf-7-Bravo. Possible false positive.', rel: 68 },
      ],
    },
  };
  if (conflictMap[type]) {
    const c = conflictMap[type];
    state.flowStep = Math.max(state.flowStep, 3);
    addIntel(state, 'conflict', c.reports[0].source, c.reports[0].msg, c.reports[0].rel);
    if (type === 'conflict-air') state.phantomTracks.push({ x: 500, y: 100, altX: 560, altY: 80 });
    if (type === 'conflict-cyber') state.ewRings.push({ x: 600, y: 220 });
    if (type === 'conflict-land') state.phantomTracks.push({ x: 640, y: 240, altX: 560, altY: 200 });
    setTimeout(() => {
      if (state.active) {
        addIntel(state, 'conflict', c.reports[1].source, c.reports[1].msg, c.reports[1].rel);
        addIntel(state, 'warn', 'SYSTEM', 'CONTRADICTORY INTEL DETECTED — Source reliability diverges.', 50);
        state.reliabilityScore = Math.round(state.reliabilityScore * 0.5 + 25);
        io.to(`exercise-${exId}`).emit('state-update', { exerciseId: exId, ...state });
      }
    }, 3000);
    return { type: 'conflict', reports: c.reports };
  }

  // Red-team / conditions
  const condMap = {
    weather: { source: 'METOC', msg: 'Visibility degrading to 500m. Sensor effectiveness -40%.', rel: 90, it: 'warn' },
    threat: { source: 'SIGINT', msg: 'NEW THREAT: Emerging adversary EW activity. Coordinated attack imminent.', rel: 65, it: 'critical' },
    falseflag: { source: 'RED-TEAM', msg: 'FALSE FLAG: Friendly units appearing as hostile on sensors. Spoofing detected.', rel: 40, it: 'critical' },
    overload: { source: 'RED-TEAM', msg: 'INFO OVERLOAD: 5 simultaneous intel feeds injected. Cognitive load critical.', rel: 30, it: 'critical' },
  };
  if (condMap[type]) {
    const c = condMap[type];
    addIntel(state, c.it, c.source, c.msg, c.rel);
    if (type === 'weather') state.weatherActive = true;
    if (type === 'threat') state.threatUnits.push({ x: 680, y: 180, label: 'NEW HOSTILE' });
    if (type === 'falseflag') state.falseFlagActive = true;
    if (type === 'overload') {
      for (let i = 0; i < 5; i++) {
        setTimeout(() => {
          if (state.active) addIntel(state, 'warn', 'AUTO-' + i, 'Priority feed ' + (i+1) + ': ' + ['Movement detected', 'EM spike', 'Comms intercept', 'Sensor anomaly', 'Unit status change'][i], 40 + Math.floor(Math.random()*30));
        }, i * 800);
      }
    }
    return { type: 'condition', ...c };
  }

  return { type: 'unknown' };
}

function addIntel(state, type, source, msg, rel) {
  state.intelFeed.push({ time: `T+${fmtClock(state.duration)}`, type, source, message: msg, reliability: rel });
  state.reliabilityScore = Math.round(state.reliabilityScore * 0.7 + rel * 0.3);
  const conflicts = state.intelFeed.filter(e => e.type === 'conflict').length;
  const comms = Object.values(state.commsStatus).filter(s => s !== 'normal').length;
  state.uncertaintyIndex = Math.min(100, conflicts * 20 + comms * 15 + Math.floor((state.config?.infoLoss || 20) / 2));
}

// ===== SOCKET.IO =====
io.on('connection', (socket) => {
  console.log('Socket connected:', socket.id);

  socket.on('join-exercise', ({ exerciseId, role, userId, username }) => {
    const exId = parseInt(exerciseId);
    socket.join(`exercise-${exId}`);
    socket.data.exerciseId = exId;
    socket.data.role = role;
    socket.data.userId = userId;
    socket.data.username = username;

    const state = getExerciseState(exId);
    if (role && role !== 'instructor') {
      state.teamStatus[role] = 'active';
    }
    socket.emit('state-update', { exerciseId: exId, ...state });
    io.to(`exercise-${exId}`).emit('team-update', { teamStatus: state.teamStatus, user: { username, role } });
    console.log(`User ${username} joined exercise ${exId} as ${role}`);
  });

  socket.on('leave-exercise', () => {
    const exId = socket.data.exerciseId;
    if (exId) {
      socket.leave(`exercise-${exId}`);
      const state = getExerciseState(exId);
      const role = socket.data.role;
      if (role && role !== 'instructor' && state.teamStatus[role]) {
        state.teamStatus[role] = 'standby';
        io.to(`exercise-${exId}`).emit('team-update', { teamStatus: state.teamStatus });
      }
    }
  });

  socket.on('intel-update', ({ exerciseId, intel }) => {
    const state = getExerciseState(parseInt(exerciseId));
    state.intelFeed.push(intel);
    io.to(`exercise-${exerciseId}`).emit('intel-update', { intel });
  });

  socket.on('role-selected', ({ exerciseId, role, username }) => {
    const state = getExerciseState(parseInt(exerciseId));
    if (role !== 'instructor' && state.teamStatus[role]) {
      state.teamStatus[role] = 'active';
    }
    io.to(`exercise-${exerciseId}`).emit('team-update', { teamStatus: state.teamStatus, user: { username, role } });
  });

  socket.on('disconnect', () => {
    const exId = socket.data.exerciseId;
    const role = socket.data.role;
    if (exId && role && role !== 'instructor') {
      const state = getExerciseState(exId);
      if (state.teamStatus[role]) {
        state.teamStatus[role] = 'standby';
        io.to(`exercise-${exId}`).emit('team-update', { teamStatus: state.teamStatus });
      }
    }
    console.log('Socket disconnected:', socket.id);
  });
});

// Timer tick for exercise duration
setInterval(() => {
  for (const [exId, state] of Object.entries(exerciseState)) {
    if (state.active && !state.paused && state.startTime) {
      state.duration = Math.floor((Date.now() - state.startTime) / 1000);
      // Auto-broadcast state every 5 seconds
      if (state.duration % 5 === 0) {
        io.to(`exercise-${exId}`).emit('tick', { duration: state.duration });
      }
    }
  }
}, 1000);

// ===== START SERVER =====
const PORT = 8000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`PRAHAR server running on port ${PORT}`);
});
