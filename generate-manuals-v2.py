#!/usr/bin/env python3
"""Generate Sentinel-X User Manual PDFs using WeasyPrint (proper Bengali text shaping)."""
from weasyprint import HTML
from pathlib import Path

OUTPUT_DIR = Path("/home/user/workspace/sentinel-x")

# Shared CSS
CSS = """
@page {
    size: A4;
    margin: 25mm 20mm 20mm 20mm;
    @top-center {
        content: "SENTINEL-X";
        font-family: 'Inter', sans-serif;
        font-size: 9pt;
        color: #3dd68c;
        font-weight: bold;
        letter-spacing: 2px;
    }
    @bottom-center {
        content: "Sentinel-X — Multi-Domain Decision Trainer";
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: #5a6b80;
    }
    @bottom-right {
        content: "Page " counter(page);
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: #5a6b80;
    }
}

@page :first {
    @top-center { content: ""; }
    @bottom-center { content: ""; }
    @bottom-right { content: ""; }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Noto Sans Bengali', 'Inter', sans-serif;
    color: #1a1a2e;
    line-height: 1.6;
    font-size: 10.5pt;
}

h1 {
    font-size: 18pt;
    color: #01696F;
    margin-top: 28px;
    margin-bottom: 14px;
    padding-bottom: 6px;
    border-bottom: 2px solid #01696F;
    page-break-after: avoid;
}

h2 {
    font-size: 13pt;
    color: #28251D;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
}

p {
    text-align: justify;
    margin-bottom: 8px;
}

ul {
    margin-left: 18px;
    margin-bottom: 10px;
}

li {
    margin-bottom: 4px;
    text-align: left;
}

b, strong {
    color: #0C4E54;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9.5pt;
}

th {
    background-color: #01696F;
    color: white;
    padding: 8px;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 6px 8px;
    border: 0.5px solid #D4D1CA;
    vertical-align: top;
}

tr:nth-child(even) td {
    background-color: #F9F8F5;
}

.cover {
    text-align: center;
    padding-top: 80px;
    page-break-after: always;
}

.cover h1 {
    font-size: 36pt;
    color: #3dd68c;
    border: none;
    margin-bottom: 8px;
}

.cover .subtitle {
    font-size: 13pt;
    color: #5a6b80;
    margin-bottom: 40px;
}

.cover .label {
    font-size: 16pt;
    color: #01696F;
    font-weight: bold;
    margin-top: 20px;
}

.cover .version {
    font-size: 12pt;
    color: #5a6b80;
    margin-top: 6px;
}

.toc {
    page-break-after: always;
}

.toc table {
    font-size: 10pt;
}

.toc th {
    background-color: #01696F;
}

.note {
    font-size: 9pt;
    color: #5a6b80;
    margin-left: 16px;
    margin-top: 16px;
    padding: 8px 12px;
    background-color: #F9F8F5;
    border-left: 3px solid #01696F;
}

code {
    font-family: 'Courier New', monospace;
    font-size: 9pt;
    color: #01696F;
    background-color: #f0f0f0;
    padding: 1px 3px;
    border-radius: 2px;
}

.page-break {
    page-break-before: always;
}

hr {
    border: none;
    border-top: 1px solid #D4D1CA;
    margin: 20px 0;
}
"""

def build_english_html():
    return f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><style>{CSS}</style></head>
<body>

<div class="cover">
    <h1>SENTINEL-X</h1>
    <p class="subtitle">Multi-Domain Decision Trainer for Degraded Communication Environments</p>
    <p class="label">USER MANUAL</p>
    <p class="version">Version 5.0 | Fullstack Edition</p>
</div>

<div class="toc">
<h1>Table of Contents</h1>
<table>
<tr><th>Section</th><th>Title</th><th>Page</th></tr>
<tr><td>1</td><td>System Overview</td><td>3</td></tr>
<tr><td>2</td><td>Getting Started — Registration &amp; Login</td><td>4</td></tr>
<tr><td>3</td><td>Command Lobby</td><td>5</td></tr>
<tr><td>4</td><td>Instructor Role — Creating &amp; Controlling Exercises</td><td>6</td></tr>
<tr><td>5</td><td>Trainee Roles — Joining &amp; Participating</td><td>8</td></tr>
<tr><td>6</td><td>Tactical Map &amp; Intel Feed</td><td>9</td></tr>
<tr><td>7</td><td>Decision Submission &amp; Confidence Slider</td><td>10</td></tr>
<tr><td>8</td><td>Scenario Configuration</td><td>11</td></tr>
<tr><td>9</td><td>Injecting Communication Degradation</td><td>12</td></tr>
<tr><td>10</td><td>Red-Team Inject Console</td><td>13</td></tr>
<tr><td>11</td><td>Cascade Detection</td><td>14</td></tr>
<tr><td>12</td><td>After-Action Review (AAR) &amp; Export</td><td>15</td></tr>
<tr><td>13</td><td>Real-Time Multiplayer (Socket.IO)</td><td>16</td></tr>
<tr><td>14</td><td>Troubleshooting</td><td>17</td></tr>
</table>
</div>

<h1>1. System Overview</h1>
<p>Sentinel-X is a fullstack web-based decision-making training platform designed for military and defense environments where communication is degraded, delayed, or contradictory. Unlike traditional training formats (TEWT, CPX) that assume complete information flow, Sentinel-X deliberately injects incomplete, delayed, or contradictory intelligence feeds — training decision-making under uncertainty rather than under ideal conditions.</p>

<h2>Key Features</h2>
<ul>
<li><b>User registration and authentication</b> with password hashing (crypto.scryptSync)</li>
<li><b>Real-time multiplayer</b> via Socket.IO — multiple users join the same exercise from different devices</li>
<li><b>Scenario engine</b> with configurable communication degradation (delay, blackout, packet loss)</li>
<li><b>Conflicting intelligence injection</b> (air, cyber, land reports with divergent reliability scores)</li>
<li><b>Red-team inject console</b> (false flag operations, info overload, weather degrade, new threats)</li>
<li><b>Decision confidence slider</b> — trainees self-report confidence with each decision</li>
<li><b>What Did You Know at the Time?</b> — intel snapshot captured with every decision submission</li>
<li><b>Cascade detection</b> — system auto-detects self-reinforcing degradation cycles</li>
<li><b>Automated After-Action Review (AAR)</b> with data-driven scoring</li>
<li><b>AAR export</b> as downloadable HTML and JSON files</li>
<li><b>Role-based asymmetric information</b> — each role sees different intel feeds</li>
<li><b>SQLite database persistence</b> — all users, exercises, decisions, and AARs stored server-side</li>
</ul>

<h2>System Architecture</h2>
<table>
<tr><th>Layer</th><th>Technology</th></tr>
<tr><td>Frontend</td><td>HTML5 + CSS3 + JavaScript (Vanilla)</td></tr>
<tr><td>Backend</td><td>Node.js + Express.js</td></tr>
<tr><td>Real-time</td><td>Socket.IO</td></tr>
<tr><td>Database</td><td>SQLite (better-sqlite3)</td></tr>
<tr><td>Authentication</td><td>Session-based (X-Visitor-Id, crypto.scryptSync)</td></tr>
<tr><td>Deployment</td><td>Express static + port proxy</td></tr>
</table>

<div class="page-break"></div>

<h1>2. Getting Started — Registration &amp; Login</h1>

<h2>Step 1: Open the Platform</h2>
<p>Open the Sentinel-X URL in your web browser. You will see the landing page with an overview of the system, innovations, research backing, and roadmap. Click the <b>Enter Platform</b> button in the top right corner to access the authentication page.</p>

<h2>Step 2: Register a New Account</h2>
<p>If you are a new user, click the <b>Register</b> link on the login page. Fill in the following:</p>
<ul>
<li><b>Username</b>: Choose a unique username (minimum 3 characters)</li>
<li><b>Password</b>: Choose a secure password (minimum 4 characters)</li>
<li><b>Role</b>: Select either Trainee or Instructor</li>
</ul>
<p>After successful registration, you will be redirected to the login page with your username pre-filled. Your password is securely hashed using crypto.scryptSync before storage — it is never stored in plaintext.</p>

<h2>Step 3: Login</h2>
<p>Enter your username and password on the login page and click <b>Sign In</b>. Upon successful authentication, you will be taken to the Command Lobby.</p>

<div class="page-break"></div>

<h1>3. Command Lobby</h1>
<p>The Command Lobby is your home base after login. It displays your username and role at the top, and provides three main sections:</p>

<h2>Create New Exercise</h2>
<p>Enter an exercise name (e.g., OP DEEP FOG) and click <b>Create &amp; Enter as Instructor</b>. The system generates a unique exercise code (e.g., MS3249) and you enter the simulator as the instructor with full control permissions.</p>

<h2>Join Existing Exercise</h2>
<p>Enter the exercise code provided by your instructor, select your role (Commander Alpha, Cyber/EW Officer, Air Liaison, or Intel Analyst), and click <b>Join Exercise</b>. You will be connected to the exercise via Socket.IO and see real-time updates.</p>

<h2>Your Exercises</h2>
<p>This section lists all exercises you have created or joined, showing their status (created, active, ended) and your role in each.</p>

<div class="page-break"></div>

<h1>4. Instructor Role — Creating &amp; Controlling Exercises</h1>
<p>As an instructor, you have full control over the exercise. The instructor-only panels are visible in the left sidebar and include:</p>

<h2>Exercise Control</h2>
<ul>
<li><b>Start</b>: Initializes the exercise, resets all state, starts the clock, and notifies all connected participants via Socket.IO</li>
<li><b>Pause</b>: Temporarily halts the exercise clock and event processing</li>
<li><b>End</b>: Terminates the exercise, generates the AAR, and broadcasts it to all participants</li>
</ul>

<h2>Scenario Configuration</h2>
<ul>
<li><b>Tempo</b>: Controls event frequency — Slow (30s), Normal (15s), or Fast (8s) between automated events</li>
<li><b>Info Loss %</b>: Sets the baseline information loss percentage (0-60%) that affects reliability scores</li>
<li><b>Domains</b>: Toggle which operational domains are active — Land, Air, Cyber, EW</li>
</ul>

<div class="page-break"></div>

<h1>5. Trainee Roles — Joining &amp; Participating</h1>
<p>Trainees join an exercise using the exercise code provided by the instructor. Each role receives different (asymmetric) information, forcing team coordination:</p>

<table>
<tr><th>Role</th><th>Information Access</th><th>Primary Function</th></tr>
<tr><td>Commander Alpha</td><td>Full map, all sources</td><td>Mission command, final decisions</td></tr>
<tr><td>Cyber/EW Officer</td><td>Spectrum data, EW/Cyber alerts</td><td>Electronic warfare, cyber defense</td></tr>
<tr><td>Air Liaison</td><td>Air corridor data, air reports</td><td>Air asset management, airspace</td></tr>
<tr><td>Intel Analyst</td><td>All sources, reliability matrix</td><td>Source assessment, threat analysis</td></tr>
</table>

<p>Each role sees a filtered intel feed based on their access level. The Commander sees the full picture, while specialized roles see only their domain. This forces communication and coordination under degraded conditions.</p>

<div class="page-break"></div>

<h1>6. Tactical Map &amp; Intel Feed</h1>

<h2>Tactical Map</h2>
<p>The central panel displays a tactical grid map of Sector Golf-7 with coordinate labels (A-J horizontally, 1-5 vertically). The map shows:</p>
<ul>
<li><b>Friendly units</b> (green circles): ALPHA, BRAVO, AIR-1</li>
<li><b>Hostile units</b> (red circles): HOSTILE</li>
<li><b>Unknown units</b> (yellow circles): UNKNOWN, UNCONFIRMED</li>
<li><b>Communication links</b>: Lines between units — green (normal), amber (delayed), red (blackout)</li>
<li><b>Objective zones</b>: Dashed rectangles for OBJ ALPHA and ENEMY ZONE</li>
<li><b>Map badges</b>: Real-time status indicators (LATENCY, SIGNAL LOST, PACKET LOSS, FALSE FLAG)</li>
<li><b>Conditions bar</b>: Shows NOMINAL or degraded conditions (COMMS DEGRADED, WEATHER, ACTIVE THREATS)</li>
</ul>

<h2>Intelligence Feed</h2>
<p>The right panel shows incoming intelligence entries in reverse chronological order. Each entry displays the timestamp, message, source, and reliability score (HIGH/MEDIUM/LOW). Entries are color-coded by type: normal (green border), warning (amber), critical (red), conflict (cyan).</p>

<div class="page-break"></div>

<h1>7. Decision Submission &amp; Confidence Slider</h1>
<p>When the exercise is active, the decision panel at the bottom right becomes available. The trainee selects a course of action, sets their confidence level, and provides a written rationale.</p>

<h2>Available Decisions</h2>
<table>
<tr><th>Decision</th><th>Effect on Map</th></tr>
<tr><td>Engage Hostile</td><td>Attack vectors drawn, units move to engage</td></tr>
<tr><td>Deploy Recon</td><td>Recon path drawn, unit moves to investigate</td></tr>
<tr><td>Fortify Position</td><td>Defensive perimeters appear around friendly units</td></tr>
<tr><td>Tactical Withdrawal</td><td>Retreat paths drawn, units reposition to secondary waypoints</td></tr>
</table>

<h2>Confidence Slider</h2>
<p>After selecting a decision, a confidence slider appears (0-100%). The trainee self-reports their confidence level. The system tracks how confidence aligns with information quality — detecting overconfidence (high confidence with limited intel) and hesitation (low confidence with ample intel).</p>
<p>An intel snapshot is automatically captured at the moment of decision submission, recording exactly what information was available — this supports the What Did You Know at the Time? evaluation in the AAR.</p>

<div class="page-break"></div>

<h1>8. Scenario Configuration</h1>
<p>Instructors can configure the scenario before or during an exercise using the Scenario Configuration panel:</p>
<table>
<tr><th>Setting</th><th>Options</th><th>Description</th></tr>
<tr><td>Tempo</td><td>Slow / Normal / Fast</td><td>Controls time between automated intel events</td></tr>
<tr><td>Info Loss %</td><td>0% - 60%</td><td>Baseline information degradation affecting reliability</td></tr>
<tr><td>Land Domain</td><td>On / Off</td><td>Enables land-based intel and units</td></tr>
<tr><td>Air Domain</td><td>On / Off</td><td>Enables air corridor and air reports</td></tr>
<tr><td>Cyber Domain</td><td>On / Off</td><td>Enables cyber alerts and EW spectrum data</td></tr>
<tr><td>EW Domain</td><td>On / Off</td><td>Enables electronic warfare jamming effects</td></tr>
</table>

<div class="page-break"></div>

<h1>9. Injecting Communication Degradation</h1>
<p>The instructor can inject three types of communication degradation at any time during an active exercise. All connected trainees see the effects in real-time via Socket.IO.</p>
<table>
<tr><th>Type</th><th>Visual Effect</th><th>Duration</th><th>Description</th></tr>
<tr><td>Comms Delay</td><td>Links turn amber, dashed</td><td>~8s</td><td>3-5 second latency on all feeds</td></tr>
<tr><td>Signal Blackout</td><td>Links disappear, NO SIGNAL</td><td>~10s</td><td>Complete communication loss</td></tr>
<tr><td>Packet Loss</td><td>Links flicker, 30% drops</td><td>~6s</td><td>Intermittent data loss on channels</td></tr>
</table>
<p>Degradation automatically recovers after the duration expires, and a COMMS RESTORED message is injected into the intel feed.</p>

<div class="page-break"></div>

<h1>10. Red-Team Inject Console</h1>
<p>The Red-Team Inject Console provides advanced scenario control for creating realistic deception and overload scenarios:</p>
<table>
<tr><th>Inject</th><th>Effect</th></tr>
<tr><td>Weather Degrade</td><td>Fog overlay on tactical map, sensor effectiveness reduced</td></tr>
<tr><td>New Threat</td><td>New hostile unit appears on map at a new position</td></tr>
<tr><td>False Flag Op</td><td>Friendly units temporarily appear as hostile — spoofing detected</td></tr>
<tr><td>Info Overload</td><td>5 simultaneous intel feeds injected — cognitive load critical, triggers cascade</td></tr>
</table>
<p>The False Flag inject automatically resolves after 12 seconds, restoring friend/foe identification. The Info Overload inject is the primary cascade trigger — when combined with comms degradation and conflicting intel, it can trigger a cascade warning.</p>

<div class="page-break"></div>

<h1>11. Cascade Detection</h1>
<p>Based on research showing that a single erroneous decision can trigger a self-reinforcing cycle of cascading failures across the command structure, Sentinel-X automatically detects cascade conditions.</p>

<h2>Cascade Trigger Conditions</h2>
<ul>
<li>2+ comms channels degraded AND 1+ conflicting intel present, OR</li>
<li>8+ intel entries (overload) AND 1+ comms channel degraded</li>
</ul>
<p>When a cascade is detected, a CASCADE WARNING is injected into the intel feed, and the cascade is recorded in the Cascade Detection panel for the AAR. The research basis is from Hubbard, Kott, and Martin (arXiv:1607.08139) on self-reinforcing degradation in decision-making teams.</p>

<div class="page-break"></div>

<h1>12. After-Action Review (AAR) &amp; Export</h1>
<p>When the instructor ends the exercise, an After-Action Review is automatically generated and displayed. The AAR includes:</p>
<ul>
<li><b>Score Cards</b>: Decision Quality, Response Time, Info Utilization, Team Coordination (0-100 each, data-driven)</li>
<li><b>Decision Timeline</b>: Chronological view of all decisions, comms failures, and cascades</li>
<li><b>Cascade Analysis</b>: Details of any detected cascades with trigger descriptions</li>
<li><b>Communication Failures Log</b>: All injected degradation events with timestamps</li>
<li><b>Local AI Evaluation</b>: Overall rating (EXCELLENT/PROFICIENT/DEVELOPING/NEEDS RETRAINING) with findings</li>
<li><b>Areas for Improvement</b>: Personalized recommendations based on exercise performance</li>
<li><b>Intel Snapshots</b>: What Did You Know at the Time? — intel available at each decision point</li>
</ul>

<h2>Export Options</h2>
<table>
<tr><th>Format</th><th>Content</th><th>Use Case</th></tr>
<tr><td>HTML</td><td>Full formatted report with tables</td><td>Printable, shareable document</td></tr>
<tr><td>JSON</td><td>Raw structured data</td><td>Integration with other systems, programmatic analysis</td></tr>
</table>

<div class="page-break"></div>

<h1>13. Real-Time Multiplayer (Socket.IO)</h1>
<p>Sentinel-X supports real-time multiplayer via Socket.IO. Multiple users can join the same exercise from different browsers or devices, each in a different role.</p>

<h2>How It Works</h2>
<ul>
<li>The instructor creates an exercise and receives a unique code</li>
<li>Trainees join using the code and select their role</li>
<li>All participants are connected to the same Socket.IO room</li>
<li>When the instructor starts, pauses, injects, or ends the exercise, all participants see updates in real-time</li>
<li>Decisions submitted by any trainee are broadcast to all participants</li>
<li>Team status (which roles are active, degraded, or in decision mode) is synchronized</li>
</ul>
<p>Each role sees asymmetric information — the Cyber/EW officer sees spectrum data, the Air Liaison sees air corridors, the Intel Analyst sees all sources. This forces communication and coordination.</p>

<h2>Verified Socket.IO Events</h2>
<table>
<tr><th>Event</th><th>Direction</th><th>Description</th></tr>
<tr><td>exercise-started</td><td>Server → All</td><td>Exercise begins, full state broadcast</td></tr>
<tr><td>state-update</td><td>Server → All</td><td>Complete state sync (intel, comms, map)</td></tr>
<tr><td>inject</td><td>Instructor → All</td><td>Degradation or conflict injected</td></tr>
<tr><td>decision-made</td><td>Trainee → All</td><td>A decision was submitted with confidence</td></tr>
<tr><td>exercise-ended</td><td>Instructor → All</td><td>Exercise ends, AAR broadcast</td></tr>
<tr><td>team-update</td><td>Server → All</td><td>Team role status changed</td></tr>
<tr><td>tick</td><td>Server → All</td><td>Clock update every 5 seconds</td></tr>
</table>

<div class="page-break"></div>

<h1>14. Troubleshooting</h1>
<table>
<tr><th>Problem</th><th>Solution</th></tr>
<tr><td>Cannot login</td><td>Verify username and password. Register if you don't have an account.</td></tr>
<tr><td>Exercise not starting</td><td>Only the instructor can start. Verify you created the exercise.</td></tr>
<tr><td>Inject button not working</td><td>Exercise must be active. Click Start first.</td></tr>
<tr><td>Other users not seeing updates</td><td>Verify Socket.IO is connected. Use separate browsers/devices.</td></tr>
<tr><td>Decision options not showing</td><td>Exercise must be started. The trainee panel shows after Start.</td></tr>
<tr><td>AAR not generating</td><td>Click End Exercise to trigger AAR generation.</td></tr>
<tr><td>Export not downloading</td><td>Check browser popup blocker. Allow downloads from the site.</td></tr>
<tr><td>Comms delay links not changing</td><td>Fixed in v5 — CSS class name corrected to comms-link-delay.</td></tr>
<tr><td>Team status stuck on STANDBY</td><td>Exercise must be started. Status changes to ACTIVE on Start.</td></tr>
</table>

<div class="note">
For additional support, refer to the research backing section on the landing page, which links to the academic papers that inform the system's design (arXiv:1607.08139, arXiv:2603.21280).
</div>

</body>
</html>
"""


def build_bengali_html():
    return f"""
<!DOCTYPE html>
<html lang="bn">
<head><meta charset="UTF-8"><style>{CSS}</style></head>
<body>

<div class="cover">
    <h1>SENTINEL-X</h1>
    <p class="subtitle">ডিগ্রেডেড কমিউনিকেশন পরিবেশের জন্য মাল্টি-ডোমেইন ডিসিশন ট্রেনার</p>
    <p class="label">ব্যবহারকারী ম্যানুয়াল</p>
    <p class="version">সংস্করণ ৫.০ | ফুলস্ট্যাক এডিশন</p>
</div>

<div class="toc">
<h1>সূচিপত্র</h1>
<table>
<tr><th>অধ্যায়</th><th>শিরোনাম</th><th>পৃষ্ঠা</th></tr>
<tr><td>১</td><td>সিস্টেম পরিচিতি</td><td>৩</td></tr>
<tr><td>২</td><td>শুরু করা — রেজিস্ট্রেশন ও লগইন</td><td>৪</td></tr>
<tr><td>৩</td><td>কমান্ড লবি</td><td>৫</td></tr>
<tr><td>৪</td><td>ইনস্ট্রাক্টর রোল — এক্সারসাইজ তৈরি ও নিয়ন্ত্রণ</td><td>৬</td></tr>
<tr><td>৫</td><td>ট্রেইনি রোল — যোগদান ও অংশগ্রহণ</td><td>৮</td></tr>
<tr><td>৬</td><td>ট্যাক্টিক্যাল ম্যাপ ও ইন্টেল ফিড</td><td>৯</td></tr>
<tr><td>৭</td><td>সিদ্ধান্ত জমা ও কনফিডেন্স স্লাইডার</td><td>১০</td></tr>
<tr><td>৮</td><td>সিনারিও কনফিগারেশন</td><td>১১</td></tr>
<tr><td>৯</td><td>কমিউনিকেশন ডিগ্রেডেশন ইনজেকশন</td><td>১২</td></tr>
<tr><td>১০</td><td>রেড-টিম ইনজেক্ট কনসোল</td><td>১৩</td></tr>
<tr><td>১১</td><td>ক্যাসকেড ডিটেকশন</td><td>১৪</td></tr>
<tr><td>১২</td><td>আফটার-অ্যাকশন রিভিউ (AAR) ও এক্সপোর্ট</td><td>১৫</td></tr>
<tr><td>১৩</td><td>রিয়েল-টাইম মাল্টিপ্লেয়ার (Socket.IO)</td><td>১৬</td></tr>
<tr><td>১৪</td><td>সমস্যা সমাধান</td><td>১৭</td></tr>
</table>
</div>

<h1>১. সিস্টেম পরিচিতি</h1>
<p>Sentinel-X একটি ফুলস্ট্যাক ওয়েব-ভিত্তিক সিদ্ধান্ত গ্রহণের প্রশিক্ষণ প্ল্যাটফর্ম, যা সামরিক এবং প্রতিরক্ষা পরিবেশের জন্য ডিজাইন করা হয়েছে যেখানে যোগাযোগ ব্যাহত, বিলম্বিত, বা পরস্পরবিরোধী। ঐতিহ্যবাহী প্রশিক্ষণ ফরম্যাট (TEWT, CPX) যেখানে সম্পূর্ণ তথ্যপ্রবাহ অনুমান করে, Sentinel-X সচেতনভাবে অসম্পূর্ণ, বিলম্বিত, বা পরস্পরবিরোধী গোয়েন্দা তথ্য ইনজেক্ট করে — আদর্শ অবস্থার পরিবর্তে অনিশ্চয়তার অধীনে সিদ্ধান্ত গ্রহণের প্রশিক্ষণ দেয়।</p>

<h2>মূল বৈশিষ্ট্য</h2>
<ul>
<li><b>ইউজার রেজিস্ট্রেশন এবং অথেন্টিকেশন</b> — পাসওয়ার্ড হ্যাশিং (crypto.scryptSync) সহ</li>
<li><b>রিয়েল-টাইম মাল্টিপ্লেয়ার</b> — Socket.IO এর মাধ্যমে একাধিক ইউজার আলাদা ডিভাইস থেকে একই এক্সারসাইজে যোগ দিতে পারে</li>
<li><b>সিনারিও ইঞ্জিন</b> — কনফিগারেবল কমিউনিকেশন ডিগ্রেডেশন (delay, blackout, packet loss)</li>
<li><b>পরস্পরবিরোধী গোয়েন্দা তথ্য ইনজেকশন</b> — air, cyber, land রিপোর্ট ভিন্ন নির্ভরযোগ্যতা স্কোর সহ</li>
<li><b>রেড-টিম ইনজেক্ট কনসোল</b> — false flag অপারেশন, info overload, weather degrade, new threat</li>
<li><b>ডিসিশন কনফিডেন্স স্লাইডার</b> — ট্রেইনি প্রতিটি সিদ্ধান্তে নিজের আত্মবিশ্বাস স্তর সেট করে</li>
<li><b>"What Did You Know at the Time?"</b> — প্রতিটি সিদ্ধান্তের সময় ইন্টেল স্ন্যাপশট ক্যাপচার হয়</li>
<li><b>ক্যাসকেড ডিটেকশন</b> — সিস্টেম স্বয়ংক্রিয়ভাবে self-reinforcing ডিগ্রেডেশন সাইকেল শনাক্ত করে</li>
<li><b>স্বয়ংক্রিয় আফটার-অ্যাকশন রিভিউ (AAR)</b> — ডেটা-চালিত স্কোরিং সহ</li>
<li><b>AAR এক্সপোর্ট</b> — HTML এবং JSON ফাইল ডাউনলোড</li>
<li><b>রোল-ভিত্তিক অসমমিত তথ্য</b> — প্রতিটি রোল আলাদা ইন্টেল ফিড দেখে</li>
<li><b>SQLite ডেটাবেস পারসিস্টেন্স</b> — সকল ইউজার, এক্সারসাইজ, সিদ্ধান্ত এবং AAR সার্ভারে সংরক্ষিত</li>
</ul>

<h2>সিস্টেম আর্কিটেকচার</h2>
<table>
<tr><th>লেয়ার</th><th>প্রযুক্তি</th></tr>
<tr><td>Frontend</td><td>HTML5 + CSS3 + JavaScript (Vanilla)</td></tr>
<tr><td>Backend</td><td>Node.js + Express.js</td></tr>
<tr><td>Real-time</td><td>Socket.IO</td></tr>
<tr><td>Database</td><td>SQLite (better-sqlite3)</td></tr>
<tr><td>Authentication</td><td>Session-based (X-Visitor-Id, crypto.scryptSync)</td></tr>
<tr><td>Deployment</td><td>Express static + port proxy</td></tr>
</table>

<div class="page-break"></div>

<h1>২. শুরু করা — রেজিস্ট্রেশন ও লগইন</h1>

<h2>ধাপ ১: প্ল্যাটফর্ম খুলুন</h2>
<p>আপনার ওয়েব ব্রাউজারে Sentinel-X URL খুলুন। আপনি ল্যান্ডিং পেজ দেখতে পাবেন যেখানে সিস্টেমের ওভারভিউ, ইনোভেশন, রিসার্চ এবং রোডম্যাপ রয়েছে। উপরে ডানদিকে <b>Enter Platform</b> বোতামে ক্লিক করুন।</p>

<h2>ধাপ ২: নতুন অ্যাকাউন্ট রেজিস্টার করুন</h2>
<p>আপনি যদি নতুন ইউজার হন, লগইন পেজে <b>Register</b> লিঙ্কে ক্লিক করুন। নিচের তথ্য পূরণ করুন:</p>
<ul>
<li><b>Username</b>: একটি ইউনিক ইউজারনেম বেছে নিন (ন্যূনতম ৩ অক্ষর)</li>
<li><b>Password</b>: একটি নিরাপদ পাসওয়ার্ড বেছে নিন (ন্যূনতম ৪ অক্ষর)</li>
<li><b>Role</b>: Trainee বা Instructor নির্বাচন করুন</li>
</ul>
<p>সফল রেজিস্ট্রেশনের পর, আপনি লগইন পেজে রিডাইরেক্ট হবেন। আপনার পাসওয়ার্ড crypto.scryptSync দিয়ে নিরাপদে হ্যাশ করা হয় — এটি কখনোই প্লেইনটেক্সটে সংরক্ষিত হয় না।</p>

<h2>ধাপ ৩: লগইন</h2>
<p>লগইন পেজে আপনার ইউজারনেম এবং পাসওয়ার্ড লিখে <b>Sign In</b> বোতামে ক্লিক করুন। সফল অথেন্টিকেশনের পর আপনি কমান্ড লবিতে নিয়ে যাওয়া হবেন।</p>

<div class="page-break"></div>

<h1>৩. কমান্ড লবি</h1>
<p>কমান্ড লবি হল লগইনের পর আপনার মূল পেজ। এটি উপরে আপনার ইউজারনেম এবং রোল প্রদর্শন করে এবং তিনটি প্রধান বিভাগ প্রদান করে:</p>

<h2>নতুন এক্সারসাইজ তৈরি করুন</h2>
<p>একটি এক্সারসাইজ নাম লিখুন (যেমন OP DEEP FOG) এবং <b>Create &amp; Enter as Instructor</b> বোতামে ক্লিক করুন। সিস্টেম একটি ইউনিক এক্সারসাইজ কোড তৈরি করে এবং আপনি ইনস্ট্রাক্টর হিসেবে সিমুলেটরে প্রবেশ করেন।</p>

<h2>বিদ্যমান এক্সারসাইজে যোগ দিন</h2>
<p>আপনার ইনস্ট্রাক্টর দ্বারা প্রদত্ত এক্সারসাইজ কোড লিখুন, আপনার রোল নির্বাচন করুন (Commander Alpha, Cyber/EW Officer, Air Liaison, বা Intel Analyst) এবং <b>Join Exercise</b> বোতামে ক্লিক করুন। আপনি Socket.IO এর মাধ্যমে এক্সারসাইজে সংযুক্ত হবেন।</p>

<h2>আপনার এক্সারসাইজ</h2>
<p>এই বিভাগে আপনার তৈরি বা যোগ দেওয়া সকল এক্সারসাইজের তালিকা থাকে — সেগুলোর স্ট্যাটাস (created, active, ended) এবং আপনার রোল সহ।</p>

<div class="page-break"></div>

<h1>৪. ইনস্ট্রাক্টর রোল — এক্সারসাইজ তৈরি ও নিয়ন্ত্রণ</h1>
<p>ইনস্ট্রাক্টর হিসেবে আপনার এক্সারসাইজের উপর সম্পূর্ণ নিয়ন্ত্রণ আছে। ইনস্ট্রাক্টর-অনলি প্যানেলগুলি বাম সাইডবারে প্রদর্শিত হয়:</p>

<h2>এক্সারসাইজ নিয়ন্ত্রণ</h2>
<ul>
<li><b>Start</b>: এক্সারসাইজ শুরু করে, সমস্ত স্টেট রিসেট করে, ঘড়ি চালু করে এবং Socket.IO এর মাধ্যমে সমস্ত সংযুক্ত অংশগ্রহণকারীদের জানায়</li>
<li><b>Pause</b>: সাময়িকভাবে এক্সারসাইজ ঘড়ি এবং ইভেন্ট প্রসেসিং বন্ধ করে</li>
<li><b>End</b>: এক্সারসাইজ শেষ করে, AAR তৈরি করে এবং সমস্ত অংশগ্রহণকারীদের কাছে পাঠায়</li>
</ul>

<h2>সিনারিও কনফিগারেশন</h2>
<ul>
<li><b>Tempo</b>: ইভেন্ট ফ্রিকোয়েন্সি নিয়ন্ত্রণ — Slow (৩০সে), Normal (১৫সে), বা Fast (৮সে)</li>
<li><b>Info Loss %</b>: বেসলাইন তথ্য হ্রাস শতাংশ (০-৬০%) যা নির্ভরযোগ্যতা স্কোরকে প্রভাবিত করে</li>
<li><b>Domains</b>: কোন অপারেশনাল ডোমেইন সক্রিয় তা টগল করুন — Land, Air, Cyber, EW</li>
</ul>

<div class="page-break"></div>

<h1>৫. ট্রেইনি রোল — যোগদান ও অংশগ্রহণ</h1>
<p>ট্রেইনিরা ইনস্ট্রাক্টর দ্বারা প্রদত্ত এক্সারসাইজ কোড ব্যবহার করে যোগ দেয়। প্রতিটি রোল ভিন্ন (অসমমিত) তথ্য গ্রহণ করে, যা টিম কোঅর্ডিনেশনে বাধ্য করে:</p>

<table>
<tr><th>রোল</th><th>তথ্য অ্যাক্সেস</th><th>প্রাথমিক কার্য</th></tr>
<tr><td>Commander Alpha</td><td>সম্পূর্ণ ম্যাপ, সকল উৎস</td><td>মিশন কমান্ড, চূড়ান্ত সিদ্ধান্ত</td></tr>
<tr><td>Cyber/EW Officer</td><td>স্পেকট্রাম ডেটা, EW/Cyber অ্যালার্ট</td><td>ইলেকট্রনিক ওয়ারফেয়ার, সাইবার ডিফেন্স</td></tr>
<tr><td>Air Liaison</td><td>এয়ার করিডর ডেটা, এয়ার রিপোর্ট</td><td>এয়ার অ্যাসেট ম্যানেজমেন্ট</td></tr>
<tr><td>Intel Analyst</td><td>সকল উৎস, নির্ভরযোগ্যতা ম্যাট্রিক্স</td><td>উৎস মূল্যায়ন, হুমকি বিশ্লেষণ</td></tr>
</table>

<p>প্রতিটি রোল তাদের অ্যাক্সেস লেভেলের উপর ভিত্তি করে ফিল্টার করা ইন্টেল ফিড দেখে। Commander সম্পূর্ণ চিত্র দেখে, যখন বিশেষায়িত রোল শুধু তাদের ডোমেইন দেখে। এটি ডিগ্রেডেড অবস্থায় যোগাযোগ এবং সমন্বয়ে বাধ্য করে।</p>

<div class="page-break"></div>

<h1>৬. ট্যাক্টিক্যাল ম্যাপ ও ইন্টেল ফিড</h1>

<h2>ট্যাক্টিক্যাল ম্যাপ</h2>
<p>কেন্দ্রীয় প্যানেলে Sector Golf-7 এর একটি ট্যাক্টিক্যাল গ্রিড ম্যাপ প্রদর্শিত হয় কোঅর্ডিনেট লেবেল সহ (A-J অনুভূমিকভাবে, 1-5 উল্লম্বভাবে)। ম্যাপে দেখা যায়:</p>
<ul>
<li><b>বন্ধুত্বপূর্ণ ইউনিট</b> (সবুজ বৃত্ত): ALPHA, BRAVO, AIR-1</li>
<li><b>শত্রু ইউনিট</b> (লাল বৃত্ত): HOSTILE</li>
<li><b>অজানা ইউনিট</b> (হলুদ বৃত্ত): UNKNOWN, UNCONFIRMED</li>
<li><b>যোগাযোগ লিংক</b>: ইউনিটের মধ্যে লাইন — সবুজ (স্বাভাবিক), অ্যাম্বার (বিলম্বিত), লাল (ব্ল্যাকআউট)</li>
<li><b>অবজেক্টিভ জোন</b>: OBJ ALPHA এবং ENEMY ZONE এর জন্য ড্যাশড আয়তক্ষেত্র</li>
<li><b>ম্যাপ ব্যাজ</b>: রিয়েল-টাইম স্ট্যাটাস ইন্ডিকেটর (LATENCY, SIGNAL LOST, PACKET LOSS, FALSE FLAG)</li>
<li><b>কন্ডিশন বার</b>: NOMINAL বা ডিগ্রেডেড কন্ডিশন দেখায়</li>
</ul>

<h2>ইন্টেলিজেন্স ফিড</h2>
<p>ডান প্যানেলে বিপরীত কালানুক্রমিক ক্রমে আসা গোয়েন্দা এন্ট্রি প্রদর্শিত হয়। প্রতিটি এন্ট্রিতে টাইমস্ট্যাম্প, বার্তা, উৎস এবং নির্ভরযোগ্যতা স্কোর (HIGH/MEDIUM/LOW) থাকে। এন্ট্রিগুলি টাইপ অনুসারে রঙ-কোডেড: normal (সবুজ), warning (অ্যাম্বার), critical (লাল), conflict (সায়ান)।</p>

<div class="page-break"></div>

<h1>৭. সিদ্ধান্ত জমা ও কনফিডেন্স স্লাইডার</h1>
<p>এক্সারসাইজ সক্রিয় থাকলে, নিচে ডানদিকে ডিসিশন প্যানেল উপলব্ধ হয়। ট্রেইনি একটি কোর্স অফ অ্যাকশন নির্বাচন করে, কনফিডেন্স লেভেল সেট করে এবং একটি লিখিত রেশনাল প্রদান করে।</p>

<h2>উপলব্ধ সিদ্ধান্ত</h2>
<table>
<tr><th>সিদ্ধান্ত</th><th>ম্যাপে প্রভাব</th></tr>
<tr><td>Engage Hostile</td><td>অ্যাটাক ভেক্টর আঁকা হয়, ইউনিট শত্রুকে আক্রমণ করতে চলে</td></tr>
<tr><td>Deploy Recon</td><td>রেকন পথ আঁকা হয়, ইউনিট তদন্ত করতে চলে</td></tr>
<tr><td>Fortify Position</td><td>বন্ধুত্বপূর্ণ ইউনিটের চারপাশে প্রতিরক্ষামূলক পরিধি দেখা যায়</td></tr>
<tr><td>Tactical Withdrawal</td><td>পিছু হটার পথ আঁকা হয়, ইউনিট পুনঃঅবস্থান নেয়</td></tr>
</table>

<h2>কনফিডেন্স স্লাইডার</h2>
<p>সিদ্ধান্ত নির্বাচনের পর একটি কনফিডেন্স স্লাইডার প্রদর্শিত হয় (০-১০০%)। ট্রেইনি নিজের আত্মবিশ্বাস স্তর সেট করে। সিস্টেম ট্র্যাক করে আত্মবিশ্বাস কীভাবে তথ্যের গুণমানের সাথে সঙ্গতিপূর্ণ — overconfidence (সীমিত ইন্টেলে উচ্চ আত্মবিশ্বাস) এবং hesitation (প্রচুর ইন্টেলে নিম্ন আত্মবিশ্বাস) শনাক্ত করে।</p>
<p>সিদ্ধান্ত জমার মুহূর্তে একটি ইন্টেল স্ন্যাপশট স্বয়ংক্রিয়ভাবে ক্যাপচার করা হয় — এটি AAR-এ "What Did You Know at the Time?" মূল্যায়নকে সমর্থন করে।</p>

<div class="page-break"></div>

<h1>৮. সিনারিও কনফিগারেশন</h1>
<p>ইনস্ট্রাক্টররা এক্সারসাইজের আগে বা সময় সিনারিও কনফিগার করতে পারেন:</p>
<table>
<tr><th>সেটিং</th><th>অপশন</th><th>বর্ণনা</th></tr>
<tr><td>Tempo</td><td>Slow / Normal / Fast</td><td>স্বয়ংক্রিয় ইন্টেল ইভেন্টের মধ্যে সময় নিয়ন্ত্রণ</td></tr>
<tr><td>Info Loss %</td><td>০% - ৬০%</td><td>নির্ভরযোগ্যতা প্রভাবিত করে এমন বেসলাইন তথ্য ডিগ্রেডেশন</td></tr>
<tr><td>Land Domain</td><td>On / Off</td><td>ল্যান্ড-ভিত্তিক ইন্টেল এবং ইউনিট সক্রিয় করে</td></tr>
<tr><td>Air Domain</td><td>On / Off</td><td>এয়ার করিডর এবং এয়ার রিপোর্ট সক্রিয় করে</td></tr>
<tr><td>Cyber Domain</td><td>On / Off</td><td>সাইবার অ্যালার্ট এবং EW স্পেকট্রাম ডেটা সক্রিয় করে</td></tr>
<tr><td>EW Domain</td><td>On / Off</td><td>ইলেকট্রনিক ওয়ারফেয়ার জ্যামিং প্রভাব সক্রিয় করে</td></tr>
</table>

<div class="page-break"></div>

<h1>৯. কমিউনিকেশন ডিগ্রেডেশন ইনজেকশন</h1>
<p>ইনস্ট্রাক্টর সক্রিয় এক্সারসাইজের সময় যেকোনো সময় তিন ধরনের কমিউনিকেশন ডিগ্রেডেশন ইনজেক্ট করতে পারেন। সমস্ত সংযুক্ত ট্রেইনি Socket.IO এর মাধ্যমে রিয়েল-টাইমে প্রভাব দেখে।</p>
<table>
<tr><th>ধরন</th><th>ভিজ্যুয়াল প্রভাব</th><th>সময়</th><th>বর্ণনা</th></tr>
<tr><td>Comms Delay</td><td>লিংক অ্যাম্বার, ড্যাশড</td><td>~৮সে</td><td>সকল ফিডে ৩-৫ সেকেন্ড লেটেন্সি</td></tr>
<tr><td>Signal Blackout</td><td>লিংক অদৃশ্য, NO SIGNAL</td><td>~১০সে</td><td>সম্পূর্ণ যোগাযোগ বিচ্ছিন্নতা</td></tr>
<tr><td>Packet Loss</td><td>লিংক ফ্লিকার, ৩০% ড্রপ</td><td>~৬সে</td><td>চ্যানেলে ব্যবধানে ডেটা লস</td></tr>
</table>
<p>ডিগ্রেডেশন সময় শেষ হওয়ার পর স্বয়ংক্রিয়ভাবে পুনরুদ্ধার হয় এবং ইন্টেল ফিডে একটি COMMS RESTORED বার্তা ইনজেক্ট করা হয়।</p>

<div class="page-break"></div>

<h1>১০. রেড-টিম ইনজেক্ট কনসোল</h1>
<p>রেড-টিম ইনজেক্ট কনসোল বাস্তবসম্মত প্রতারণা এবং ওভারলোড সিনারিও তৈরির জন্য উন্নত সিনারিও নিয়ন্ত্রণ প্রদান করে:</p>
<table>
<tr><th>ইনজেক্ট</th><th>প্রভাব</th></tr>
<tr><td>Weather Degrade</td><td>ম্যাপে কুয়াশার ওভারলে, সেন্সর কার্যকারিতা হ্রাস</td></tr>
<tr><td>New Threat</td><td>ম্যাপে নতুন অবস্থানে নতুন শত্রু ইউনিট আবির্ভূত</td></tr>
<tr><td>False Flag Op</td><td>বন্ধুত্বপূর্ণ ইউনিট সাময়িকভাবে শত্রু হিসেবে দেখা যায় — স্পুফিং শনাক্ত</td></tr>
<tr><td>Info Overload</td><td>৫টি একই সাথে ইন্টেল ফিড ইনজেক্ট — কগনিটিভ লোড ক্রিটিক্যাল, ক্যাসকেড ট্রিগার</td></tr>
</table>
<p>False Flag ইনজেক্ট ১২ সেকেন্ড পর স্বয়ংক্রিয়ভাবে সমাধান হয়। Info Overload ইনজেক্ট হল প্রাথমিক ক্যাসকেড ট্রিগার — যখন কমিউনিকেশন ডিগ্রেডেশন এবং পরস্পরবিরোধী ইন্টেলের সাথে মিলিত হয়, এটি একটি ক্যাসকেড সতর্কতা ট্রিগার করতে পারে।</p>

<div class="page-break"></div>

<h1>১১. ক্যাসকেড ডিটেকশন</h1>
<p>গবেষণা অনুসারে, একটি ভুল সিদ্ধান্ত সমগ্র কমান্ড স্ট্রাকচার জুড়ে self-reinforcing ক্যাসকেডিং ফেইলিওরের সাইকেল ট্রিগার করতে পারে। Sentinel-X স্বয়ংক্রিয়ভাবে ক্যাসকেড কন্ডিশন শনাক্ত করে।</p>

<h2>ক্যাসকেড ট্রিগার কন্ডিশন</h2>
<ul>
<li>২+ কমিউনিকেশন চ্যানেল ডিগ্রেডেড এবং ১+ পরস্পরবিরোধী ইন্টেল উপস্থিত, অথবা</li>
<li>৮+ ইন্টেল এন্ট্রি (ওভারলোড) এবং ১+ কমিউনিকেশন চ্যানেল ডিগ্রেডেড</li>
</ul>
<p>ক্যাসকেড শনাক্ত হলে, একটি CASCADE WARNING ইন্টেল ফিডে ইনজেক্ট করা হয় এবং ক্যাসকেডটি AAR-এর জন্য Cascade Detection প্যানেলে রেকর্ড করা হয়। গবেষণার ভিত্তি Hubbard, Kott, এবং Martin (arXiv:1607.08139) থেকে নেওয়া।</p>

<div class="page-break"></div>

<h1>১২. আফটার-অ্যাকশন রিভিউ (AAR) ও এক্সপোর্ট</h1>
<p>ইনস্ট্রাক্টর এক্সারসাইজ শেষ করলে, একটি আফটার-অ্যাকশন রিভিউ স্বয়ংক্রিয়ভাবে তৈরি এবং প্রদর্শিত হয়। AAR-এ অন্তর্ভুক্ত:</p>
<ul>
<li><b>স্কোর কার্ড</b>: Decision Quality, Response Time, Info Utilization, Team Coordination (প্রতিটি ০-১০০, ডেটা-চালিত)</li>
<li><b>সিদ্ধান্ত টাইমলাইন</b>: সকল সিদ্ধান্ত, কমিউনিকেশন ফেইলিওর এবং ক্যাসকেডের কালানুক্রমিক ভিউ</li>
<li><b>ক্যাসকেড বিশ্লেষণ</b>: শনাক্ত করা ক্যাসকেডের বিস্তারিত ট্রিগার বর্ণনা সহ</li>
<li><b>কমিউনিকেশন ফেইলিওর লগ</b>: সকল ইনজেক্টেড ডিগ্রেডেশন ইভেন্ট টাইমস্ট্যাম্প সহ</li>
<li><b>লোকাল AI মূল্যায়ন</b>: সামগ্রিক রেটিং (EXCELLENT/PROFICIENT/DEVELOPING/NEEDS RETRAINING) ফাইন্ডিং সহ</li>
<li><b>উন্নতির ক্ষেত্র</b>: এক্সারসাইজ পারফরম্যান্সের উপর ভিত্তি করে ব্যক্তিগতকৃত সুপারিশ</li>
<li><b>ইন্টেল স্ন্যাপশট</b>: What Did You Know at the Time? — প্রতিটি সিদ্ধান্ত বিন্দুতে উপলব্ধ ইন্টেল</li>
</ul>

<h2>এক্সপোর্ট অপশন</h2>
<table>
<tr><th>ফরম্যাট</th><th>কন্টেন্ট</th><th>ব্যবহার</th></tr>
<tr><td>HTML</td><td>টেবিল সহ সম্পূর্ণ ফরম্যাটেড রিপোর্ট</td><td>প্রিন্টযোগ্য, শেয়ারযোগ্য ডকুমেন্ট</td></tr>
<tr><td>JSON</td><td>কাঁচা স্ট্রাকচার্ড ডেটা</td><td>অন্যান্য সিস্টেমের সাথে ইন্টিগ্রেশন</td></tr>
</table>

<div class="page-break"></div>

<h1>১৩. রিয়েল-টাইম মাল্টিপ্লেয়ার (Socket.IO)</h1>
<p>Sentinel-X Socket.IO এর মাধ্যমে রিয়েল-টাইম মাল্টিপ্লেয়ার সমর্থন করে। একাধিক ইউজার আলাদা ব্রাউজার বা ডিভাইস থেকে একই এক্সারসাইজে যোগ দিতে পারে, প্রত্যেকে আলাদা রোলে।</p>

<h2>কীভাবে কাজ করে</h2>
<ul>
<li>ইনস্ট্রাক্টর একটি এক্সারসাইজ তৈরি করেন এবং একটি ইউনিক কোড পান</li>
<li>ট্রেইনিরা কোড ব্যবহার করে যোগ দেয় এবং তাদের রোল নির্বাচন করে</li>
<li>সমস্ত অংশগ্রহণকারী একই Socket.IO রুমে সংযুক্ত হয়</li>
<li>ইনস্ট্রাক্টর যখন start, pause, inject, বা end করেন, সমস্ত অংশগ্রহণকারী রিয়েল-টাইমে আপডেট দেখে</li>
<li>যেকোনো ট্রেইনি দ্বারা জমা দেওয়া সিদ্ধান্ত সমস্ত অংশগ্রহণকারীদের কাছে ব্রডকাস্ট করা হয়</li>
<li>টিম স্ট্যাটাস (কোন রোল active, degraded, বা decision mode-এ) সিঙ্ক্রোনাইজড</li>
</ul>
<p>প্রতিটি রোল অসমমিত তথ্য দেখে — Cyber/EW অফিসার স্পেকট্রাম ডেটা দেখে, Air Liaison এয়ার করিডর দেখে, Intel Analyst সব উৎস দেখে। এটি যোগাযোগ এবং সমন্বয়ে বাধ্য করে।</p>

<h2>যাচাইকৃত Socket.IO ইভেন্ট</h2>
<table>
<tr><th>ইভেন্ট</th><th>দিক</th><th>বর্ণনা</th></tr>
<tr><td>exercise-started</td><td>সার্ভার → সকল</td><td>এক্সারসাইজ শুরু, সম্পূর্ণ স্টেট ব্রডকাস্ট</td></tr>
<tr><td>state-update</td><td>সার্ভার → সকল</td><td>সম্পূর্ণ স্টেট সিঙ্ক (intel, comms, map)</td></tr>
<tr><td>inject</td><td>ইনস্ট্রাক্টর → সকল</td><td>ডিগ্রেডেশন বা কনফ্লিক্ট ইনজেক্ট করা হয়েছে</td></tr>
<tr><td>decision-made</td><td>ট্রেইনি → সকল</td><td>একটি সিদ্ধান্ত কনফিডেন্স সহ জমা দেওয়া হয়েছে</td></tr>
<tr><td>exercise-ended</td><td>ইনস্ট্রাক্টর → সকল</td><td>এক্সারসাইজ শেষ, AAR ব্রডকাস্ট</td></tr>
<tr><td>team-update</td><td>সার্ভার → সকল</td><td>টিম রোল স্ট্যাটাস পরিবর্তিত</td></tr>
<tr><td>tick</td><td>সার্ভার → সকল</td><td>৫ সেকেন্ডে ঘড়ি আপডেট</td></tr>
</table>

<div class="page-break"></div>

<h1>১৪. সমস্যা সমাধান</h1>
<table>
<tr><th>সমস্যা</th><th>সমাধান</th></tr>
<tr><td>লগইন করতে পারছি না</td><td>ইউজারনেম এবং পাসওয়ার্ড যাচাই করুন। অ্যাকাউন্ট না থাকলে রেজিস্টার করুন।</td></tr>
<tr><td>এক্সারসাইজ শুরু হচ্ছে না</td><td>শুধুমাত্র ইনস্ট্রাক্টর শুরু করতে পারে। আপনি এক্সারসাইজ তৈরি করেছেন কিনা যাচাই করুন।</td></tr>
<tr><td>Inject বোতাম কাজ করছে না</td><td>এক্সারসাইজ সক্রিয় থাকতে হবে। প্রথমে Start ক্লিক করুন।</td></tr>
<tr><td>অন্য ইউজাররা আপডেট দেখছে না</td><td>Socket.IO সংযুক্ত কিনা যাচাই করুন। আলাদা ব্রাউজার/ডিভাইস ব্যবহার করুন।</td></tr>
<tr><td>সিদ্ধান্ত অপশন দেখা যাচ্ছে না</td><td>এক্সারসাইজ শুরু হতে হবে। Start এর পরে ট্রেইনি প্যানেল দেখা যায়।</td></tr>
<tr><td>AAR তৈরি হচ্ছে না</td><td>AAR ট্রিগার করতে End Exercise ক্লিক করুন।</td></tr>
<tr><td>এক্সপোর্ট ডাউনলোড হচ্ছে না</td><td>ব্রাউজার পপআপ ব্লকার চেক করুন। সাইট থেকে ডাউনলোড অনুমোদন করুন।</td></tr>
<tr><td>Team status STANDBY-এ আটকে আছে</td><td>এক্সারসাইজ শুরু হতে হবে। Start এ স্ট্যাটাস ACTIVE হয়।</td></tr>
</table>

<div class="note">
অতিরিক্ত সহায়তার জন্য, ল্যান্ডিং পেজের রিসার্চ ব্যাকিং সেকশন দেখুন, যা সিস্টেমের ডিজাইনকে নির্দেশকারী একাডেমিক পেপারগুলির লিংক করে (arXiv:1607.08139, arXiv:2603.21280)।
</div>

</body>
</html>
"""


if __name__ == "__main__":
    # Generate English PDF
    print("Generating English manual...")
    HTML(string=build_english_html()).write_pdf(
        str(OUTPUT_DIR / "Sentinel-X-User-Manual-EN.pdf"),
        title="Sentinel-X User Manual",
        author="Perplexity Computer",
    )
    print("English manual generated: Sentinel-X-User-Manual-EN.pdf")
    
    # Generate Bengali PDF
    print("Generating Bengali manual...")
    HTML(string=build_bengali_html()).write_pdf(
        str(OUTPUT_DIR / "Sentinel-X-User-Manual-BN.pdf"),
        title="Sentinel-X ব্যবহারকারী ম্যানুয়াল",
        author="Perplexity Computer",
    )
    print("Bengali manual generated: Sentinel-X-User-Manual-BN.pdf")
    print("\nBoth manuals generated successfully!")
