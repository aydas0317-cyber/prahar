PRAHAR — Indian Army Command Decision Training System
Commanders train to make time-critical decisions under degraded comms: incomplete, delayed, and conflicting intelligence.

PRAHAR is a privacy-preserving, local-first command decision training simulator built for the Indian Army. Unlike existing formats (TEWT, CPX) that assume complete and reliable information flow, PRAHAR deliberately injects uncertainty — training decision-making under real-world conditions rather than ideal ones.

🔥 Key Features
Feature	Description
Degraded Comms Simulation	Delay, signal blackout, and packet loss injection on comms links between units
Conflicting Intel	Contradictory intelligence from multiple sources — trainees must weigh reliability
Trust-Weighted Scoring	Every intel source carries a dynamic reliability score
Asymmetric Role-Based Intel	Each role sees different data — Commander sees the full picture, Cyber/EW sees spectrum data, Intel Analyst sees reliability matrix
Decision + Rationale Capture	Trainees set confidence level, write rationale, and submit — intel snapshot captured at decision time
Automated AAR	After-Action Review with decision timeline, cascade analysis, comms failure log, and local AI evaluation
Cascade Detection	Tracks self-reinforcing cycles of cascading failures across the command structure
Real-Time Multiplayer	Socket.IO-powered — multiple trainees join different roles and coordinate live
Team Attribution	ALPHA / BRAVO / AIR-1 / INTEL badges on every decision in the log and AAR
Autoplay Gameplay Demo	Landing page features an animated demo cycling through a full exercise
100% On-Premise	Zero cloud dependency. All data stays local. No external transmission.
🎖️ Command Roles
Role	Team	Intel Access
Commander Alpha	ALPHA	Full map, all sources
Cyber / EW Officer	BRAVO	Spectrum data only
Air Liaison	AIR-1	Air corridor data
Intel Analyst	INTEL	Source reliability matrix
Instructor	—	Full control + inject console
🛠️ Tech Stack
Frontend: Vanilla HTML5, CSS3, SVG tactical map, JavaScript (no framework)

Backend: Node.js + Express

Database: SQLite (better-sqlite3)

Real-Time: Socket.IO

Authentication: Local username/password with session tokens

🚀 Quick Start
Prerequisites
Node.js 18+

npm

Install & Run
bash
# Clone the repository
git clone https://github.com/yourusername/prahar.git
cd prahar

# Install dependencies
npm install

# Start the server
npm start
Open http://localhost:8000 in your browser.

Instructor Login
Enter any username

Use access code: PRAHAR-2024 as the password

Or register as Instructor with the same code

Multiplayer
Open multiple browser tabs with different roles to coordinate in real-time. Each role sees asymmetric intelligence.

📁 Project Structure
text
prahar/
├── index.html          # Main HTML — landing, login, lobby, simulator, AAR views
├── app-v6.js           # Client-side application logic (active version)
├── server.js           # Express + Socket.IO + SQLite backend
├── styles.css          # Full styling — dark tactical command center theme
├── package.json        # Node.js dependencies
├── .gitignore
└── screenshots/        # UI screenshots (16 screenshots)
    ├── screenshot-01-landing.png
    ├── screenshot-07-simulator.png
    ├── screenshot-11-decision-panel.png
    ├── screenshot-13-aar.png
    └── ...
🎮 How It Works
Instructor creates an exercise and starts the scenario

Comms degrade — latency, blackout, packet loss on unit links

Conflicting intel appears — phantom tracks, contradictory reports

Commander selects a course of action (Engage / Recon / Defend / Withdraw)

Confidence level set, rationale written, intel snapshot captured

Decision effect plays out on the tactical map

AAR generates automatically — scores, timeline, AI evaluation, exportable report

🧪 Exercise Flow
text
Normal Comms → Comms Degraded → Conflicting Intel → Decision → AAR
Inject Types
Category	Injects
Comms Degradation	Delay, Signal Blackout, Packet Loss
Conflicting Intel	Air Report, Cyber Alert, Land Intel
Red-Team	Weather, New Threat, False Flag, Info Overload
📊 AAR Scoring
Metric	Description
Decision Quality	Based on confidence, rationale quality, and intel utilization
Response Time	Speed of decision relative to exercise duration
Info Utilization	Number of intel sources processed
Team Coordination	Cascade prevention and coordination quality
AAR is exportable as HTML and JSON.

🖼️ Screenshots
Landing Page	Simulator	Decision Panel	AAR
			
🔒 Security & Privacy
All data stored locally in SQLite

No cloud dependencies

No external API calls (except Google Fonts for typography)

Passwords hashed with SHA-256

Session-based authentication                         

⚠️ Disclaimer
This is a training simulator prototype. All scenarios, intelligence feeds, and AI evaluations are simulated. No operational or classified data is used.

PRAHAR (प्रहार) — Hindi for "strike" or "assault" — reflects the system's purpose: training commanders to strike decisively under uncertainty.
