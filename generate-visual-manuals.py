#!/usr/bin/env python3
"""Generate Sentinel-X Visual User Manuals — screenshot on one side, instructions on the other.
Three versions: English, Bengali, Hinglish."""
from weasyprint import HTML
from pathlib import Path
import base64

OUTPUT_DIR = Path("/home/user/workspace/sentinel-x")
SCREENSHOT_DIR = OUTPUT_DIR

def img_to_base64(path):
    """Convert image to base64 data URL."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"

# Load all screenshots as base64
screenshots = {}
for f in sorted(SCREENSHOT_DIR.glob("screenshot-*.png")):
    screenshots[f.stem] = img_to_base64(str(f))

# Define the page sections: (screenshot_key, title_en, title_bn, title_hi, description_en, description_bn, description_hi)
PAGES = [
    {
        "screenshot": "screenshot-01-landing",
        "title_en": "Landing Page — Home",
        "title_bn": "ল্যান্ডিং পেজ — হোম",
        "title_hi": "Landing Page — Home",
        "sections_en": [
            ("Top Navigation Bar", "SENTINEL-X logo on the left. Navigation links: System Overview, Live Demo, Innovation, Research, Roadmap. 'Enter Platform' button on the right — click this to access the login/register page."),
            ("Hero Section", "Shows the main headline: 'Trains commanders to make time-critical decisions under incomplete, delayed, and conflicting information'. Key stats: 7 MVP Modules, 4 Command Roles, 100% Local/On-Premise, 0 Cloud Dependency. Two buttons: 'Launch Demo' and 'See How It Works'."),
            ("Tactical Radar Visual", "Right side shows a dark circular tactical radar display with active asset status indicators (3 Assets, 1 Comms Degraded, 1 Signal Lost)."),
        ],
        "sections_bn": [
            ("টপ নেভিগেশন বার", "বামে SENTINEL-X লোগো। নেভিগেশন লিংক: System Overview, Live Demo, Innovation, Research, Roadmap। ডানে 'Enter Platform' বোতাম — এটিতে ক্লিক করে লগইন/রেজিস্টার পেজে যান।"),
            ("হিরো সেকশন", "প্রধান শিরোনাম: 'কমান্ডারদের অসম্পূর্ণ, বিলম্বিত এবং পরস্পরবিরোধী তথ্যের অধীনে সময়-সংবেদনশীল সিদ্ধান্ত নিতে প্রশিক্ষণ দেয়'। মূল পরিসংখ্যান: ৭টি MVP মডিউল, ৪টি কমান্ড রোল, ১০০% লোকাল/অন-প্রেমাইস, ০ ক্লাউড নির্ভরতা।"),
            ("ট্যাক্টিক্যাল রাডার ভিজ্যুয়াল", "ডানদিকে একটি গাঢ় বৃত্তাকার ট্যাক্টিক্যাল রাডার ডিসপ্লে সক্রিয় অ্যাসেট স্ট্যাটাস ইন্ডিকেটর সহ (৩টি অ্যাসেট, ১টি কমিউনিকেশন ডিগ্রেডেড, ১টি সিগন্যাল লস্ট)।"),
        ],
        "sections_hi": [
            ("Top Navigation Bar", "Baayein taraf SENTINEL-X logo. Navigation links: System Overview, Live Demo, Innovation, Research, Roadmap. Right mein 'Enter Platform' button — is par click karke login/register page par jaayein."),
            ("Hero Section", "Main headline: 'Commanders ko incomplete, delayed, aur conflicting information ke under time-critical decisions lene ki training deta hai'. Key stats: 7 MVP Modules, 4 Command Roles, 100% Local/On-Premise, 0 Cloud Dependency."),
            ("Tactical Radar Visual", "Right side mein ek dark circular tactical radar display hai with active asset status indicators (3 Assets, 1 Comms Degraded, 1 Signal Lost)."),
        ],
    },
    {
        "screenshot": "screenshot-03-landing-innovation",
        "title_en": "Landing Page — Innovation Section",
        "title_bn": "ল্যান্ডিং পেজ — ইনোভেশন সেকশন",
        "title_hi": "Landing Page — Innovation Section",
        "sections_en": [
            ("How the System Works", "Four sequential process cards: 01 Instructor Control (injects real-time communication failures), 02 Degraded Information (commander receives incomplete/conflicting data), 03 Decision + Rationale (course of action selection, confidence levels, rationales recorded), 04 Automated AAR (generates post-exercise After-Action Review and analytics)."),
            ("Live Demo Section", "Interactive demo tabs showing: Normal Comms, Comms Degraded, Conflicting Intel, Decision, and AAR phases. 'Launch Full Simulation' button at the bottom."),
        ],
        "sections_bn": [
            ("সিস্টেম কীভাবে কাজ করে", "চারটি ক্রমিক প্রক্রিয়া কার্ড: ০১ ইনস্ট্রাক্টর কন্ট্রোল (রিয়েল-টাইম কমিউনিকেশন ব্যর্থতা ইনজেক্ট করে), ০২ ডিগ্রেডেড ইনফরমেশন (কমান্ডার অসম্পূর্ণ/পরস্পরবিরোধী ডেটা গ্রহণ করে), ০৩ ডিসিশন + রেশনাল (কোর্স অফ অ্যাকশন নির্বাচন, কনফিডেন্স লেভেল), ০৪ অটোমেটেড AAR (পোস্ট-এক্সারসাইজ আফটার-অ্যাকশন রিভিউ)।"),
            ("লাইভ ডেমো সেকশন", "ইন্টারঅ্যাকটিভ ডেমো ট্যাব: Normal Comms, Comms Degraded, Conflicting Intel, Decision, এবং AAR ফেজ। নিচে 'Launch Full Simulation' বোতাম।"),
        ],
        "sections_hi": [
            ("System Kaise Kaam Karta Hai", "Char sequential process cards: 01 Instructor Control (real-time communication failures inject karta hai), 02 Degraded Information (commander ko incomplete/conflicting data milta hai), 03 Decision + Rationale (course of action selection, confidence levels), 04 Automated AAR (post-exercise After-Action Review generate karta hai)."),
            ("Live Demo Section", "Interactive demo tabs: Normal Comms, Comms Degraded, Conflicting Intel, Decision, aur AAR phases. Niche 'Launch Full Simulation' button hai."),
        ],
    },
    {
        "screenshot": "screenshot-04-landing-research",
        "title_en": "Landing Page — Research & Roadmap",
        "title_bn": "ল্যান্ডিং পেজ — রিসার্চ ও রোডম্যাপ",
        "title_hi": "Landing Page — Research & Roadmap",
        "sections_en": [
            ("Research Backing", "Academic papers that inform the system design. Links to arXiv:1607.08139 (self-reinforcing degradation in decision-making teams by Hubbard, Kott, Martin) and arXiv:2603.21280. These papers form the theoretical basis for cascade detection and degraded communication training."),
            ("Roadmap Section", "Shows the development roadmap with future milestones and planned features for the Sentinel-X platform."),
        ],
        "sections_bn": [
            ("রিসার্চ ব্যাকিং", "সিস্টেম ডিজাইনকে নির্দেশ করে এমন একাডেমিক পেপার। arXiv:1607.08139 (Hubbard, Kott, Martin দ্বারা সিদ্ধান্ত গ্রহণের দলে self-reinforcing ডিগ্রেডেশন) এবং arXiv:2603.21280 লিংক। এই পেপারগুলি ক্যাসকেড ডিটেকশন এবং ডিগ্রেডেড কমিউনিকেশন প্রশিক্ষণের তাত্ত্বিক ভিত্তি গঠন করে।"),
            ("রোডম্যাপ সেকশন", "ভবিষ্যতের মাইলস্টোন এবং Sentinel-X প্ল্যাটফর্মের জন্য পরিকল্পিত বৈশিষ্ট্যগুলির সাথে ডেভেলপমেন্ট রোডম্যাপ দেখায়।"),
        ],
        "sections_hi": [
            ("Research Backing", "Academic papers jo system design ko inform karte hain. arXiv:1607.08139 (Hubbard, Kott, Martin dwara decision-making teams mein self-reinforcing degradation) aur arXiv:2603.21280 ke links. Ye papers cascade detection aur degraded communication training ke theoretical basis hain."),
            ("Roadmap Section", "Development roadmap dikhata hai with future milestones aur Sentinel-X platform ke liye planned features."),
        ],
    },
    {
        "screenshot": "screenshot-06-lobby",
        "title_en": "Command Lobby — Create & Join Exercises",
        "title_bn": "কমান্ড লবি — এক্সারসাইজ তৈরি ও যোগদান",
        "title_hi": "Command Lobby — Exercise Create & Join",
        "sections_en": [
            ("Header", "Shows 'Welcome, testcmdr (Instructor)' with a Logout button. The Command Lobby title is displayed in green."),
            ("Create New Exercise", "Enter an exercise name (e.g., OP DEEP FOG) in the EXERCISE NAME field and click 'Create & Enter as Instructor'. The system generates a unique code and you enter the simulator as instructor."),
            ("Join Existing Exercise", "Enter the exercise code provided by your instructor, select your role (Commander Alpha, Cyber/EW Officer, Air Liaison, or Intel Analyst) from the dropdown, and click 'Join Exercise'."),
            ("Your Exercises", "Lists all exercises you have created or joined, showing name, code, status (created/active/ended), and your role."),
        ],
        "sections_bn": [
            ("হেডার", "'Welcome, testcmdr (Instructor)' একটি Logout বোতাম সহ দেখায়। কমান্ড লবি শিরোনাম সবুজ রঙে প্রদর্শিত হয়।"),
            ("নতুন এক্সারসাইজ তৈরি করুন", "EXERCISE NAME ফিল্ডে একটি এক্সারসাইজ নাম লিখুন (যেমন OP DEEP FOG) এবং 'Create & Enter as Instructor' এ ক্লিক করুন। সিস্টেম একটি ইউনিক কোড তৈরি করে এবং আপনি ইনস্ট্রাক্টর হিসেবে সিমুলেটরে প্রবেশ করেন।"),
            ("বিদ্যমান এক্সারসাইজে যোগ দিন", "আপনার ইনস্ট্রাক্টর দ্বারা প্রদত্ত এক্সারসাইজ কোড লিখুন, ড্রপডাউন থেকে আপনার রোল নির্বাচন করুন (Commander Alpha, Cyber/EW Officer, Air Liaison, বা Intel Analyst) এবং 'Join Exercise' এ ক্লিক করুন।"),
            ("আপনার এক্সারসাইজ", "আপনার তৈরি বা যোগ দেওয়া সকল এক্সারসাইজের তালিকা — নাম, কোড, স্ট্যাটাস (created/active/ended), এবং আপনার রোল সহ।"),
        ],
        "sections_hi": [
            ("Header", "'Welcome, testcmdr (Instructor)' dikhta hai Logout button ke saath. Command Lobby title green colour mein displayed hai."),
            ("Create New Exercise", "EXERCISE NAME field mein exercise naam likhein (jaise OP DEEP FOG) aur 'Create & Enter as Instructor' par click karein. System ek unique code generate karta hai aur aap instructor banke simulator mein enter karte hain."),
            ("Join Existing Exercise", "Apne instructor dwara diye gaye exercise code ko likhein, dropdown se apna role select karein (Commander Alpha, Cyber/EW Officer, Air Liaison, ya Intel Analyst) aur 'Join Exercise' par click karein."),
            ("Your Exercises", "Aapke dwara create ya join kiye gaye saare exercises ki list — naam, code, status (created/active/ended), aur aapka role ke saath."),
        ],
    },
    {
        "screenshot": "screenshot-07-simulator",
        "title_en": "Simulator — Standby Mode (Before Start)",
        "title_bn": "সিমুলেটর — স্ট্যান্ডবাই মোড (শুরুর আগে)",
        "title_hi": "Simulator — Standby Mode (Start se pehle)",
        "sections_en": [
            ("Top Status Bar", "SENTINEL-X logo with STANDBY status badge. Exercise timer shows T+00:00:00. Exercise name (OP DEEP FOG) displayed. Role indicator shows 'Instructor'. Exit button on the right."),
            ("Phase Tabs", "Five tabs showing exercise progression: Normal Comms (active), Comms Degraded, Conflicting Intel, Decision, and AAR."),
            ("Left Sidebar — Exercise Control", "Start, Pause, and End buttons. Scenario Configuration: Tempo dropdown (Slow/Normal/Fast), Info Loss % slider, Domain checkboxes (Land, Air, Cyber, EW)."),
            ("Left Sidebar — Inject Controls", "Three groups: Inject Comms Degradation (Comms Delay, Signal Blackout, Packet Loss), Inject Conflicting Intel (Air Report, Cyber Alert, Land Intel), Red-Team Inject Console (Weather Degrade, New Threat, False Flag Op, Info Overload)."),
            ("Center — Tactical Map", "Grid map of Sector Golf-7 with coordinate labels A-J and 1-5. Shows friendly units (ALPHA, BRAVO, AIR-1 in green), hostile units (HOSTILE in red), unknown units (UNKNOWN, UNCONFIRMED in yellow), objective zones (OBJ ALPHA, ENEMY ZONE)."),
            ("Right — Intelligence Feed", "Displays 'Awaiting exercise start...' until the exercise begins."),
        ],
        "sections_bn": [
            ("টপ স্ট্যাটাস বার", "SENTINEL-X লোগো স্ট্যান্ডবাই স্ট্যাটাস ব্যাজ সহ। এক্সারসাইজ টাইমার T+00:00:00 দেখায়। এক্সারসাইজ নাম (OP DEEP FOG) প্রদর্শিত। রোল ইন্ডিকেটর 'Instructor' দেখায়। ডানে Exit বোতাম।"),
            ("ফেজ ট্যাব", "পাঁচটি ট্যাব এক্সারসাইজ অগ্রগতি দেখায়: Normal Comms (সক্রিয়), Comms Degraded, Conflicting Intel, Decision, এবং AAR।"),
            ("বাম সাইডবার — এক্সারসাইজ কন্ট্রোল", "Start, Pause, এবং End বোতাম। সিনারিও কনফিগারেশন: Tempo ড্রপডাউন (Slow/Normal/Fast), Info Loss % স্লাইডার, ডোমেইন চেকবক্স (Land, Air, Cyber, EW)।"),
            ("বাম সাইডবার — ইনজেক্ট কন্ট্রোল", "তিনটি গ্রুপ: Inject Comms Degradation (Comms Delay, Signal Blackout, Packet Loss), Inject Conflicting Intel (Air Report, Cyber Alert, Land Intel), Red-Team Inject Console (Weather Degrade, New Threat, False Flag Op, Info Overload)।"),
            ("কেন্দ্র — ট্যাক্টিক্যাল ম্যাপ", "Sector Golf-7 এর গ্রিড ম্যাপ কোঅর্ডিনেট লেবেল A-J এবং 1-5 সহ। বন্ধুত্বপূর্ণ ইউনিট (ALPHA, BRAVO, AIR-1 সবুজ), শত্রু ইউনিট (HOSTILE লাল), অজানা ইউনিট (UNKNOWN, UNCONFIRMED হলুদ), অবজেক্টিভ জোন (OBJ ALPHA, ENEMY ZONE) দেখায়।"),
            ("ডান — ইন্টেলিজেন্স ফিড", "এক্সারসাইজ শুরু না হওয়া পর্যন্ত 'Awaiting exercise start...' প্রদর্শন করে।"),
        ],
        "sections_hi": [
            ("Top Status Bar", "SENTINEL-X logo with STANDBY status badge. Exercise timer T+00:00:00 dikhata hai. Exercise naam (OP DEEP FOG) displayed. Role indicator 'Instructor' dikhata hai. Right mein Exit button."),
            ("Phase Tabs", "Paanch tabs exercise progression dikhate hain: Normal Comms (active), Comms Degraded, Conflicting Intel, Decision, aur AAR."),
            ("Left Sidebar — Exercise Control", "Start, Pause, aur End buttons. Scenario Configuration: Tempo dropdown (Slow/Normal/Fast), Info Loss % slider, Domain checkboxes (Land, Air, Cyber, EW)."),
            ("Left Sidebar — Inject Controls", "Teen groups: Inject Comms Degradation (Comms Delay, Signal Blackout, Packet Loss), Inject Conflicting Intel (Air Report, Cyber Alert, Land Intel), Red-Team Inject Console (Weather Degrade, New Threat, False Flag Op, Info Overload)."),
            ("Center — Tactical Map", "Sector Golf-7 ka grid map coordinate labels A-J aur 1-5 ke saath. Friendly units (ALPHA, BRAVO, AIR-1 green), hostile units (HOSTILE red), unknown units (UNKNOWN, UNCONFIRMED yellow), objective zones (OBJ ALPHA, ENEMY ZONE) dikhata hai."),
            ("Right — Intelligence Feed", "Exercise start hone tak 'Awaiting exercise start...' dikhata hai."),
        ],
    },
    {
        "screenshot": "screenshot-08-simulator-active",
        "title_en": "Simulator — Exercise Active (Normal Comms)",
        "title_bn": "সিমুলেটর — এক্সারসাইজ সক্রিয় (নরমাল কমিউনিকেশন)",
        "title_hi": "Simulator — Exercise Active (Normal Comms)",
        "sections_en": [
            ("Status Change", "Status badge changes from STANDBY to EXERCISE ACTIVE (green). Timer starts counting. Team coordination roles (CMD Alpha, Cyber/EW) change to ACTIVE."),
            ("Intel Feed Populated", "The Intelligence Feed starts receiving baseline reports: 'Air patrol nominal', 'All units in position'. Each entry shows timestamp, message, source, and reliability score (HIGH/MEDIUM/LOW)."),
            ("Map State", "Tactical map shows normal green communication links between units. All friendly units (ALPHA, BRAVO, AIR-1) are connected and operational."),
        ],
        "sections_bn": [
            ("স্ট্যাটাস পরিবর্তন", "স্ট্যাটাস ব্যাজ STANDBY থেকে EXERCISE ACTIVE (সবুজ) এ পরিবর্তিত হয়। টাইমার গণনা শুরু করে। টিম কোঅর্ডিনেশন রোল (CMD Alpha, Cyber/EW) ACTIVE তে পরিবর্তিত হয়।"),
            ("ইন্টেল ফিড পপুলেটেড", "ইন্টেলিজেন্স ফিড বেসলাইন রিপোর্ট গ্রহণ শুরু করে: 'Air patrol nominal', 'All units in position'। প্রতিটি এন্ট্রিতে টাইমস্ট্যাম্প, বার্তা, উৎস, এবং নির্ভরযোগ্যতা স্কোর (HIGH/MEDIUM/LOW) থাকে।"),
            ("ম্যাপ স্টেট", "ট্যাক্টিক্যাল ম্যাপ ইউনিটের মধ্যে স্বাভাবিক সবুজ যোগাযোগ লিংক দেখায়। সমস্ত বন্ধুত্বপূর্ণ ইউনিট (ALPHA, BRAVO, AIR-1) সংযুক্ত এবং কার্যকর।"),
        ],
        "sections_hi": [
            ("Status Change", "Status badge STANDBY se EXERCISE ACTIVE (green) mein change hota hai. Timer count karna shuru karta hai. Team coordination roles (CMD Alpha, Cyber/EW) ACTIVE ho jate hain."),
            ("Intel Feed Populated", "Intelligence Feed baseline reports receive karna shuru karta hai: 'Air patrol nominal', 'All units in position'. Har entry mein timestamp, message, source, aur reliability score (HIGH/MEDIUM/LOW) hota hai."),
            ("Map State", "Tactical map units ke beech normal green communication links dikhata hai. Saare friendly units (ALPHA, BRAVO, AIR-1) connected aur operational hain."),
        ],
    },
    {
        "screenshot": "screenshot-09-comms-degraded",
        "title_en": "Simulator — Comms Degradation Injected",
        "title_bn": "সিমুলেটর — কমিউনিকেশন ডিগ্রেডেশন ইনজেক্ট করা হয়েছে",
        "title_hi": "Simulator — Comms Degradation Injected",
        "sections_en": [
            ("Comms Delay Effect", "The instructor clicked 'Comms Delay'. Network links on the tactical map turn into dashed amber lines. Yellow latency badges (LATENCY - ALPHA, LATENCY - BRAVO, LATENCY - AIR) appear on the map."),
            ("Intel Feed Warning", "The Intelligence Feed logs: '3-5s latency on all feeds — all channels affected'. This simulates real-world communication delays in degraded environments."),
            ("Auto-Recovery", "After approximately 8 seconds, the degradation automatically recovers. A 'COMMS RESTORED' message is injected into the intel feed, and links return to green."),
        ],
        "sections_bn": [
            ("কমিউনিকেশন ডিলে প্রভাব", "ইনস্ট্রাক্টর 'Comms Delay' এ ক্লিক করেছেন। ট্যাক্টিক্যাল ম্যাপে নেটওয়ার্ক লিংক ড্যাশড অ্যাম্বার লাইনে পরিণত হয়। হলুদ লেটেন্সি ব্যাজ (LATENCY - ALPHA, LATENCY - BRAVO, LATENCY - AIR) ম্যাপে আবির্ভূত হয়।"),
            ("ইন্টেল ফিড সতর্কতা", "ইন্টেলিজেন্স ফিড লগ করে: '3-5s latency on all feeds — all channels affected'। এটি ডিগ্রেডেড পরিবেশে বাস্তব-বিশ্ব যোগাযোগ বিলম্ব অনুকরণ করে।"),
            ("অটো-রিকভারি", "প্রায় ৮ সেকেন্ড পরে ডিগ্রেডেশন স্বয়ংক্রিয়ভাবে পুনরুদ্ধার হয়। একটি 'COMMS RESTORED' বার্তা ইন্টেল ফিডে ইনজেক্ট করা হয় এবং লিংক সবুজে ফিরে আসে।"),
        ],
        "sections_hi": [
            ("Comms Delay Effect", "Instructor ne 'Comms Delay' par click kiya. Tactical map par network links dashed amber lines ban jaate hain. Yellow latency badges (LATENCY - ALPHA, LATENCY - BRAVO, LATENCY - AIR) map par appear hote hain."),
            ("Intel Feed Warning", "Intelligence Feed log karta hai: '3-5s latency on all feeds — all channels affected'. Ye real-world communication delays ko simulate karta hai degraded environments mein."),
            ("Auto-Recovery", "Lagbhag 8 second baad degradation automatically recover hota hai. Ek 'COMMS RESTORED' message intel feed mein inject hota hai aur links wapas green ho jaate hain."),
        ],
    },
    {
        "screenshot": "screenshot-11-decision-panel",
        "title_en": "Simulator — Conflicting Intel & Cascade Warning",
        "title_bn": "সিমুলেটর — পরস্পরবিরোধী ইন্টেল ও ক্যাসকেড সতর্কতা",
        "title_hi": "Simulator — Conflicting Intel & Cascade Warning",
        "sections_en": [
            ("Phantom Contact", "After injecting 'Conflicting Air Report', a dashed unconfirmed phantom contact marked '? UNCONFIRMED' appears near AIR-1 on the tactical map. This represents divergent sensor data."),
            ("Diverging Intel", "The Intelligence Feed shows contradictory reports: Radar reports 2 hostile aircraft, while ELINT reports 4 enemy aircraft. The reliability scores differ, forcing the commander to assess which source to trust."),
            ("Cascade Warning", "When 2+ comms channels are degraded AND 1+ conflicting intel is present, the system automatically detects a cascade condition and injects a 'CASCADE WARNING: Self-reinforcing degradation detected' into the intel feed."),
        ],
        "sections_bn": [
            ("ফ্যান্টম কন্টাক্ট", "'Conflicting Air Report' ইনজেক্ট করার পর, ট্যাক্টিক্যাল ম্যাপে AIR-1 এর কাছে একটি ড্যাশড অনুনিশ্চিত ফ্যান্টম কন্টাক্ট '? UNCONFIRMED' হিসেবে আবির্ভূত হয়। এটি ভিন্ন সেন্সর ডেটা প্রতিনিধিত্ব করে।"),
            ("ভিন্ন ইন্টেল", "ইন্টেলিজেন্স ফিড পরস্পরবিরোধী রিপোর্ট দেখায়: রাডার ২টি শত্রু বিমান রিপোর্ট করে, যখন ELINT ৪টি শত্রু বিমান রিপোর্ট করে। নির্ভরযোগ্যতা স্কোর ভিন্ন, কমান্ডারকে কোন উৎসকে বিশ্বাস করতে হবে তা মূল্যায়ন করতে বাধ্য করে।"),
            ("ক্যাসকেড সতর্কতা", "যখন ২+ কমিউনিকেশন চ্যানেল ডিগ্রেডেড এবং ১+ পরস্পরবিরোধী ইন্টেল উপস্থিত, সিস্টেম স্বয়ংক্রিয়ভাবে একটি ক্যাসকেড কন্ডিশন শনাক্ত করে এবং ইন্টেল ফিডে একটি 'CASCADE WARNING: Self-reinforcing degradation detected' ইনজেক্ট করে।"),
        ],
        "sections_hi": [
            ("Phantom Contact", "'Conflicting Air Report' inject karne ke baad, tactical map par AIR-1 ke paas ek dashed unconfirmed phantom contact '? UNCONFIRMED' appear hota hai. Ye divergent sensor data represent karta hai."),
            ("Diverging Intel", "Intelligence Feed contradictory reports dikhata hai: Radar 2 hostile aircraft report karta hai, jabki ELINT 4 enemy aircraft report karta hai. Reliability scores alag hain, commander ko assess karna padta hai kaunse source par bharosa karein."),
            ("Cascade Warning", "Jab 2+ comms channels degraded hain AUR 1+ conflicting intel present hai, system automatically cascade condition detect karta hai aur intel feed mein 'CASCADE WARNING: Self-reinforcing degradation detected' inject karta hai."),
        ],
    },
    {
        "screenshot": "screenshot-12-decision-confidence",
        "title_en": "Decision Submission & Confidence Slider",
        "title_bn": "সিদ্ধান্ত জমা ও কনফিডেন্স স্লাইডার",
        "title_hi": "Decision Submission & Confidence Slider",
        "sections_en": [
            ("Decision Options", "Four course-of-action buttons: Engage Hostile (attack vectors drawn, units move to engage), Deploy Recon (recon path drawn, unit moves to investigate), Fortify Position (defensive perimeters appear), Tactical Withdrawal (retreat paths drawn, units reposition)."),
            ("Confidence Slider", "After selecting a decision, a confidence slider appears (0-100%). The trainee self-reports their confidence level. The system tracks overconfidence (high confidence with limited intel) and hesitation (low confidence with ample intel)."),
            ("Rationale Input", "A text area for the trainee to provide written rationale for their decision. This is captured along with an intel snapshot at the moment of submission — supporting the 'What Did You Know at the Time?' evaluation."),
            ("Cascade Detection Panel", "Shows real-time cascade status. Trust vs Speed Evaluator displays Info Reliability %, Uncertainty level, and Decision Clock."),
        ],
        "sections_bn": [
            ("সিদ্ধান্ত অপশন", "চারটি কোর্স-অফ-অ্যাকশন বোতাম: Engage Hostile (অ্যাটাক ভেক্টর আঁকা, ইউনিট শত্রুকে আক্রমণ করতে চলে), Deploy Recon (রেকন পথ আঁকা, ইউনিট তদন্ত করতে চলে), Fortify Position (প্রতিরক্ষামূলক পরিধি দেখা যায়), Tactical Withdrawal (পিছু হটার পথ আঁকা, ইউনিট পুনঃঅবস্থান নেয়)।"),
            ("কনফিডেন্স স্লাইডার", "সিদ্ধান্ত নির্বাচনের পর একটি কনফিডেন্স স্লাইডার প্রদর্শিত হয় (০-১০০%)। ট্রেইনি নিজের আত্মবিশ্বাস স্তর সেট করে। সিস্টেম overconfidence (সীমিত ইন্টেলে উচ্চ আত্মবিশ্বাস) এবং hesitation (প্রচুর ইন্টেলে নিম্ন আত্মবিশ্বাস) ট্র্যাক করে।"),
            ("রেশনাল ইনপুট", "ট্রেইনির সিদ্ধান্তের জন্য লিখিত রেশনাল প্রদানের একটি টেক্সট এরিয়া। এটি জমার মুহূর্তে একটি ইন্টেল স্ন্যাপশটের সাথে ক্যাপচার করা হয় — 'What Did You Know at the Time?' মূল্যায়নকে সমর্থন করে।"),
            ("ক্যাসকেড ডিটেকশন প্যানেল", "রিয়েল-টাইম ক্যাসকেড স্ট্যাটাস দেখায়। Trust vs Speed Evaluator ইনফো রিলায়েবিলিটি %, আনসারটেন্টি লেভেল, এবং ডিসিশন ক্লক প্রদর্শন করে।"),
        ],
        "sections_hi": [
            ("Decision Options", "Chaar course-of-action buttons: Engage Hostile (attack vectors draw hote hain, units engage karne move karte hain), Deploy Recon (recon path draw hota hai, unit investigate karne move karta hai), Fortify Position (defensive perimeters appear hote hain), Tactical Withdrawal (retreat paths draw hote hain, units reposition karte hain)।"),
            ("Confidence Slider", "Decision select karne ke baad ek confidence slider appear hota hai (0-100%)। Trainee apna confidence level set karta hai. System overconfidence (limited intel par high confidence) aur hesitation (ample intel par low confidence) track karta hai।"),
            ("Rationale Input", "Trainee ke decision ke liye written rationale ka ek text area। Ye submission ke moment par ek intel snapshot ke saath capture hota hai — 'What Did You Know at the Time?' evaluation ko support karta hai।"),
            ("Cascade Detection Panel", "Real-time cascade status dikhata hai। Trust vs Speed Evaluator Info Reliability %, Uncertainty level, aur Decision Clock display karta hai।"),
        ],
    },
    {
        "screenshot": "screenshot-14-aar-timeline",
        "title_en": "After-Action Review (AAR) — Timeline & Analysis",
        "title_bn": "আফটার-অ্যাকশন রিভিউ (AAR) — টাইমলাইন ও বিশ্লেষণ",
        "title_hi": "After-Action Review (AAR) — Timeline & Analysis",
        "sections_en": [
            ("AAR Header", "Shows exercise name (OP DEEP FOG), code, duration (T+00:00:20), and participants. Export HTML, Export JSON, and Return buttons in the top right."),
            ("Score Cards", "Four metric cards: Decision Quality, Response Time, Info Utilization, Team Coordination — each scored 0-100 based on exercise performance."),
            ("Decision Timeline", "Chronological view of all events: comms delays, conflicting intel, decisions made, and cascades detected. Each event shows timestamp and description."),
            ("Cascade Analysis", "Details any detected cascades with trigger descriptions. Shows 'No cascades detected' if information was managed well."),
            ("Communication Failures Log", "All injected degradation events with timestamps — comms delays, blackouts, packet losses."),
            ("AI Evaluation & Improvement", "Local AI evaluation gives overall rating (EXCELLENT/PROFICIENT/DEVELOPING/NEEDS RETRAINING) with findings and personalized recommendations."),
        ],
        "sections_bn": [
            ("AAR হেডার", "এক্সারসাইজ নাম (OP DEEP FOG), কোড, সময়কাল (T+00:00:20), এবং অংশগ্রহণকারী দেখায়। উপরে ডানে Export HTML, Export JSON, এবং Return বোতাম।"),
            ("স্কোর কার্ড", "চারটি মেট্রিক কার্ড: Decision Quality, Response Time, Info Utilization, Team Coordination — প্রতিটি এক্সারসাইজ পারফরম্যান্সের উপর ভিত্তি করে ০-১০০ স্কোর করা হয়।"),
            ("সিদ্ধান্ত টাইমলাইন", "সকল ইভেন্টের কালানুক্রমিক ভিউ: কমিউনিকেশন ডিলে, পরস্পরবিরোধী ইন্টেল, গৃহীত সিদ্ধান্ত, এবং শনাক্ত ক্যাসকেড। প্রতিটি ইভেন্টে টাইমস্ট্যাম্প এবং বর্ণনা দেখায়।"),
            ("ক্যাসকেড বিশ্লেষণ", "শনাক্ত করা ক্যাসকেডের বিস্তারিত ট্রিগার বর্ণনা সহ। তথ্য ভালভাবে পরিচালিত হলে 'No cascades detected' দেখায়।"),
            ("কমিউনিকেশন ফেইলিওর লগ", "সকল ইনজেক্টেড ডিগ্রেডেশন ইভেন্ট টাইমস্ট্যাম্প সহ — কমিউনিকেশন ডিলে, ব্ল্যাকআউট, প্যাকেট লস।"),
            ("AI মূল্যায়ন ও উন্নতি", "লোকাল AI মূল্যায়ন সামগ্রিক রেটিং (EXCELLENT/PROFICIENT/DEVELOPING/NEEDS RETRAINING) ফাইন্ডিং এবং ব্যক্তিগতকৃত সুপারিশ সহ দেয়।"),
        ],
        "sections_hi": [
            ("AAR Header", "Exercise naam (OP DEEP FOG), code, duration (T+00:00:20), aur participants dikhata hai. Top right mein Export HTML, Export JSON, aur Return buttons."),
            ("Score Cards", "Chaar metric cards: Decision Quality, Response Time, Info Utilization, Team Coordination — har ek exercise performance par based 0-100 score hota hai."),
            ("Decision Timeline", "Saare events ka chronological view: comms delays, conflicting intel, decisions made, aur cascades detected. Har event mein timestamp aur description hota hai."),
            ("Cascade Analysis", "Detected cascades ki detail trigger descriptions ke saath. Agar information well-managed rahi toh 'No cascades detected' dikhata hai."),
            ("Communication Failures Log", "Saare injected degradation events timestamps ke saath — comms delays, blackouts, packet losses."),
            ("AI Evaluation & Improvement", "Local AI evaluation overall rating (EXCELLENT/PROFICIENT/DEVELOPING/NEEDS RETRAINING) findings aur personalized recommendations ke saath deta hai."),
        ],
    },
    {
        "screenshot": "screenshot-15-aar-export",
        "title_en": "AAR — Export Options",
        "title_bn": "AAR — এক্সপোর্ট অপশন",
        "title_hi": "AAR — Export Options",
        "sections_en": [
            ("Export HTML", "Click 'Export HTML' to download a fully formatted report with tables, timelines, and score cards. This creates a printable, shareable document."),
            ("Export JSON", "Click 'Export JSON' to download raw structured data. Useful for integration with other systems, programmatic analysis, or archival."),
            ("Return Button", "Click 'Return' to go back to the Command Lobby where you can create a new exercise or join another one."),
        ],
        "sections_bn": [
            ("HTML এক্সপোর্ট", "টেবিল, টাইমলাইন এবং স্কোর কার্ড সহ একটি সম্পূর্ণ ফরম্যাটেড রিপোর্ট ডাউনলোড করতে 'Export HTML' এ ক্লিক করুন। এটি একটি প্রিন্টযোগ্য, শেয়ারযোগ্য ডকুমেন্ট তৈরি করে।"),
            ("JSON এক্সপোর্ট", "কাঁচা স্ট্রাকচার্ড ডেটা ডাউনলোড করতে 'Export JSON' এ ক্লিক করুন। অন্যান্য সিস্টেমের সাথে ইন্টিগ্রেশন, প্রোগ্রাম্যাটিক বিশ্লেষণ, বা আর্কাইভের জন্য উপযোগী।"),
            ("রিটার্ন বোতাম", "কমান্ড লবিতে ফিরে যেতে 'Return' এ ক্লিক করুন যেখানে আপনি নতুন এক্সারসাইজ তৈরি করতে বা অন্যটিতে যোগ দিতে পারেন।"),
        ],
        "sections_hi": [
            ("Export HTML", "Tables, timelines aur score cards ke saath ek fully formatted report download karne ke liye 'Export HTML' par click karein. Ye ek printable, shareable document banata hai."),
            ("Export JSON", "Raw structured data download karne ke liye 'Export JSON' par click karein. Dusre systems ke saath integration, programmatic analysis, ya archival ke liye useful."),
            ("Return Button", "Command Lobby par wapas jaane ke liye 'Return' par click karein jahan aap naya exercise create kar sakte hain ya kisi aur mein join kar sakte hain."),
        ],
    },
]


CSS = """
@page {
    size: A4 landscape;
    margin: 12mm 10mm 10mm 10mm;
    @top-center {
        content: "SENTINEL-X — Visual User Manual";
        font-family: 'Noto Sans Bengali', 'Inter', sans-serif;
        font-size: 8pt;
        color: #3dd68c;
        font-weight: bold;
        letter-spacing: 1px;
    }
    @bottom-right {
        content: "Page " counter(page);
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: #5a6b80;
    }
    @bottom-left {
        content: "Sentinel-X — Multi-Domain Decision Trainer";
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: #5a6b80;
    }
}

@page :first {
    @top-center { content: ""; }
    @bottom-left { content: ""; }
    @bottom-right { content: ""; }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Noto Sans Bengali', 'Inter', sans-serif;
    color: #1a1a2e;
    line-height: 1.5;
    font-size: 9.5pt;
}

.cover {
    text-align: center;
    padding-top: 120px;
    page-break-after: always;
}

.cover h1 {
    font-size: 32pt;
    color: #3dd68c;
    margin-bottom: 8px;
}

.cover .subtitle {
    font-size: 12pt;
    color: #5a6b80;
    margin-bottom: 40px;
}

.cover .label {
    font-size: 14pt;
    color: #01696F;
    font-weight: bold;
    margin-top: 20px;
}

.cover .version {
    font-size: 11pt;
    color: #5a6b80;
    margin-top: 6px;
}

.manual-page {
    page-break-after: always;
    width: 100%;
}

.manual-page:last-child {
    page-break-after: auto;
}

.manual-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}

.manual-table td {
    vertical-align: top;
    padding: 0;
}

.manual-table td.screenshot-cell {
    width: 55%;
    padding-right: 10px;
}

.manual-table td.instructions-cell {
    width: 45%;
    padding-left: 10px;
}

.screenshot-side img {
    width: 100%;
    max-height: 165mm;
    border: 2px solid #1a2438;
    border-radius: 4px;
    object-fit: contain;
}

.screenshot-label {
    text-align: center;
    font-size: 8pt;
    color: #5a6b80;
    margin-top: 4px;
    font-style: italic;
}

.instructions-side h2 {
    font-size: 12pt;
    color: #01696F;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 2px solid #01696F;
}

.instructions-side h3 {
    font-size: 10pt;
    color: #28251D;
    margin-top: 10px;
    margin-bottom: 4px;
}

.instructions-side p {
    font-size: 9pt;
    margin-bottom: 6px;
    text-align: justify;
}

b, strong {
    color: #0C4E54;
}
"""


def build_manual(lang="en"):
    """Build manual in specified language (en, bn, hi)."""
    lang_names = {
        "en": ("English", "USER MANUAL", "Version 5.0 | Fullstack Edition"),
        "bn": ("বাংলা", "ব্যবহারকারী ম্যানুয়াল", "সংস্করণ ৫.০ | ফুলস্ট্যাক এডিশন"),
        "hi": ("Hinglish", "USER MANUAL", "Version 5.0 | Fullstack Edition"),
    }
    
    title_key = {"en": "title_en", "bn": "title_bn", "hi": "title_hi"}
    sections_key = {"en": "sections_en", "bn": "sections_bn", "hi": "sections_hi"}
    
    lang_name, cover_label, cover_version = lang_names[lang]
    
    html_parts = [f"""
<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="UTF-8"><style>{CSS}</style></head>
<body>

<div class="cover">
    <h1>SENTINEL-X</h1>
    <p class="subtitle">Multi-Domain Decision Trainer for Degraded Communication Environments</p>
    <p class="label">{cover_label}</p>
    <p class="version">{cover_version}</p>
</div>
"""]
    
    for page in PAGES:
        screenshot_data = screenshots.get(page["screenshot"], "")
        title = page[title_key[lang]]
        sections = page[sections_key[lang]]
        
        sections_html = ""
        for heading, desc in sections:
            sections_html += f"<h3>{heading}</h3><p>{desc}</p>"
        
        html_parts.append(f"""
<div class="manual-page">
<table class="manual-table"><tr>
    <td class="screenshot-cell">
        <div class="screenshot-side">
            <img src="{screenshot_data}" alt="{title}" />
            <div class="screenshot-label">{title}</div>
        </div>
    </td>
    <td class="instructions-cell">
        <div class="instructions-side">
            <h2>{title}</h2>
            {sections_html}
        </div>
    </td>
</tr></table>
</div>
""")
    
    html_parts.append("</body></html>")
    
    return "\n".join(html_parts)


if __name__ == "__main__":
    for lang, filename in [("en", "Sentinel-X-Visual-Manual-EN.pdf"), 
                           ("bn", "Sentinel-X-Visual-Manual-BN.pdf"),
                           ("hi", "Sentinel-X-Visual-Manual-HI.pdf")]:
        print(f"Generating {lang} manual...")
        html = build_manual(lang)
        HTML(string=html).write_pdf(
            str(OUTPUT_DIR / filename),
            title=f"Sentinel-X Visual User Manual ({lang})",
            author="Perplexity Computer",
        )
        print(f"Generated: {filename}")
    
    print("\nAll three visual manuals generated successfully!")
