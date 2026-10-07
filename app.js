/* ===== SENTINEL-X V5 — FULLSTACK WITH REAL AUTH + MULTIPLAYER ===== */
(function () {
  'use strict';

  // API base — read from global set in HTML (gets port/8000 replaced at deploy time)
  const API = (window.SENTINEL_API && !String(window.SENTINEL_API).startsWith('__')) ? window.SENTINEL_API : 'http://localhost:8000';

  // Load Socket.IO client dynamically
  function loadSocketIO() {
    return new Promise((resolve, reject) => {
      if (window.io) { resolve(); return; }
      const script = document.createElement('script');
      script.src = API + '/socket.io/socket.io.js';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  let socket = null;
  let currentExercise = null;

  const state = {
    currentView: 'landing', role: 'instructor',
    user: null, // { id, username, role }
    exerciseActive: false, exercisePaused: false,
    exerciseStartTime: null, exerciseDuration: 0, timerInterval: null,
    intelFeed: [], decisions: [], commsFailures: [],
    selectedDecision: null, decisionStartTime: null,
    commsStatus: { alpha: 'normal', bravo: 'normal', air: 'normal' },
    weatherActive: false, threatUnits: [], phantomTracks: [], ewRings: [],
    decisionEffect: null, flowStep: 1,
    reliabilityScore: 85, uncertaintyIndex: 15,
    confidence: 50,
    cascades: [],
    scenarioConfig: { tempo: 'normal', infoLoss: 20, domains: { land: true, air: true, cyber: true, ew: true } },
    teamStatus: { commander: 'standby', cyber: 'standby', air: 'standby', intel: 'standby' },
    teamMembers: [], // connected users
    falseFlagActive: false,
    exerciseCode: null,
    exerciseId: null,
  };

  const ROLES = {
    instructor: { name: 'Instructor', color: 'var(--primary)' },
    commander: { name: 'Commander Alpha', color: 'var(--cyan)' },
    cyber: { name: 'Cyber / EW Officer', color: 'var(--warn)' },
    air: { name: 'Air Liaison', color: 'var(--cyan)' },
    intel: { name: 'Intel Analyst', color: 'var(--primary)' },
  };

  const UNITS = {
    alpha: { x: 180, y: 200, type: 'friendly', label: 'ALPHA', status: 'OK' },
    bravo: { x: 300, y: 320, type: 'friendly', label: 'BRAVO', status: 'OK' },
    air1: { x: 420, y: 120, type: 'friendly', label: 'AIR-1', status: 'OK' },
    hostile1: { x: 600, y: 220, type: 'hostile', label: 'HOSTILE', status: 'ACTIVE' },
    unknown1: { x: 620, y: 370, type: 'unknown', label: 'UNKNOWN', status: 'UNCONFIRMED' },
  };
  const COMMS_LINKS = [
    { from: 'alpha', to: 'bravo', id: 'link-ab' },
    { from: 'alpha', to: 'air1', id: 'link-aa' },
    { from: 'bravo', to: 'hostile1', id: 'link-bh' },
  ];

  // ===== API HELPERS =====
  let _visitorId = null;
  function getVisitorId() {
    if (_visitorId) return _visitorId;
    _visitorId = (window.crypto && crypto.randomUUID && crypto.randomUUID()) || 'v-' + Date.now() + '-' + Math.random().toString(36).slice(2);
    return _visitorId;
  }
  function withVisitor(path) {
    const sep = path.includes('?') ? '&' : '?';
    return path + sep + 'visitorId=' + encodeURIComponent(getVisitorId());
  }
  function applyExerciseState(s) {
    if (!s) return;
    Object.assign(state, s);
    if (typeof s.active === 'boolean') state.exerciseActive = s.active;
    if (typeof s.exerciseActive === 'boolean') state.exerciseActive = s.exerciseActive;
    if (typeof s.paused === 'boolean') state.paused = s.paused;
    if (typeof s.duration === 'number') state.duration = s.duration;
  }
  async function apiFetch(path, method = 'GET', body = null) {
    const opts = { method, headers: { 'X-Visitor-ID': getVisitorId() } };
    if (body) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
    try {
      const res = await fetch(API + withVisitor(path), opts);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'API error');
      return data;
    } catch (e) {
      console.error('API error:', path, e);
      throw e;
    }
  }

  // ===== AUTH =====
  async function register(username, password, role, instructorCode) {
    const result = await apiFetch('/api/auth/register', 'POST', { username, password, role, instructorCode });
    state.user = result;
    return result;
  }
  async function login(username, password) {
    const result = await apiFetch('/api/auth/login', 'POST', { username, password });
    state.user = result;
    return result;
  }
  async function checkAuth() {
    try {
      const result = await apiFetch('/api/auth/me');
      state.user = result;
      return result;
    } catch { return null; }
  }
  async function logout() {
    await apiFetch('/api/auth/logout', 'POST');
    state.user = null;
    if (socket) { socket.disconnect(); socket = null; }
  }
  async function fetchInstructorCode() {
    try {
      const result = await apiFetch('/api/auth/instructor-code');
      const el1 = document.getElementById('instructor-code-value');
      const el2 = document.getElementById('reg-instructor-code-hint');
      if (el1) el1.textContent = result.code;
      if (el2) el2.textContent = result.code;
    } catch (e) { /* ignore */ }
  }
  async function forgotPassword(username) {
    return await apiFetch('/api/auth/forgot-password', 'POST', { username });
  }
  async function resetPassword(username, newPassword, resetToken) {
    return await apiFetch('/api/auth/reset-password', 'POST', { username, newPassword, resetToken });
  }

  // ===== EXERCISE API =====
  async function createExercise(name, config) {
    const result = await apiFetch('/api/exercises', 'POST', { name, config });
    currentExercise = result;
    state.exerciseId = result.id;
    state.exerciseCode = result.code;
    return result;
  }
  async function joinExercise(code, role) {
    const result = await apiFetch('/api/exercises/join', 'POST', { code, role });
    currentExercise = result;
    state.exerciseId = result.id;
    state.exerciseCode = result.code;
    return result;
  }
  async function startExercise() {
    const result = await apiFetch(`/api/exercises/${state.exerciseId}/start`, 'POST');
    return result;
  }
  async function pauseExercise() {
    const result = await apiFetch(`/api/exercises/${state.exerciseId}/pause`, 'POST');
    return result;
  }
  async function endExercise() {
    const result = await apiFetch(`/api/exercises/${state.exerciseId}/end`, 'POST');
    return result;
  }
  async function inject(type) {
    const result = await apiFetch(`/api/exercises/${state.exerciseId}/inject`, 'POST', { type });
    return result;
  }
  async function submitDecisionAPI(action, rationale, confidence, intelSnapshot, infoCount, conflictCount, commsDegradedCount) {
    const result = await apiFetch(`/api/exercises/${state.exerciseId}/decision`, 'POST', {
      action, rationale, confidence, intelSnapshot, infoCount, conflictCount, commsDegradedCount
    });
    return result;
  }

  // ===== SOCKET.IO =====
  async function connectSocket(role) {
    await loadSocketIO();
    socket = io(API, { transports: ['websocket', 'polling'], query: { visitorId: getVisitorId() } });

    socket.on('connect', () => {
      console.log('Socket connected:', socket.id);
      if (state.exerciseId) {
        socket.emit('join-exercise', { exerciseId: state.exerciseId, role, userId: state.user?.id, username: state.user?.username });
      }
    });

    socket.on('state-update', (data) => {
      console.log('State update:', data);
      if (data.exerciseId !== state.exerciseId) return;
      // Sync state from server
      Object.assign(state, {
        intelFeed: data.intelFeed || state.intelFeed,
        decisions: data.decisions || state.decisions,
        commsFailures: data.commsFailures || state.commsFailures,
        commsStatus: data.commsStatus || state.commsStatus,
        weatherActive: data.weatherActive ?? state.weatherActive,
        threatUnits: data.threatUnits || state.threatUnits,
        phantomTracks: data.phantomTracks || state.phantomTracks,
        ewRings: data.ewRings || state.ewRings,
        cascades: data.cascades || state.cascades,
        falseFlagActive: data.falseFlagActive ?? state.falseFlagActive,
        reliabilityScore: data.reliabilityScore ?? state.reliabilityScore,
        uncertaintyIndex: data.uncertaintyIndex ?? state.uncertaintyIndex,
        flowStep: data.flowStep ?? state.flowStep,
        teamStatus: data.teamStatus || state.teamStatus,
        exerciseActive: data.active ?? state.exerciseActive,
        exercisePaused: data.paused ?? state.exercisePaused,
      });
      renderAllMap(); updateMapBadges(); renderIntel(); renderCascade(); updateTeamStatusUI(); updateEvaluatorUI();
      if (data.active) { showDecisionPanel(); } else { hideDecisionPanel(); }
    });

    socket.on('exercise-started', (data) => {
      if (data.exerciseId !== state.exerciseId) return;
      state.exerciseActive = true; state.exercisePaused = false;
      state.exerciseStartTime = Date.now();
      applyExerciseState(data.state);
      startClock(); setFlowStep(1); renderAllMap(); updateMapBadges(); renderCascade();
      setAllTeamStatus('active');
      showDecisionPanel();
      updateExStatus('live', 'EXERCISE ACTIVE');
    });

    socket.on('exercise-paused', (data) => {
      state.exercisePaused = data.paused;
      updateExStatus(state.exercisePaused ? 'warn' : 'live', state.exercisePaused ? 'PAUSED' : 'ACTIVE');
    });

    socket.on('exercise-ended', (data) => {
      if (data.exerciseId !== state.exerciseId) return;
      state.exerciseActive = false;
      stopClock(); setFlowStep(5);
      updateExStatus('offline', 'COMPLETE');
      setAllTeamStatus('standby');
      generateAARFromData(data.aar);
      switchView('aar');
    });

    socket.on('inject', (data) => {
      if (data.exerciseId !== state.exerciseId) return;
      applyExerciseState(data.state);
      renderAllMap(); updateMapBadges(); renderIntel(); renderCascade(); updateEvaluatorUI();
    });

    socket.on('decision-made', (data) => {
      if (data.exerciseId !== state.exerciseId) return;
      state.decisions = data.state.decisions;
      state.flowStep = Math.max(state.flowStep, 4);
      addDecLog(data.decision.timestamp, data.decision.action + ' (' + data.decision.confidence + '%) — ' + data.decision.username);
      updateTeamStatusUI();
    });

    socket.on('intel-update', (data) => {
      state.intelFeed.push(data.intel);
      renderIntel(); updateEvaluatorUI();
    });

    socket.on('team-update', (data) => {
      state.teamStatus = data.teamStatus;
      if (data.user) {
        const exists = state.teamMembers.find(m => m.username === data.user.username);
        if (!exists) state.teamMembers.push(data.user);
      }
      updateTeamStatusUI();
    });

    socket.on('tick', (data) => {
      state.exerciseDuration = data.duration;
      const clock = document.getElementById('clock');
      if (clock) clock.textContent = fmtClock(state.exerciseDuration);
      updateDecisionClock();
    });
  }

  // ===== VIEW =====
  function switchView(v) {
    state.currentView = v;
    document.querySelectorAll('.view').forEach(x => x.classList.remove('active'));
    document.getElementById('view-' + v)?.classList.add('active');
    window.scrollTo(0, 0);
    // Fetch instructor code for auth views
    if (v === 'login' || v === 'register' || v === 'forgot') {
      fetchInstructorCode();
    }
  }
  function scrollToSection(id) { document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' }); }

  // ===== CLOCK =====
  function fmtClock(s) {
    const h = Math.floor(s/3600).toString().padStart(2,'0');
    const m = Math.floor((s%3600)/60).toString().padStart(2,'0');
    const s2 = (s%60).toString().padStart(2,'0');
    return 'T+'+h+':'+m+':'+s2;
  }
  function startClock() {
    state.exerciseStartTime = Date.now() - state.exerciseDuration * 1000;
    if (state.timerInterval) clearInterval(state.timerInterval);
    state.timerInterval = setInterval(() => {
      if (state.exerciseActive && !state.exercisePaused) {
        state.exerciseDuration = Math.floor((Date.now()-state.exerciseStartTime)/1000);
        document.getElementById('clock').textContent = fmtClock(state.exerciseDuration);
        updateDecisionClock();
        checkCascade();
      }
    }, 1000);
  }
  function stopClock() { if (state.timerInterval) clearInterval(state.timerInterval); state.timerInterval = null; }

  function updateExStatus(status, text) {
    const d = document.getElementById('ex-dot'); const t = document.getElementById('ex-text');
    if (d) d.className = 'dot dot-' + status;
    if (t) t.textContent = text;
  }

  // ===== FLOW TIMELINE =====
  function setFlowStep(step) {
    state.flowStep = step;
    document.querySelectorAll('.ft-step').forEach(s => {
      const sn = parseInt(s.dataset.ft);
      s.classList.toggle('active', sn <= step);
    });
  }

  // ===== MAP RENDER =====
  function renderGrid() {
    const g = document.getElementById('grid-lines'); if (!g) return;
    let l = '';
    for (let x=0; x<=800; x+=40) l += `<line x1="${x}" y1="0" x2="${x}" y2="500"/>`;
    for (let y=0; y<=500; y+=40) l += `<line x1="0" y1="${y}" x2="800" y2="${y}"/>`;
    g.innerHTML = l;
  }
  function renderCoordLabels() {
    const c = document.getElementById('coord-labels'); if (!c) return;
    let t = '';
    for (let x=0; x<=800; x+=80) t += `<text x="${x}" y="12">${String.fromCharCode(65+x/80)}</text>`;
    for (let y=40; y<=500; y+=80) t += `<text x="4" y="${y}">${Math.floor(y/80)+1}</text>`;
    c.innerHTML = t;
  }
  function renderZones() {
    const z = document.getElementById('zones'); if (!z) return;
    z.innerHTML = `
      <rect x="120" y="100" width="120" height="80" fill="none" stroke="rgba(61,214,140,0.15)" stroke-width="1" stroke-dasharray="4,4" rx="4"/>
      <text x="180" y="95" fill="rgba(61,214,140,0.4)" font-size="8" font-family="Geist Mono" text-anchor="middle">OBJ ALPHA</text>
      <rect x="560" y="300" width="100" height="70" fill="none" stroke="rgba(239,68,68,0.15)" stroke-width="1" stroke-dasharray="4,4" rx="4"/>
      <text x="610" y="295" fill="rgba(239,68,68,0.4)" font-size="8" font-family="Geist Mono" text-anchor="middle">ENEMY ZONE</text>
    `;
  }
  function renderCommsLinks() {
    const l = document.getElementById('comms-links'); if (!l) return;
    let html = '';
    COMMS_LINKS.forEach(link => {
      const f = UNITS[link.from], t = UNITS[link.to]; if (!f || !t) return;
      const st = state.commsStatus[link.from] || 'normal';
      html += `<line class="comms-link comms-link-${st}" x1="${f.x}" y1="${f.y}" x2="${t.x}" y2="${t.y}"/>`;
    });
    l.innerHTML = html;
  }
  function renderUnits() {
    const u = document.getElementById('units'); if (!u) return;
    let html = '';
    Object.entries(UNITS).forEach(([key, unit]) => {
      const commKey = key === 'air1' ? 'air' : key;
      const down = state.commsStatus[commKey] === 'blackout';
      const stTxt = down ? 'NO SIGNAL' : unit.status;
      let displayType = unit.type;
      let displayLabel = unit.label;
      if (state.falseFlagActive && unit.type === 'friendly') {
        displayType = 'hostile';
        displayLabel = unit.label + '?';
      }
      html += `<g class="unit-group" id="unit-${key}" transform="translate(${unit.x},${unit.y})">
        <circle class="unit-pulse unit-pulse-${displayType} animate" cx="0" cy="0" r="12"/>
        <circle class="unit-circle unit-circle-${displayType}" cx="0" cy="0" r="14"/>
        <text class="unit-label unit-label-${displayType}" x="0" y="4">${displayLabel}</text>
        <text class="unit-status ${down ? 'unit-no-signal' : ''}" x="0" y="28">${stTxt}</text>
      </g>`;
    });
    u.innerHTML = html;
  }
  function renderThreats() {
    const t = document.getElementById('threats'); if (!t) return;
    let html = '';
    state.threatUnits.forEach(tr => {
      html += `<g class="threat-marker" transform="translate(${tr.x},${tr.y})">
        <circle class="unit-pulse unit-pulse-hostile animate" cx="0" cy="0" r="12"/>
        <circle class="unit-circle unit-circle-hostile" cx="0" cy="0" r="14"/>
        <text class="unit-label unit-label-hostile" x="0" y="4">${tr.label}</text>
      </g>`;
    });
    state.phantomTracks.forEach(tr => {
      html += `<g class="threat-marker" transform="translate(${tr.x},${tr.y})">
        <circle cx="0" cy="0" r="16" fill="none" stroke="var(--warn)" stroke-width="1.5" stroke-dasharray="3,3" opacity="0.6"/>
        <text x="0" y="4" font-size="14" fill="var(--warn)" text-anchor="middle" font-family="Geist Mono" font-weight="700">?</text>
        <text x="0" y="28" font-size="7" fill="var(--warn)" text-anchor="middle" font-family="Geist Mono">UNCONFIRMED</text>
      </g>`;
      if (tr.altX) html += `<line class="phantom-track" x1="${tr.x}" y1="${tr.y}" x2="${tr.altX}" y2="${tr.altY}" stroke="var(--warn)"/>`;
    });
    state.ewRings.forEach(r => {
      html += `<circle class="ew-ring" cx="${r.x}" cy="${r.y}" r="30"/>
        <circle class="ew-ring" cx="${r.x}" cy="${r.y}" r="45" style="animation-delay:.5s"/>
        <text x="${r.x}" y="${r.y-50}" font-size="7" fill="var(--purple)" text-anchor="middle" font-family="Geist Mono">EW JAMMING</text>`;
    });
    t.innerHTML = html;
  }
  function renderEffects() {
    const e = document.getElementById('effects'); if (!e) return;
    let html = '';
    if (state.weatherActive) {
      html += `<rect class="weather-overlay" x="0" y="0" width="800" height="500"/>`;
      for (let i=0; i<5; i++) {
        const x = 100+i*140, y = 50+(i%3)*150;
        html += `<ellipse cx="${x}" cy="${y}" rx="80" ry="40" fill="rgba(90,107,128,0.06)"/>`;
      }
    }
    if (state.role === 'cyber') {
      html += `<circle cx="600" cy="220" r="60" fill="none" stroke="rgba(168,85,247,0.15)" stroke-width="1" stroke-dasharray="2,4"/>`;
      html += `<text x="600" y="160" font-size="7" fill="var(--purple)" text-anchor="middle" font-family="Geist Mono">EW SPECTRUM</text>`;
    } else if (state.role === 'air') {
      html += `<path d="M 100 80 Q 300 60 500 100 T 800 80" fill="none" stroke="rgba(6,182,212,0.1)" stroke-width="1" stroke-dasharray="4,8"/>`;
      html += `<text x="400" y="70" font-size="7" fill="var(--cyan)" text-anchor="middle" font-family="Geist Mono">AIR CORRIDOR A</text>`;
    } else if (state.role === 'intel') {
      html += `<text x="180" y="230" font-size="7" fill="var(--primary)" text-anchor="middle" font-family="Geist Mono">REL: 85%</text>`;
      html += `<text x="600" y="250" font-size="7" fill="var(--crit)" text-anchor="middle" font-family="Geist Mono">REL: 55%</text>`;
    }
    e.innerHTML = html;
  }
  function renderDecisionFx() {
    const d = document.getElementById('decision-fx'); if (!d) return;
    if (!state.decisionEffect) { d.innerHTML = ''; return; }
    const fx = state.decisionEffect; let html = '';
    if (fx.type === 'attack') {
      html += `<path class="attack-vector" d="M ${UNITS.air1.x} ${UNITS.air1.y} L ${UNITS.hostile1.x} ${UNITS.hostile1.y}"/>`;
      html += `<path class="attack-vector" d="M ${UNITS.alpha.x} ${UNITS.alpha.y} L ${UNITS.hostile1.x} ${UNITS.hostile1.y}"/>`;
      moveUnit('air1', UNITS.hostile1.x-40, UNITS.hostile1.y-20);
      moveUnit('alpha', UNITS.hostile1.x-60, UNITS.hostile1.y+10);
    } else if (fx.type === 'recon') {
      html += `<path class="recon-path" d="M ${UNITS.alpha.x} ${UNITS.alpha.y} L ${UNITS.unknown1.x} ${UNITS.unknown1.y}"/>`;
      moveUnit('alpha', UNITS.unknown1.x-40, UNITS.unknown1.y);
    } else if (fx.type === 'defend') {
      html += `<circle class="defensive-perimeter" cx="${UNITS.alpha.x}" cy="${UNITS.alpha.y}" r="50"/>`;
      html += `<circle class="defensive-perimeter" cx="${UNITS.bravo.x}" cy="${UNITS.bravo.y}" r="50"/>`;
      html += `<circle class="defensive-perimeter" cx="${UNITS.air1.x}" cy="${UNITS.air1.y}" r="40"/>`;
    } else if (fx.type === 'retreat') {
      html += `<path class="retreat-path" d="M ${UNITS.alpha.x} ${UNITS.alpha.y} L 80 180"/>`;
      html += `<path class="retreat-path" d="M ${UNITS.bravo.x} ${UNITS.bravo.y} L 100 350"/>`;
      moveUnit('alpha', 80, 180);
      moveUnit('bravo', 100, 350);
    }
    d.innerHTML = html;
  }
  function moveUnit(key, nx, ny) {
    const u = UNITS[key]; if (!u) return;
    u.x = nx; u.y = ny;
    const el = document.getElementById('unit-'+key);
    if (el) el.setAttribute('transform', `translate(${nx},${ny})`);
    setTimeout(() => renderCommsLinks(), 100);
  }
  function renderAllMap() {
    renderGrid(); renderCoordLabels(); renderZones(); renderCommsLinks();
    renderUnits(); renderThreats(); renderEffects(); renderDecisionFx();
  }

  // ===== COMMS BADGES =====
  function updateMapBadges() {
    const o = document.getElementById('map-badges'); if (!o) return;
    let html = '';
    const active = Object.entries(state.commsStatus).filter(([k,v]) => v !== 'normal');
    active.forEach(([u, s]) => {
      const labels = { delay: 'LATENCY', blackout: 'SIGNAL LOST', packetloss: 'PACKET LOSS' };
      const crit = s === 'blackout';
      html += `<div class="map-badge ${crit ? 'map-badge-crit' : ''}">${labels[s]||s.toUpperCase()} — ${u.toUpperCase()}</div>`;
    });
    if (state.falseFlagActive) {
      html += `<div class="map-badge map-badge-crit">FALSE FLAG — FRIENDLIES MISLABELED</div>`;
    }
    o.innerHTML = html;
    Object.entries(state.commsStatus).forEach(([u, s]) => {
      const d = document.getElementById('dot-'+u);
      if (d) { const ds = s==='normal'?'live':s==='blackout'?'crit':'warn'; d.className = 'dot dot-'+ds; }
    });
    const cond = document.getElementById('map-cond');
    if (cond) {
      const parts = [];
      if (active.length > 0) parts.push('COMMS DEGRADED');
      if (state.weatherActive) parts.push('WEATHER');
      if (state.threatUnits.length > 0 || state.phantomTracks.length > 0) parts.push('ACTIVE THREATS');
      if (state.falseFlagActive) parts.push('FALSE FLAG');
      cond.textContent = 'CONDITIONS: ' + (parts.length > 0 ? parts.join(' | ') : 'NOMINAL');
    }
  }

  // ===== INTEL FEED =====
  function addIntel(type, source, msg, rel) {
    state.intelFeed.push({ time: fmtClock(state.exerciseDuration), type, source, message: msg, reliability: rel });
    renderIntel(); updateEvaluatorUI();
  }
  function renderIntel() {
    const f = document.getElementById('intel-feed'); if (!f) return;
    if (state.intelFeed.length === 0) { f.innerHTML = '<div class="feed-empty">Awaiting exercise start...</div>'; return; }
    let feed = state.intelFeed;
    if (state.role === 'cyber') {
      feed = state.intelFeed.filter(e => e.source.includes('CYBER') || e.source.includes('SIGINT') || e.source.includes('COMMS') || e.source.includes('SYSTEM') || e.type === 'conflict');
    } else if (state.role === 'air') {
      feed = state.intelFeed.filter(e => e.source.includes('AIR') || e.source.includes('SIGINT') || e.source.includes('COMMS') || e.source.includes('SYSTEM') || e.type === 'conflict');
    }
    f.innerHTML = feed.slice().reverse().map(e => {
      const rl = e.reliability>=80?'HIGH':e.reliability>=50?'MEDIUM':'LOW';
      const rc = e.reliability>=80?'var(--primary)':e.reliability>=50?'var(--warn)':'var(--crit)';
      return `<div class="intel-entry intel-${e.type}">
        <div class="intel-entry-time">${e.time}</div>
        <div>${e.message}</div>
        <div class="intel-entry-source">SRC: ${e.source}</div>
        <div class="intel-entry-reliability"><span style="color:${rc}">●</span> RELIABILITY: ${rl} (${e.reliability}%)</div>
      </div>`;
    }).join('');
  }

  // ===== EVALUATOR =====
  function updateEvaluatorUI() {
    const m = document.getElementById('meter-rel'); const v = document.getElementById('val-rel');
    if (m) m.style.width = state.reliabilityScore + '%';
    if (v) v.textContent = state.reliabilityScore + '%';
    const um = document.getElementById('meter-unc'); const uv = document.getElementById('val-unc');
    if (um) um.style.width = state.uncertaintyIndex + '%';
    if (uv) uv.textContent = state.uncertaintyIndex < 30 ? 'LOW' : state.uncertaintyIndex < 60 ? 'MEDIUM' : 'HIGH';
  }
  function updateDecisionClock() {
    if (!state.exerciseActive || !state.decisionStartTime) return;
    const elapsed = Math.floor((Date.now()-state.decisionStartTime)/1000);
    const pct = Math.min(100, (elapsed/60)*100);
    const m = document.getElementById('meter-clk'); const v = document.getElementById('val-clk');
    if (m) { m.style.width = pct+'%'; m.className = 'eval-fill ' + (pct>75?'eval-fill-cyan':pct>50?'eval-fill-amber':'eval-fill-green'); }
    if (v) { const mm = Math.floor(elapsed/60).toString().padStart(2,'0'); const ss = (elapsed%60).toString().padStart(2,'0'); v.textContent = mm+':'+ss; }
  }
  function updateConfidenceMeter() {
    const m = document.getElementById('meter-conf'); const v = document.getElementById('val-conf');
    if (m) { m.style.width = state.confidence + '%'; m.className = 'eval-fill ' + (state.confidence>70?'eval-fill-green':state.confidence>40?'eval-fill-amber':'eval-fill-cyan'); }
    if (v) v.textContent = state.confidence + '%';
  }

  // ===== DECISION LOG =====
  function addDecLog(time, action) {
    const l = document.getElementById('dec-log'); if (!l) return;
    const e = l.querySelector('.dec-log-empty'); if (e) e.remove();
    const i = document.createElement('div'); i.className = 'dec-log-item';
    i.innerHTML = `<div class="dec-log-time">${time}</div><div class="dec-log-action">${action}</div>`;
    l.insertBefore(i, l.firstChild);
  }

  // ===== TEAM STATUS =====
  function updateTeamStatusUI() {
    Object.entries(state.teamStatus).forEach(([member, status]) => {
      const ids = { commander: 'tm-cmd', cyber: 'tm-cyb', air: 'tm-air', intel: 'tm-int' };
      const el = document.getElementById(ids[member]);
      if (el) {
        el.textContent = status.toUpperCase();
        const parent = el.closest('.team-member');
        const dot = parent?.querySelector('.tm-dot');
        if (dot) {
          const cls = status === 'active' ? 'dot-live' : status === 'degraded' ? 'dot-warn' : status === 'decision' ? 'dot-crit' : 'dot-live';
          dot.className = 'tm-dot ' + cls;
        }
      }
    });
    // Update connected members list
    const teamNote = document.querySelector('.team-note');
    if (teamNote) {
      const count = state.teamMembers.length;
      teamNote.textContent = count > 0
        ? `${count} user${count > 1 ? 's' : ''} connected — real-time sync active via Socket.IO`
        : 'Connected to server — waiting for team members...';
    }
  }
  function setAllTeamStatus(status) {
    Object.keys(state.teamStatus).forEach(m => { state.teamStatus[m] = status; });
    updateTeamStatusUI();
  }

  // ===== CASCADE DETECTION =====
  function checkCascade() {
    const commsDegraded = Object.values(state.commsStatus).filter(s => s !== 'normal').length;
    const conflicts = state.intelFeed.filter(e => e.type === 'conflict').length;
    const intelOverload = state.intelFeed.length > 8;
    if ((commsDegraded >= 2 && conflicts >= 1) || (intelOverload && commsDegraded >= 1)) {
      const existing = state.cascades.find(c => c.type === 'overload');
      if (!existing) {
        state.cascades.push({
          time: fmtClock(state.exerciseDuration),
          type: 'overload',
          description: 'Cascade triggered: comms degraded + conflicting intel overload detected. Decision accuracy at risk.',
          triggers: `${commsDegraded} comms failures, ${conflicts} conflicts, ${state.intelFeed.length} intel entries`
        });
        renderCascade();
        addIntel('critical', 'SYSTEM', 'CASCADE WARNING: Self-reinforcing degradation detected. Multiple failures compounding.', 30);
      }
    }
  }
  function renderCascade() {
    const c = document.getElementById('cascade-panel'); if (!c) return;
    if (state.cascades.length === 0) { c.innerHTML = '<div class="cascade-empty">No cascades detected.</div>'; return; }
    c.innerHTML = state.cascades.map(cs => `<div class="cascade-item ${cs.type === 'overload' ? 'cascade-crit' : ''}"><div class="cascade-time">${cs.time}</div><div class="cascade-desc">${cs.description}</div><div class="cascade-trig">${cs.triggers}</div></div>`).join('');
  }

  // ===== SCENARIO CONFIG =====
  function initScenarioConfig() {
    const tempo = document.getElementById('cfg-tempo');
    const infoloss = document.getElementById('cfg-infoloss');
    const infolossVal = document.getElementById('cfg-infoloss-val');
    if (tempo) tempo.addEventListener('change', e => { state.scenarioConfig.tempo = e.target.value; });
    if (infoloss) infoloss.addEventListener('input', e => { state.scenarioConfig.infoLoss = parseInt(e.target.value); if (infolossVal) infolossVal.textContent = e.target.value + '%'; });
    document.querySelectorAll('.cfg-domain').forEach(d => {
      d.addEventListener('click', () => {
        const dom = d.dataset.domain;
        state.scenarioConfig.domains[dom] = !state.scenarioConfig.domains[dom];
        d.classList.toggle('cfg-domain-off');
        const check = d.querySelector('.cfg-check');
        if (check) check.style.visibility = state.scenarioConfig.domains[dom] ? 'visible' : 'hidden';
      });
    });
  }

  // ===== EXERCISE CODE DISPLAY =====
  function showExerciseCode(code) {
    state.exerciseCode = code;
    // Update scenario label to show the code
    const sl = document.getElementById('scenario-lbl');
    if (sl) sl.textContent = code + ' — OP DEEP FOG';
    // Update any code display elements
    document.querySelectorAll('[data-exercise-code]').forEach(el => { el.textContent = code; });
    // Show a visible code banner in the app header
    let banner = document.getElementById('code-banner');
    if (!banner) {
      banner = document.createElement('div');
      banner.id = 'code-banner';
      banner.style.cssText = 'background:rgba(255,182,39,0.15);border:1px solid var(--accent);color:var(--accent);padding:6px 12px;border-radius:4px;font-family:var(--font-mono);font-size:13px;text-align:center;margin:4px 0';
      const header = document.getElementById('app-header') || document.querySelector('#view-app .app-topbar');
      if (header) header.insertAdjacentHTML('afterend', banner.outerHTML);
    }
    banner.textContent = 'EXERCISE CODE: ' + code + ' — Share this code with trainees';
  }

  // ===== EXERCISE CONTROL =====
  async function handleStart() {
    try {
      await startExercise();
      // Local state init for instructor
      state.exerciseActive = true; state.exercisePaused = false;
      state.exerciseStartTime = Date.now();
      state.intelFeed = []; state.decisions = []; state.commsFailures = [];
      state.commsStatus = { alpha: 'normal', bravo: 'normal', air: 'normal' };
      state.weatherActive = false; state.threatUnits = []; state.phantomTracks = []; state.ewRings = [];
      state.cascades = []; state.falseFlagActive = false;
      state.reliabilityScore = 85; state.uncertaintyIndex = 15; state.flowStep = 1;
      UNITS.alpha.x = 180; UNITS.alpha.y = 200;
      UNITS.bravo.x = 300; UNITS.bravo.y = 320;
      UNITS.air1.x = 420; UNITS.air1.y = 120;
      updateExStatus('live', 'EXERCISE ACTIVE');
      startClock(); setFlowStep(1); renderAllMap(); updateMapBadges(); renderCascade();
      setAllTeamStatus('active');
      showDecisionPanel();
      state.decisionStartTime = Date.now();
      // Auto intel sequence
      const tempoMs = { slow: 30000, normal: 15000, fast: 8000 }[state.scenarioConfig.tempo];
      setTimeout(() => { if (state.exerciseActive) addIntel('normal', 'ALPHA-1', 'All units in position. Sector Golf-7 secured.', 88); }, 500);
      setTimeout(() => { if (state.exerciseActive) addIntel('normal', 'AIR-1', 'Air patrol nominal. No hostile air activity.', 92); }, Math.floor(tempoMs*0.15));
      setTimeout(() => { if (state.exerciseActive) addIntel('normal', 'BRAVO-1', 'Ground sensors active. No movement detected.', 78); }, Math.floor(tempoMs*0.25));
      setTimeout(() => { if (state.exerciseActive) addIntel('warn', 'SIGINT', 'Intermittent EM emissions — possible EW activity bearing 045.', 65); }, Math.floor(tempoMs*0.4));
      setTimeout(() => { if (state.exerciseActive) handleInject('delay'); }, Math.floor(tempoMs*0.8));
      setTimeout(() => { if (state.exerciseActive) handleInject('conflict-air'); }, Math.floor(tempoMs*1.3));
      setTimeout(() => { if (state.exerciseActive) handleInject('weather'); }, Math.floor(tempoMs*1.9));
    } catch (e) { alert('Failed to start: ' + e.message); }
  }
  async function handlePause() {
    try { await pauseExercise(); } catch (e) {}
    state.exercisePaused = !state.exercisePaused;
    updateExStatus(state.exercisePaused?'warn':'live', state.exercisePaused?'PAUSED':'ACTIVE');
  }
  async function handleEnd() {
    try {
      const result = await endExercise();
      state.exerciseActive = false;
      stopClock(); setFlowStep(5);
      updateExStatus('offline', 'COMPLETE');
      setAllTeamStatus('standby');
      generateAARFromData(result.aar);
      switchView('aar');
    } catch (e) { alert('Failed to end: ' + e.message); }
  }
  async function handleInject(type) {
    try {
      const result = await inject(type);
      applyExerciseState(result.state);
      renderAllMap(); updateMapBadges(); renderIntel(); renderCascade(); updateEvaluatorUI();
    } catch (e) { console.error('Inject failed:', e); }
  }

  function showDecisionPanel() {
    const p = document.getElementById('dp-prompt'); const o = document.getElementById('dp-options');
    if (p) p.style.display = 'none'; if (o) o.style.display = 'grid';
  }
  function hideDecisionPanel() {
    const p = document.getElementById('dp-prompt'); const o = document.getElementById('dp-options');
    if (p) p.style.display = 'block'; if (o) o.style.display = 'none';
  }

  // ===== DECISIONS =====
  function selectDecision(d) {
    state.selectedDecision = d;
    document.querySelectorAll('.dp-option').forEach(o => {
      o.style.borderColor = o.dataset.decision === d ? 'var(--primary)' : 'var(--border)';
      o.style.background = o.dataset.decision === d ? 'var(--surface3)' : 'var(--surface2)';
    });
    const conf = document.getElementById('dp-confidence');
    const rat = document.getElementById('dp-rationale');
    const snap = document.getElementById('dp-snapshot');
    if (conf) conf.style.display = 'block';
    if (rat) rat.style.display = 'flex';
    if (snap) { snap.style.display = 'block'; document.getElementById('snap-count').textContent = state.intelFeed.length; }
  }
  async function submitDecision() {
    if (!state.selectedDecision) return;
    const r = document.getElementById('rat-input')?.value.trim() || '';
    const labels = { attack: 'Engage Hostile', recon: 'Deploy Recon', defend: 'Fortify Position', retreat: 'Tactical Withdrawal' };
    const effects = {
      attack: 'Attack vectors plotted on map. Air and ground assets moving to engage hostile.',
      recon: 'Recon team deployed. Path drawn on map. Intel confidence will update.',
      defend: 'Defensive perimeter established around friendly positions.',
      retreat: 'Units executing tactical withdrawal to secondary waypoints.',
    };
    const intelSnapshot = state.intelFeed.map(e => ({ time: e.time, source: e.source, message: e.message, reliability: e.reliability }));
    const infoCount = state.intelFeed.length;
    const conflictCount = state.intelFeed.filter(e => e.type === 'conflict').length;
    const commsDegradedCount = Object.values(state.commsStatus).filter(s => s !== 'normal').length;

    try {
      const result = await submitDecisionAPI(labels[state.selectedDecision], r, state.confidence, intelSnapshot, infoCount, conflictCount, commsDegradedCount);
      addDecLog(result.decision.timestamp, result.decision.action + ' (' + result.decision.confidence + '%)');
      setFlowStep(4);
      state.decisionEffect = { type: state.selectedDecision };
      renderDecisionFx();
      const ep = document.getElementById('dp-effect');
      if (ep) { ep.style.display = 'block'; ep.innerHTML = `<div class="dp-effect-title">DECISION EFFECT</div><div>${effects[state.selectedDecision]}</div><div class="dp-effect-conf">Confidence: ${state.confidence}% | Intel used: ${infoCount} | Conflicts: ${conflictCount}</div>`; }
      addIntel('normal', 'SYSTEM', 'Decision logged: ' + labels[state.selectedDecision] + ' at ' + state.confidence + '% confidence. Rationale + intel snapshot captured for AAR.', 100);
    } catch (e) {
      // Fallback: local only
      addDecLog(fmtClock(state.exerciseDuration), labels[state.selectedDecision] + ' (' + state.confidence + '%)');
    }
    state.selectedDecision = null;
    document.querySelectorAll('.dp-option').forEach(o => { o.style.borderColor = ''; o.style.background = ''; });
    const ri = document.getElementById('rat-input'); if (ri) ri.value = '';
    document.getElementById('dp-confidence').style.display = 'none';
    document.getElementById('dp-rationale').style.display = 'none';
    document.getElementById('dp-snapshot').style.display = 'none';
    state.decisionStartTime = Date.now();
  }

  // ===== AAR =====
  function generateAARFromData(aar) {
    if (!aar) { generateAARLocal(); return; }
    document.getElementById('aar-name').textContent = aar.scenario || 'OP DEEP FOG';
    document.getElementById('aar-meta').textContent = `Code: ${aar.code} | Duration: ${aar.duration} | Participants: ${(aar.participants||[]).map(p=>p.username).join(', ')}`;
    const s = aar.scores || {};
    setScore('dec', s.decision || 0);
    setScore('res', s.response || 0);
    setScore('inf', s.info || 0);
    setScore('coo', s.coordination || 0);
    renderAARTimeline(aar);
    renderAARCascade(aar);
    renderAARComms(aar);
    renderAARAIEval(aar);
    renderAARImp(aar);
    // Store for export
    state.currentAAR = aar;
  }
  function generateAARLocal() {
    const role = ROLES[state.role] || { name: 'Trainee' };
    document.getElementById('aar-name').textContent = 'OP DEEP FOG';
    document.getElementById('aar-meta').textContent = `Duration: ${fmtClock(state.exerciseDuration)} | Trainee: ${role.name}`;
    const has = state.decisions.length > 0;
    setScore('dec', has ? Math.min(100, 60 + state.confidence * 0.3) : 0);
    setScore('res', has ? Math.max(20, 100 - Math.floor(state.exerciseDuration / 2)) : 0);
    setScore('inf', has ? Math.min(100, 40 + state.intelFeed.length * 8) : 0);
    setScore('coo', has ? Math.min(100, 50 + (state.cascades.length === 0 ? 30 : 10)) : 0);
    renderAARTimelineLocal(); renderAARCascadeLocal(); renderAARCommsLocal(); renderAARAIEvalLocal(); renderAARImpLocal();
    state.currentAAR = buildLocalAARData();
  }
  function setScore(k, v) {
    const e = document.getElementById('sc-'+k); const b = document.getElementById('sb-'+k);
    if (e) e.textContent = v > 0 ? v+'/100' : '—';
    if (b) setTimeout(() => { b.style.width = v+'%'; }, 200);
  }
  function renderAARTimeline(aar) {
    const c = document.getElementById('aar-tl'); if (!c) return;
    const events = [];
    (aar.commsFailures||[]).forEach(f => events.push({ t: f.time, e: f.type, d: f.description }));
    (aar.decisions||[]).forEach(d => events.push({ t: d.time, e: d.action + ' (' + d.confidence + '%)', d: 'Rationale: ' + d.rationale + ' | Intel: ' + d.infoCount + ' entries | Conflicts: ' + d.conflictCount }));
    (aar.cascades||[]).forEach(cs => events.push({ t: cs.time, e: 'CASCADE', d: cs.description }));
    if (events.length === 0) { c.innerHTML = '<div class="aar-empty">No events recorded.</div>'; return; }
    c.innerHTML = events.map(e => `<div class="timeline-item"><div class="timeline-time">${e.t}</div><div class="timeline-event">${e.e}</div><div class="timeline-detail">${e.d}</div></div>`).join('');
  }
  function renderAARCascade(aar) {
    const c = document.getElementById('aar-cascade'); if (!c) return;
    if (!aar.cascades || aar.cascades.length === 0) { c.innerHTML = '<div class="aar-empty">No cascades detected. Good information management.</div>'; return; }
    c.innerHTML = aar.cascades.map(cs => `<div class="comms-log-item cascade-aar-item"><span class="comms-log-time">${cs.time}</span><span class="comms-log-type cascade-type">CASCADE</span><span>${cs.description} <em>(${cs.triggers})</em></span></div>`).join('');
  }
  function renderAARComms(aar) {
    const c = document.getElementById('aar-comms'); if (!c) return;
    if (!aar.commsFailures || aar.commsFailures.length === 0) { c.innerHTML = '<div class="aar-empty">No failures recorded.</div>'; return; }
    c.innerHTML = aar.commsFailures.map(f => `<div class="comms-log-item"><span class="comms-log-time">${f.time}</span><span class="comms-log-type">${f.type}</span><span>${f.description}</span></div>`).join('');
  }
  function renderAARAIEval(aar) {
    const c = document.getElementById('aar-ai'); if (!c) return;
    if (!aar.decisions || aar.decisions.length === 0) { c.innerHTML = '<div class="aar-empty">No evaluation available.</div>'; return; }
    const fd = aar.decisions[0];
    const avg = aar.scores ? Math.round((aar.scores.decision + aar.scores.response + aar.scores.info + aar.scores.coordination) / 4) : 0;
    const rating = avg>=80?'EXCELLENT':avg>=65?'PROFICIENT':avg>=50?'DEVELOPING':'NEEDS RETRAINING';
    const rc = avg>=80?'var(--primary)':avg>=65?'var(--cyan)':avg>=50?'var(--warn)':'var(--crit)';
    let f = [];
    if (fd.infoCount > 5) f.push('Trainee effectively utilized ' + fd.infoCount + ' intelligence sources.');
    else f.push('Trainee underutilized intelligence. Only ' + fd.infoCount + ' entries processed.');
    if (fd.conflictCount > 0) f.push('Contradictory intelligence was present (' + fd.conflictCount + ' conflicts).');
    if (aar.cascades && aar.cascades.length > 0) f.push('Cascade detected. Consider training on prioritization under overload.');
    f.push('Decision confidence was ' + fd.confidence + '% — ' + (fd.confidence > 70 && fd.infoCount < 5 ? 'possibly overconfident given limited intel.' : 'appropriate for available information.'));
    f.push('Intel snapshot captured ' + (fd.intelSnapshot||[]).length + ' entries at decision time for "what did you know" evaluation.');
    c.innerHTML = `<div class="ai-eval-header"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h6v6H9z"/></svg><span>LOCAL AI EVALUATOR — ANALYSIS COMPLETE</span></div><div class="ai-eval-summary">Overall: <strong style="color:${rc}">${rating}</strong> (${avg}/100).<br/>Primary decision: <strong>${fd.action}</strong> at ${fd.time} (${fd.confidence}% confidence).<br/>${fd.infoCount} intel entries, ${fd.conflictCount} contradictory, ${aar.commsFailures?.length||0} comms failures, ${aar.cascades?.length||0} cascades.<br/>All evaluation performed locally. No data transmitted externally.</div><div class="ai-eval-findings">${f.map(x=>`<div class="ai-eval-finding"><span class="ai-eval-finding-icon">▸</span><span>${x}</span></div>`).join('')}</div>`;
  }
  function renderAARImp(aar) {
    const c = document.getElementById('aar-imp'); if (!c) return;
    if (!aar.decisions || aar.decisions.length === 0) { c.innerHTML = '<div class="aar-empty">Complete an exercise.</div>'; return; }
    let im = [];
    const fd = aar.decisions[0];
    if (fd.confidence > 70 && fd.infoCount < 5) im.push('Reduce overconfidence when intel is limited — seek more sources before committing.');
    if ((aar.commsFailures||[]).length > 2) im.push('Practice decision-making under sustained comms degradation.');
    if ((aar.cascades||[]).length > 0) im.push('Improve prioritization to prevent cascade overload scenarios.');
    im.push('Continue training on asymmetric information handling across team roles.');
    im.push('Practice capturing rationale concisely under time pressure.');
    c.innerHTML = im.map((x,i) => `<div class="improvement-item"><span class="improvement-number">${(i+1).toString().padStart(2,'0')}</span><span class="improvement-text">${x}</span></div>`).join('');
  }
  // Local fallbacks
  function renderAARTimelineLocal() {
    const c = document.getElementById('aar-tl'); if (!c) return;
    const ev = [];
    state.commsFailures.forEach(f => ev.push({ t: f.time, e: f.type, d: f.description }));
    state.decisions.forEach(d => ev.push({ t: d.time, e: d.action + ' (' + d.confidence + '%)', d: 'Rationale: ' + d.rationale }));
    state.cascades.forEach(cs => ev.push({ t: cs.time, e: 'CASCADE', d: cs.description }));
    if (ev.length === 0) { c.innerHTML = '<div class="aar-empty">No events recorded.</div>'; return; }
    c.innerHTML = ev.map(e => `<div class="timeline-item"><div class="timeline-time">${e.t}</div><div class="timeline-event">${e.e}</div><div class="timeline-detail">${e.d}</div></div>`).join('');
  }
  function renderAARCascadeLocal() {
    const c = document.getElementById('aar-cascade'); if (!c) return;
    if (state.cascades.length === 0) { c.innerHTML = '<div class="aar-empty">No cascades detected.</div>'; return; }
    c.innerHTML = state.cascades.map(cs => `<div class="comms-log-item cascade-aar-item"><span class="comms-log-time">${cs.time}</span><span class="comms-log-type cascade-type">CASCADE</span><span>${cs.description} <em>(${cs.triggers})</em></span></div>`).join('');
  }
  function renderAARCommsLocal() {
    const c = document.getElementById('aar-comms'); if (!c) return;
    if (state.commsFailures.length === 0) { c.innerHTML = '<div class="aar-empty">No failures recorded.</div>'; return; }
    c.innerHTML = state.commsFailures.map(f => `<div class="comms-log-item"><span class="comms-log-time">${f.time}</span><span class="comms-log-type">${f.type}</span><span>${f.description}</span></div>`).join('');
  }
  function renderAARAIEvalLocal() {
    const c = document.getElementById('aar-ai'); if (!c) return;
    if (state.decisions.length === 0) { c.innerHTML = '<div class="aar-empty">No evaluation available.</div>'; return; }
    c.innerHTML = '<div class="aar-empty">Evaluation available in full mode.</div>';
  }
  function renderAARImpLocal() {
    const c = document.getElementById('aar-imp'); if (!c) return;
    if (state.decisions.length === 0) { c.innerHTML = '<div class="aar-empty">Complete an exercise.</div>'; return; }
    c.innerHTML = '<div class="improvement-item"><span class="improvement-number">01</span><span class="improvement-text">Continue training.</span></div>';
  }
  function buildLocalAARData() {
    return {
      scenario: 'OP DEEP FOG', duration: fmtClock(state.exerciseDuration),
      decisions: state.decisions, commsFailures: state.commsFailures,
      cascades: state.cascades, intelFeed: state.intelFeed,
    };
  }

  // ===== EXPORT =====
  function buildAARData() {
    return state.currentAAR || buildLocalAARData();
  }
  function exportAARHTML() {
    const d = buildAARData();
    const html = `<!DOCTYPE html><html><head><title>Sentinel-X AAR — ${d.scenario}</title><style>
      body{font-family:'Segoe UI',system-ui,sans-serif;background:#04060d;color:#c8d4e0;padding:40px;max-width:900px;margin:0 auto}
      h1{color:#3dd68c;font-family:monospace;border-bottom:2px solid #1a2438;padding-bottom:10px}
      h2{color:#3dd68c;font-family:monospace;border-bottom:1px solid #1a2438;padding-bottom:8px;margin-top:32px;font-size:16px}
      .meta{font-family:monospace;font-size:12px;color:#5a6b80;margin-bottom:24px}
      table{width:100%;border-collapse:collapse;margin:12px 0}
      td,th{padding:10px;border:1px solid #1a2438;text-align:left;font-size:13px}
      th{color:#3dd68c;font-family:monospace;background:#0c1320}
      .footer{margin-top:40px;padding-top:16px;border-top:1px solid #1a2438;font-size:11px;color:#5a6b80;font-family:monospace}
    </style></head><body>
      <h1>SENTINEL-X — AFTER-ACTION REPORT</h1>
      <div class="meta">Scenario: ${d.scenario} | Duration: ${d.duration} | Code: ${d.code || 'N/A'}</div>
      <h2>Decisions</h2>
      <table><tr><th>Time</th><th>User</th><th>Decision</th><th>Confidence</th><th>Rationale</th></tr>
      ${(d.decisions||[]).map(dec=>`<tr><td>${dec.time||dec.timestamp}</td><td>${dec.username||'—'}</td><td>${dec.action}</td><td>${dec.confidence}%</td><td>${dec.rationale||'—'}</td></tr>`).join('') || '<tr><td colspan=5>None</td></tr>'}</table>
      <h2>Cascade Analysis</h2>
      ${(d.cascades||[]).length > 0 ? d.cascades.map(cs=>`<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:6px;padding:12px;margin:8px 0"><strong>${cs.time} — CASCADE</strong><br>${cs.description}<br><em>Triggers: ${cs.triggers}</em></div>`).join('') : '<p>No cascades detected.</p>'}
      <h2>Communication Failures</h2>
      <table><tr><th>Time</th><th>Type</th><th>Description</th></tr>
      ${(d.commsFailures||[]).map(f=>`<tr><td>${f.time}</td><td>${f.type}</td><td>${f.description}</td></tr>`).join('') || '<tr><td colspan=3>None</td></tr>'}</table>
      <h2>Intel Feed</h2>
      <table><tr><th>Time</th><th>Source</th><th>Message</th><th>Reliability</th></tr>
      ${(d.intelFeed||[]).map(e=>`<tr><td>${e.time}</td><td>${e.source}</td><td>${e.message}</td><td>${e.reliability}%</td></tr>`).join('') || '<tr><td colspan=4>None</td></tr>'}</table>
      <div class="footer">Generated by Sentinel-X Server. All evaluation performed on-premise.</div>
    </body></html>`;
    downloadFile('Sentinel-X-AAR-' + Date.now() + '.html', html, 'text/html');
  }
  function exportAARJSON() {
    const d = buildAARData();
    downloadFile('Sentinel-X-AAR-' + Date.now() + '.json', JSON.stringify(d, null, 2), 'application/json');
  }
  function downloadFile(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 100);
  }

  // ===== AUTH UI =====
  function showAuthError(msg) {
    // Try the error div for the currently visible auth view
    const view = state.currentView;
    let el = null;
    if (view === 'register') el = document.getElementById('reg-auth-error');
    else if (view === 'forgot') el = document.getElementById('forgot-auth-error');
    else el = document.getElementById('auth-error');
    if (el) { el.textContent = msg; el.style.color = ''; el.style.display = 'block'; setTimeout(() => { el.style.display = 'none'; }, 5000); }
  }

  // ===== EVENTS =====
  document.addEventListener('click', function (e) {
    const t = e.target.closest('[data-action],[data-role],[data-inject],[data-decision],[data-scroll],[data-auth],[data-exercise],[data-quick-join],[data-open-exercise]');
    if (!t) return;
    const a = t.dataset.action, r = t.dataset.role, inj = t.dataset.inject, dec = t.dataset.decision, sc = t.dataset.scroll;
    const auth = t.dataset.auth, exAction = t.dataset.exercise, quickJoin = t.dataset.quickJoin, openEx = t.dataset.openExercise;

    if (auth) {
      e.preventDefault();
      if (auth === 'register') {
        const u = document.getElementById('reg-username')?.value;
        const p = document.getElementById('reg-password')?.value;
        const role = document.getElementById('reg-role')?.value || 'trainee';
        const instructorCode = document.getElementById('reg-instructor-code')?.value || '';
        if (!u || !p) { showAuthError('Username and password required'); return; }
        if (role === 'instructor' && !instructorCode) { showAuthError('Instructor access code required'); return; }
        register(u, p, role, instructorCode).then(() => {
          switchView('login');
          document.getElementById('login-username').value = u;
        }).catch(err => showAuthError(err.message));
      } else if (auth === 'login') {
        const u = document.getElementById('login-username')?.value;
        const p = document.getElementById('login-password')?.value;
        if (!u || !p) { showAuthError('Username and password required'); return; }
        login(u, p).then(user => {
          state.user = user;
          switchView('lobby');
          renderLobby();
        }).catch(err => showAuthError(err.message));
      } else if (auth === 'go-register') switchView('register');
      else if (auth === 'go-login') switchView('login');
      else if (auth === 'go-forgot') switchView('forgot');
      else if (auth === 'forgot-request') {
        const u = document.getElementById('forgot-username')?.value;
        if (!u) { showAuthError('Username required'); return; }
        const errEl = document.getElementById('forgot-auth-error');
        forgotPassword(u).then(result => {
          document.getElementById('forgot-step1').style.display = 'none';
          document.getElementById('forgot-step2').style.display = 'block';
          document.getElementById('forgot-token').value = result.resetToken || '';
        }).catch(err => {
          if (errEl) { errEl.textContent = err.message; errEl.style.display = 'block'; setTimeout(() => { errEl.style.display = 'none'; }, 5000); }
        });
      } else if (auth === 'forgot-reset') {
        const u = document.getElementById('forgot-username')?.value;
        const np = document.getElementById('forgot-new-password')?.value;
        const rt = document.getElementById('forgot-token')?.value;
        if (!u || !np || !rt) { showAuthError('All fields required'); return; }
        const errEl = document.getElementById('forgot-auth-error');
        resetPassword(u, np, rt).then(() => {
          if (errEl) { errEl.textContent = 'Password reset successful! Redirecting to login...'; errEl.style.color = 'var(--primary)'; errEl.style.display = 'block'; }
          setTimeout(() => { switchView('login'); document.getElementById('login-username').value = u; }, 2000);
        }).catch(err => {
          if (errEl) { errEl.textContent = err.message; errEl.style.display = 'block'; setTimeout(() => { errEl.style.display = 'none'; }, 5000); }
        });
      } else if (auth === 'logout') {
        logout().then(() => { switchView('landing'); });
      }
      return;
    }

    if (quickJoin) {
      e.preventDefault();
      const role = document.getElementById('join-role')?.value || 'commander';
      joinExercise(quickJoin, role).then(ex => {
        state.exerciseId = ex.id;
        state.exerciseCode = ex.code;
        state.role = role;
        showExerciseCode(ex.code);
        const ri = ROLES[role];
        document.getElementById('role-text').textContent = ri.name;
        document.getElementById('role-dot').style.background = ri.color;
        document.body.className = 'role-' + role;
        const b = document.getElementById('role-banner');
        if (b) b.textContent = 'ROLE-SPECIFIC INTEL — ' + ri.name.toUpperCase();
        connectSocket(role).then(() => {
          switchView('app'); renderAllMap(); renderIntel(); updateTeamStatusUI();
          if (ex.state) {
            applyExerciseState(ex.state);
            renderAllMap(); updateMapBadges(); renderIntel(); renderCascade(); updateTeamStatusUI();
            if (state.exerciseActive) { showDecisionPanel(); startClock(); }
          }
        });
      }).catch(err => showAuthError(err.message));
      return;
    }

    if (openEx) {
      e.preventDefault();
      const exRole = t.dataset.openRole || 'instructor';
      apiFetch('/api/exercises/' + openEx).then(ex => {
        state.exerciseId = ex.id;
        state.exerciseCode = ex.code;
        state.role = exRole === 'instructor' ? 'instructor' : exRole;
        const ri = ROLES[state.role] || { name: 'Instructor', color: 'var(--primary)' };
        const rt = document.getElementById('role-text');
        const rd = document.getElementById('role-dot');
        if (rt) rt.textContent = ri.name;
        if (rd) rd.style.background = ri.color;
        document.body.className = state.role === 'instructor' ? 'role-instructor' : 'role-' + state.role;
        const banner = document.getElementById('role-banner');
        if (banner) banner.textContent = 'ROLE-SPECIFIC INTEL — ' + ri.name.toUpperCase();
        // Show exercise code
        showExerciseCode(ex.code);
        connectSocket(state.role).then(() => {
          switchView('app'); renderAllMap(); renderIntel(); updateTeamStatusUI();
          if (ex.state) {
            applyExerciseState(ex.state);
            renderAllMap(); updateMapBadges(); renderIntel(); renderCascade(); updateTeamStatusUI();
            if (state.exerciseActive) { showDecisionPanel(); startClock(); }
          }
        });
      }).catch(err => showAuthError(err.message));
      return;
    }

    if (exAction) {
      e.preventDefault();
      if (exAction === 'create') {
        const name = document.getElementById('ex-name')?.value || 'OP DEEP FOG';
        createExercise(name, state.scenarioConfig).then(ex => {
          state.exerciseId = ex.id;
          state.exerciseCode = ex.code;
          state.role = 'instructor';
          showExerciseCode(ex.code);
          document.getElementById('role-text').textContent = 'Instructor';
          document.getElementById('role-dot').style.background = 'var(--primary)';
          document.body.className = 'role-instructor';
          connectSocket('instructor').then(() => {
            switchView('app'); renderAllMap(); renderIntel(); updateTeamStatusUI();
          });
        }).catch(err => showAuthError(err.message));
      } else if (exAction === 'join') {
        const code = document.getElementById('join-code')?.value;
        const role = document.getElementById('join-role')?.value || 'commander';
        if (!code) { showAuthError('Exercise code required'); return; }
        joinExercise(code, role).then(ex => {
          state.exerciseId = ex.id;
          state.exerciseCode = ex.code;
          state.role = role;
          const ri = ROLES[role];
          document.getElementById('role-text').textContent = ri.name;
          document.getElementById('role-dot').style.background = ri.color;
          document.body.className = 'role-' + role;
          const b = document.getElementById('role-banner');
          if (b) b.textContent = 'ROLE-SPECIFIC INTEL — ' + ri.name.toUpperCase();
          connectSocket(role).then(() => {
            switchView('app'); renderAllMap(); renderIntel(); updateTeamStatusUI();
            // Sync state from server
            if (ex.state) {
              applyExerciseState(ex.state);
              renderAllMap(); updateMapBadges(); renderIntel(); renderCascade(); updateTeamStatusUI();
              if (state.exerciseActive) { showDecisionPanel(); startClock(); }
            }
          });
        }).catch(err => showAuthError(err.message));
      }
      return;
    }

    if (a === 'go-login') {
      // Check if already authenticated
      checkAuth().then(user => {
        if (user) { state.user = user; switchView('lobby'); renderLobby(); }
        else switchView('login');
      });
      return;
    }
    if (a === 'go-landing') {
      if (state.exerciseActive) { state.exerciseActive = false; stopClock(); setAllTeamStatus('standby'); }
      if (socket) { socket.emit('leave-exercise'); }
      switchView('landing');
      return;
    }
    if (a === 'start-exercise') handleStart();
    else if (a === 'pause-exercise') handlePause();
    else if (a === 'end-exercise') handleEnd();
    else if (a === 'submit-decision') submitDecision();
    else if (a === 'export-aar-html') exportAARHTML();
    else if (a === 'export-aar-json') exportAARJSON();
    else if (r) {
      // Role selection from old login - now used for lobby
      state.role = r;
      const ri = ROLES[r];
      document.getElementById('role-text').textContent = ri.name;
      document.getElementById('role-dot').style.background = ri.color;
      document.body.className = r === 'instructor' ? 'role-instructor' : 'role-' + r;
      const b = document.getElementById('role-banner');
      if (b) b.textContent = 'ROLE-SPECIFIC INTEL — ' + ri.name.toUpperCase();
      switchView('app'); renderAllMap(); renderIntel();
    }
    else if (inj) handleInject(inj);
    else if (dec) selectDecision(dec);
    else if (sc) scrollToSection(sc);
  });

  // Confidence slider
  const confSlider = document.getElementById('conf-slider');
  const confDisplay = document.getElementById('conf-display');
  if (confSlider) {
    confSlider.addEventListener('input', e => {
      state.confidence = parseInt(e.target.value);
      if (confDisplay) confDisplay.textContent = state.confidence + '%';
      updateConfidenceMeter();
    });
  }

  // ===== LOBBY =====
  function renderLobby() {
    const userInfo = document.getElementById('lobby-user');
    if (userInfo) userInfo.textContent = `Welcome, ${state.user.username} (${state.user.role})`;
    // Load user's exercises
    apiFetch('/api/exercises').then(exercises => {
      const list = document.getElementById('exercise-list');
      if (list) {
        if (exercises.length === 0) {
          list.innerHTML = '<div class="aar-empty">No exercises yet.</div>';
        } else {
          list.innerHTML = exercises.map(ex => `
            <div class="exercise-card" data-exercise-id="${ex.id}">
              <div class="ex-card-name">${ex.name}</div>
              <div class="ex-card-meta">Code: <strong style="color:var(--primary);font-family:var(--font-mono)">${ex.code}</strong> | Status: ${ex.status} | Role: ${ex.role}</div>
              <button class="btn-primary btn-sm" data-open-exercise="${ex.id}" data-open-role="${ex.role}" style="margin-top:6px">${ex.role === 'instructor' ? 'Open Instructor Console' : 'Open Exercise'}</button>
            </div>
          `).join('');
        }
      }
    }).catch(() => {});

    // Load available exercises for trainees to join
    apiFetch('/api/exercises/available').then(exercises => {
      const list = document.getElementById('available-exercises');
      if (!list) return;
      if (exercises.length === 0) {
        list.innerHTML = '<div class="aar-empty">No exercises available. Ask your instructor for a code, or create one yourself.</div>';
      } else {
        list.innerHTML = exercises.map(ex => `
          <div class="exercise-card" data-available-code="${ex.code}">
            <div class="ex-card-name">${ex.name}</div>
            <div class="ex-card-meta">Code: <strong style="color:var(--primary);font-family:var(--font-mono)">${ex.code}</strong> | Instructor: ${ex.instructor_name} | ${ex.participant_count} joined</div>
            <button class="btn-primary btn-sm" data-quick-join="${ex.code}" style="margin-top:6px">Join as Trainee</button>
          </div>
        `).join('');
      }
    }).catch(() => {});
  }

  // ===== INIT =====
  initScenarioConfig();
  renderGrid(); renderCoordLabels(); renderZones(); renderCommsLinks();
  renderUnits(); renderThreats(); renderEffects();
  switchView('landing');

  // Toggle instructor code field on role change
  const regRoleSelect = document.getElementById('reg-role');
  if (regRoleSelect) {
    regRoleSelect.addEventListener('change', e => {
      const codeField = document.getElementById('instructor-code-field');
      if (codeField) codeField.style.display = e.target.value === 'instructor' ? 'block' : 'none';
    });
  }

  // Check auth on load
  checkAuth().then(user => {
    if (user) {
      state.user = user;
      // Show landing page, they can enter platform
    }
  });
})();
