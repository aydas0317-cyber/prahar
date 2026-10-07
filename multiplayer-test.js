/**
 * Multiplayer smoke test — two independent Socket.IO clients
 * with different X-Visitor-Id headers (simulating separate browsers)
 */
const { io } = require('socket.io-client');
const http = require('http');

const API = 'http://localhost:8000';

function apiRequest(path, method, body, visitorId) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = http.request(`${API}${path}`, {
      method: method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Visitor-Id': visitorId,
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}),
      },
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(body) }); }
        catch (e) { resolve({ status: res.statusCode, data: body }); }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function runTest() {
  console.log('=== Sentinel-X Multiplayer Smoke Test ===\n');

  // === CLIENT 1: Instructor ===
  const VISITOR_1 = 'test-visitor-instructor-001';
  console.log('1. Registering instructor...');
  let r = await apiRequest('/api/auth/register', 'POST', { username: 'mp_instructor', password: 'pass123', role: 'instructor' }, VISITOR_1);
  console.log('   Register:', r.status, r.data.username || r.data.error);

  console.log('2. Creating exercise...');
  r = await apiRequest('/api/exercises', 'POST', { name: 'MP TEST OP', config: { tempo: 'fast', infoLoss: 20 } }, VISITOR_1);
  console.log('   Exercise:', r.status, 'code:', r.data.code);
  const exerciseId = r.data.id;
  const exerciseCode = r.data.code;

  console.log('3. Starting exercise...');
  r = await apiRequest(`/api/exercises/${exerciseId}/start`, 'POST', {}, VISITOR_1);
  console.log('   Start:', r.status, 'active:', r.data.state?.active);

  // === CLIENT 2: Commander (separate visitor ID) ===
  const VISITOR_2 = 'test-visitor-commander-002';
  console.log('4. Registering commander...');
  r = await apiRequest('/api/auth/register', 'POST', { username: 'mp_commander', password: 'pass123', role: 'trainee' }, VISITOR_2);
  console.log('   Register:', r.status, r.data.username || r.data.error);

  console.log('5. Joining exercise...');
  r = await apiRequest('/api/exercises/join', 'POST', { code: exerciseCode, role: 'commander' }, VISITOR_2);
  console.log('   Join:', r.status, 'active:', r.data.state?.active, 'teamStatus:', JSON.stringify(r.data.state?.teamStatus));

  // === Socket.IO connections ===
  console.log('\n6. Connecting Socket.IO clients...');

  const socket1 = io(API, {
    transports: ['websocket', 'polling'],
    extraHeaders: { 'X-Visitor-Id': VISITOR_1 },
  });

  const socket2 = io(API, {
    transports: ['websocket', 'polling'],
    extraHeaders: { 'X-Visitor-Id': VISITOR_2 },
  });

  // Track events received by commander (socket2)
  const eventsReceived = [];
  socket2.on('state-update', (data) => { eventsReceived.push('state-update'); console.log('   [CMDR] Received state-update, active:', data.active, 'comms:', JSON.stringify(data.commsStatus)); });
  socket2.on('exercise-started', (data) => { eventsReceived.push('exercise-started'); console.log('   [CMDR] Received exercise-started'); });
  socket2.on('inject', (data) => { eventsReceived.push('inject'); console.log('   [CMDR] Received inject:', data.type, 'comms:', JSON.stringify(data.state?.commsStatus)); });
  socket2.on('decision-made', (data) => { eventsReceived.push('decision-made'); console.log('   [CMDR] Received decision-made:', data.decision?.action); });
  socket2.on('exercise-ended', (data) => { eventsReceived.push('exercise-ended'); console.log('   [CMDR] Received exercise-ended, AAR scores:', JSON.stringify(data.aar?.scores)); });
  socket2.on('team-update', (data) => { eventsReceived.push('team-update'); console.log('   [CMDR] Received team-update:', JSON.stringify(data.teamStatus)); });

  // Wait for connections
  await new Promise(resolve => {
    let connected = 0;
    socket1.on('connect', () => { console.log('   Instructor socket connected:', socket1.id); connected++; if (connected >= 2) resolve(); });
    socket2.on('connect', () => { console.log('   Commander socket connected:', socket2.id); connected++; if (connected >= 2) resolve(); });
  });

  // Join rooms
  console.log('\n7. Joining exercise rooms...');
  socket1.emit('join-exercise', { exerciseId, role: 'instructor', userId: 1, username: 'mp_instructor' });
  socket2.emit('join-exercise', { exerciseId, role: 'commander', userId: 2, username: 'mp_commander' });

  await sleep(1000);

  // Instructor injects comms delay
  console.log('\n8. Instructor injects comms delay...');
  r = await apiRequest(`/api/exercises/${exerciseId}/inject`, 'POST', { type: 'delay' }, VISITOR_1);
  console.log('   Inject result:', r.status, r.data.success);
  await sleep(1000);

  // Commander submits decision
  console.log('\n9. Commander submits decision...');
  r = await apiRequest(`/api/exercises/${exerciseId}/decision`, 'POST', {
    action: 'Deploy Recon',
    rationale: 'Conflicting reports - verify before engaging',
    confidence: 75,
    intelSnapshot: [{ source: 'AIR-1', msg: '2 aircraft detected', reliability: 85 }],
    infoCount: 5,
    conflictCount: 1,
    commsDegradedCount: 1
  }, VISITOR_2);
  console.log('   Decision result:', r.status, r.data.success);
  await sleep(1000);

  // Instructor ends exercise
  console.log('\n10. Instructor ends exercise...');
  r = await apiRequest(`/api/exercises/${exerciseId}/end`, 'POST', {}, VISITOR_1);
  console.log('   End result:', r.status, r.data.success);
  console.log('   AAR scores:', JSON.stringify(r.data.aar?.scores));
  await sleep(1000);

  // Summary
  console.log('\n=== RESULTS ===');
  console.log('Events received by commander:', eventsReceived);
  const passed = eventsReceived.includes('inject') && eventsReceived.includes('decision-made') && eventsReceived.includes('exercise-ended');
  console.log('Multiplayer test:', passed ? 'PASSED ✓' : 'FAILED ✗');

  socket1.disconnect();
  socket2.disconnect();
  process.exit(passed ? 0 : 1);
}

runTest().catch(e => { console.error('Test error:', e); process.exit(1); });
