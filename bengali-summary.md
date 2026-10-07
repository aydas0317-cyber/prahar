## পুরনো ওয়েবসাইটের বিশ্লেষণ

আমি তোমার চারটি জিনিস বিশ্লেষণ করেছি — problem statement, background, PPT (১২টি slide), এবং ZIP ফাইলের ওয়েবসাইট (৩টি ফাইল: index.html, app.js, styles.css)।

### পুরনো ওয়েবসাইট কতটা সম্পূর্ণ ছিল: প্রায় ৬০%

| ক্ষেত্র | স্কোর | ঘাটতি |
|---|---:|---|
| Scenario engine + communication degradation | 18/25 | Configuration panel ছিল না |
| Multiplayer / team coordination | 2/20 | Single-player ছিল, team sync ছিল না |
| Instructor dashboard | 13/20 | Controls ছিল, কিন্তু configuration ছিল না |
| AAR / report export | 13/20 | শুধু print ছিল, download ছিল না |
| UX / polish | 12/15 | Design ভালো ছিল |
| মোট | 58/100 ≈ 60% | |

### PPT-তে যে features ছিল কিন্তু ওয়েবসাইটে ছিল না

- Decision Confidence Slider
- "What Did You Know at the Time?" — decision নেওয়ার সময়ের intel snapshot
- Cascade Detection
- Red-Team Inject Console
- Scenario configuration — tempo, info-loss %, domain selection
- Team coordination panel
- Downloadable AAR — HTML/JSON export

## আমি কী তৈরি করেছি

পুরনো ওয়েবসাইটের ভালো tactical design বজায় রেখে সব missing features যোগ করেছি:

- **Scenario Configuration Panel** — tempo (slow/normal/fast), info-loss %, domain toggles: land/air/cyber/EW
- **Decision Confidence Slider** — trainee নিজের confidence level সেট করতে পারে, evaluator-এ real-time দেখা যায়
- **"What Did You Know at the Time?"** — প্রতিটি decision-এর সঙ্গে সেই মুহূর্তের intel snapshot capture হয় এবং AAR-এ দেখা যায়
- **Cascade Detection** — comms degradation + conflicting intel + overload হলে system নিজে cascade detect করে (arXiv:1607.08139 research-এর উপর ভিত্তি করে)
- **Red-Team Inject Console** — False Flag (friendly-কে hostile দেখানো), Info Overload (একসাথে ৫টি intel), Weather, New Threat
- **Team Coordination Panel** — Commander, Cyber/EW, Air, Intel role-এর live status
- **Role-based Asymmetric Intel** — Cyber officer শুধু spectrum data দেখে, Air liaison শুধু air corridor দেখে, Intel analyst সব দেখে
- **Downloadable AAR** — HTML এবং JSON দুই format-এ export (শুধু print নয়)
- **Cascade Analysis Section** AAR-এ
- **Data-driven Scoring** — random score নয়, actual exercise data থেকে score calculation

## Testing

Testing সম্পূর্ণ হয়েছে:

Instructor নির্বাচন → Start → Comms Delay inject → Conflict inject → Cascade auto-trigger → "Deploy Recon" decision → Confidence 75% set → rationale submit → End → AAR generated।

AAR-এ score (Decision Quality 83/100, Response Time 69/100, Info Utilization 100/100, Team Coordination 80/100), decision timeline, cascade analysis, AI evaluation, HTML export এবং JSON export সব ঠিকভাবে কাজ করছে।

## Multiplayer সম্পর্কে সতর্কতা

এটি **simulated role-based team coordination** — প্রতিটি role আলাদা intel দেখে এবং team status live update হয়। Real-time multiplayer (Socket.IO) করতে হলে backend server দরকার, যা static preview-এর মধ্যে এখন নেই।

---

উপরে attached preview-তে ওয়েবসাইট ready আছে — ক্লিক করে খুলে দেখে নিতে পারো। ZIP ফাইল চাইলে বলো, আমি আলাদা করে দিয়ে দেব।
