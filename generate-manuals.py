#!/usr/bin/env python3
"""Generate Sentinel-X User Manual PDFs — English and Bengali versions."""
import urllib.request
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Register fonts
FONT_DIR = Path("/tmp/fonts")
pdfmetrics.registerFont(TTFont("Inter", str(FONT_DIR / "Inter.ttf")))
pdfmetrics.registerFont(TTFont("Inter-Bold", str(FONT_DIR / "Inter.ttf")))
pdfmetrics.registerFont(TTFont("NotoBengali", "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf"))
pdfmetrics.registerFont(TTFont("NotoBengali-Bold", "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf"))
pdfmetrics.registerFont(TTFont("NotoBengali-Medium", "/usr/share/fonts/truetype/noto/NotoSansBengali-Medium.ttf"))

# Colors (matching Sentinel-X theme)
DARK_BG = HexColor("#04060d")
DARK_SURFACE = HexColor("#080d18")
PRIMARY = HexColor("#3dd68c")
PRIMARY_DIM = HexColor("#2aa86a")
TEXT_COLOR = HexColor("#1a1a2e")
TEXT_MUTED = HexColor("#5a6b80")
BORDER = HexColor("#1a2438")
ACCENT_CYAN = HexColor("#06b6d4")
ACCENT_WARN = HexColor("#f59e0b")
ACCENT_CRIT = HexColor("#ef4444")
LIGHT_BG = HexColor("#f7f6f2")
SURFACE_BG = HexColor("#f9f8f5")

# ===== ENGLISH STYLES =====
styles_en = getSampleStyleSheet()

style_en_title = ParagraphStyle("Title_EN", parent=styles_en["Title"], fontName="Inter-Bold", fontSize=24, leading=30, textColor=PRIMARY, spaceAfter=6, alignment=TA_LEFT)
style_en_subtitle = ParagraphStyle("Subtitle_EN", parent=styles_en["Normal"], fontName="Inter", fontSize=12, leading=16, textColor=TEXT_MUTED, spaceAfter=20, alignment=TA_LEFT)
style_en_h1 = ParagraphStyle("H1_EN", parent=styles_en["Heading1"], fontName="Inter-Bold", fontSize=16, leading=22, textColor=PRIMARY, spaceBefore=24, spaceAfter=10, alignment=TA_LEFT)
style_en_h2 = ParagraphStyle("H2_EN", parent=styles_en["Heading2"], fontName="Inter-Bold", fontSize=13, leading=18, textColor=HexColor("#28251D"), spaceBefore=16, spaceAfter=8, alignment=TA_LEFT)
style_en_body = ParagraphStyle("Body_EN", parent=styles_en["Normal"], fontName="Inter", fontSize=10, leading=15, textColor=TEXT_COLOR, spaceAfter=8, alignment=TA_JUSTIFY)
style_en_bullet = ParagraphStyle("Bullet_EN", parent=style_en_body, leftIndent=20, bulletIndent=10, spaceAfter=4, alignment=TA_LEFT)
style_en_code = ParagraphStyle("Code_EN", parent=styles_en["Normal"], fontName="Courier", fontSize=9, leading=12, textColor=HexColor("#01696F"), backColor=HexColor("#f0f0f0"), spaceAfter=6, alignment=TA_LEFT)
style_en_note = ParagraphStyle("Note_EN", parent=style_en_body, fontSize=9, textColor=TEXT_MUTED, leftIndent=16, spaceAfter=8)
style_en_footer = ParagraphStyle("Footer_EN", parent=styles_en["Normal"], fontName="Inter", fontSize=8, leading=10, textColor=TEXT_MUTED, alignment=TA_CENTER)

# ===== BENGALI STYLES =====
style_bn_title = ParagraphStyle("Title_BN", parent=styles_en["Title"], fontName="NotoBengali-Bold", fontSize=24, leading=32, textColor=PRIMARY, spaceAfter=6, alignment=TA_LEFT)
style_bn_subtitle = ParagraphStyle("Subtitle_BN", parent=styles_en["Normal"], fontName="NotoBengali", fontSize=12, leading=18, textColor=TEXT_MUTED, spaceAfter=20, alignment=TA_LEFT)
style_bn_h1 = ParagraphStyle("H1_BN", parent=styles_en["Heading1"], fontName="NotoBengali-Bold", fontSize=16, leading=24, textColor=PRIMARY, spaceBefore=24, spaceAfter=10, alignment=TA_LEFT)
style_bn_h2 = ParagraphStyle("H2_BN", parent=styles_en["Heading2"], fontName="NotoBengali-Bold", fontSize=13, leading=20, textColor=HexColor("#28251D"), spaceBefore=16, spaceAfter=8, alignment=TA_LEFT)
style_bn_body = ParagraphStyle("Body_BN", parent=styles_en["Normal"], fontName="NotoBengali", fontSize=10, leading=16, textColor=TEXT_COLOR, spaceAfter=8, alignment=TA_JUSTIFY)
style_bn_bullet = ParagraphStyle("Bullet_BN", parent=style_bn_body, leftIndent=20, bulletIndent=10, spaceAfter=4, alignment=TA_LEFT)
style_bn_note = ParagraphStyle("Note_BN", parent=style_bn_body, fontSize=9, textColor=TEXT_MUTED, leftIndent=16, spaceAfter=8)
style_bn_footer = ParagraphStyle("Footer_BN", parent=styles_en["Normal"], fontName="NotoBengali", fontSize=8, leading=12, textColor=TEXT_MUTED, alignment=TA_CENTER)

def make_bullet_list(items, style):
    """Create a bullet list from items."""
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=10, value="•") for item in items],
        bulletType="bullet",
        bulletColor=PRIMARY,
        leftIndent=20,
    )

def make_table(data, col_widths, header_bg=PRIMARY, is_bn=False):
    """Create a styled table."""
    t = Table(data, colWidths=col_widths)
    header_font = "NotoBengali-Bold" if is_bn else "Inter-Bold"
    body_font = "NotoBengali" if is_bn else "Inter"
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTNAME", (0, 0), (-1, 0), header_font),
        ("FONTNAME", (0, 1), (-1, -1), body_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), SURFACE_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t

def header_footer(canvas_obj, doc, title_text, is_bn=False):
    """Draw header and footer on each page."""
    canvas_obj.saveState()
    w, h = A4
    
    # Header bar
    canvas_obj.setFillColor(DARK_BG)
    canvas_obj.rect(0, h - 40, w, 40, fill=1, stroke=0)
    
    # Header text
    font = "NotoBengali-Bold" if is_bn else "Inter-Bold"
    canvas_obj.setFillColor(PRIMARY)
    canvas_obj.setFont(font, 10)
    canvas_obj.drawString(40, h - 26, "SENTINEL-X")
    canvas_obj.setFillColor(HexColor("#c8d4e0"))
    canvas_obj.setFont(font, 8)
    canvas_obj.drawRightString(w - 40, h - 26, title_text)
    
    # Footer
    canvas_obj.setFillColor(TEXT_MUTED)
    canvas_obj.setFont("Inter" if not is_bn else "NotoBengali", 8)
    canvas_obj.drawString(40, 20, f"Page {doc.page}")
    canvas_obj.drawRightString(w - 40, 20, "Sentinel-X — Multi-Domain Decision Trainer")
    canvas_obj.setStrokeColor(BORDER)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(40, 30, w - 40, 30)
    
    canvas_obj.restoreState()

def header_footer_en(canvas_obj, doc):
    header_footer(canvas_obj, doc, "User Manual", is_bn=False)

def header_footer_bn(canvas_obj, doc):
    header_footer(canvas_obj, doc, "ব্যবহারকারী ম্যানুয়াল", is_bn=True)


# ===================================================================
# ENGLISH USER MANUAL
# ===================================================================
def build_english_manual():
    doc = SimpleDocTemplate(
        "/home/user/workspace/sentinel-x/Sentinel-X-User-Manual-EN.pdf",
        pagesize=A4,
        title="Sentinel-X User Manual",
        author="Perplexity Computer",
        leftMargin=40, rightMargin=40, topMargin=60, bottomMargin=40,
    )
    
    s = []  # story
    
    # === COVER ===
    s.append(Spacer(1, 60))
    s.append(Paragraph("SENTINEL-X", style_en_title))
    s.append(Paragraph("Multi-Domain Decision Trainer for Degraded Communication Environments", style_en_subtitle))
    s.append(Spacer(1, 20))
    s.append(Paragraph("USER MANUAL", ParagraphStyle("CoverLabel_EN", parent=style_en_body, fontName="Inter-Bold", fontSize=14, textColor=PRIMARY, alignment=TA_CENTER)))
    s.append(Spacer(1, 6))
    s.append(Paragraph("Version 5.0 | Fullstack Edition", ParagraphStyle("CoverVersion_EN", parent=style_en_body, fontName="Inter", fontSize=11, textColor=TEXT_MUTED, alignment=TA_CENTER)))
    s.append(PageBreak())
    
    # === TABLE OF CONTENTS ===
    s.append(Paragraph("Table of Contents", style_en_h1))
    toc_data = [
        ["Section", "Title", "Page"],
        ["1", "System Overview", "3"],
        ["2", "Getting Started — Registration & Login", "4"],
        ["3", "Command Lobby", "5"],
        ["4", "Instructor Role — Creating & Controlling Exercises", "6"],
        ["5", "Trainee Roles — Joining & Participating", "8"],
        ["6", "Tactical Map & Intel Feed", "9"],
        ["7", "Decision Submission & Confidence Slider", "10"],
        ["8", "Scenario Configuration", "11"],
        ["9", "Injecting Communication Degradation", "12"],
        ["10", "Red-Team Inject Console", "13"],
        ["11", "Cascade Detection", "14"],
        ["12", "After-Action Review (AAR) & Export", "15"],
        ["13", "Real-Time Multiplayer (Socket.IO)", "16"],
        ["14", "Troubleshooting", "17"],
    ]
    s.append(make_table(toc_data, [50, 320, 60]))
    s.append(PageBreak())
    
    # === 1. SYSTEM OVERVIEW ===
    s.append(Paragraph("1. System Overview", style_en_h1))
    s.append(Paragraph(
        "Sentinel-X is a fullstack web-based decision-making training platform designed for military and "
        "defense environments where communication is degraded, delayed, or contradictory. Unlike traditional "
        "training formats (TEWT, CPX) that assume complete information flow, Sentinel-X deliberately injects "
        "incomplete, delayed, or contradictory intelligence feeds — training decision-making under uncertainty "
        "rather than under ideal conditions.", style_en_body))
    s.append(Paragraph("Key Features", style_en_h2))
    s.append(make_bullet_list([
        "User registration and authentication with password hashing (crypto.scryptSync)",
        "Real-time multiplayer via Socket.IO — multiple users join the same exercise from different devices",
        "Scenario engine with configurable communication degradation (delay, blackout, packet loss)",
        "Conflicting intelligence injection (air, cyber, land reports with divergent reliability scores)",
        "Red-team inject console (false flag operations, info overload, weather degrade, new threats)",
        "Decision confidence slider — trainees self-report confidence with each decision",
        "What Did You Know at the Time? — intel snapshot captured with every decision submission",
        "Cascade detection — system auto-detects self-reinforcing degradation cycles",
        "Automated After-Action Review (AAR) with data-driven scoring",
        "AAR export as downloadable HTML and JSON files",
        "Role-based asymmetric information — each role sees different intel feeds",
        "SQLite database persistence — all users, exercises, decisions, and AARs stored server-side",
    ], style_en_bullet))
    s.append(Spacer(1, 10))
    
    # Architecture table
    s.append(Paragraph("System Architecture", style_en_h2))
    arch_data = [
        ["Layer", "Technology"],
        ["Frontend", "HTML5 + CSS3 + JavaScript (Vanilla)"],
        ["Backend", "Node.js + Express.js"],
        ["Real-time", "Socket.IO"],
        ["Database", "SQLite (better-sqlite3)"],
        ["Authentication", "Session-based (X-Visitor-Id, crypto.scryptSync)"],
        ["Deployment", "Express static + port proxy"],
    ]
    s.append(make_table(arch_data, [150, 280]))
    s.append(PageBreak())
    
    # === 2. GETTING STARTED ===
    s.append(Paragraph("2. Getting Started — Registration & Login", style_en_h1))
    s.append(Paragraph("Step 1: Open the Platform", style_en_h2))
    s.append(Paragraph(
        "Open the Sentinel-X URL in your web browser. You will see the landing page with an overview of "
        "the system, innovations, research backing, and roadmap. Click the <b>Enter Platform</b> button "
        "in the top right corner to access the authentication page.", style_en_body))
    
    s.append(Paragraph("Step 2: Register a New Account", style_en_h2))
    s.append(Paragraph(
        "If you are a new user, click the <b>Register</b> link on the login page. Fill in the following:", style_en_body))
    s.append(make_bullet_list([
        "<b>Username</b>: Choose a unique username (minimum 3 characters)",
        "<b>Password</b>: Choose a secure password (minimum 4 characters)",
        "<b>Role</b>: Select either Trainee or Instructor",
    ], style_en_bullet))
    s.append(Paragraph(
        "After successful registration, you will be redirected to the login page with your username pre-filled. "
        "Your password is securely hashed using crypto.scryptSync before storage — it is never stored in plaintext.", style_en_body))
    
    s.append(Paragraph("Step 3: Login", style_en_h2))
    s.append(Paragraph(
        "Enter your username and password on the login page and click <b>Sign In</b>. Upon successful "
        "authentication, you will be taken to the Command Lobby.", style_en_body))
    s.append(PageBreak())
    
    # === 3. COMMAND LOBBY ===
    s.append(Paragraph("3. Command Lobby", style_en_h1))
    s.append(Paragraph(
        "The Command Lobby is your home base after login. It displays your username and role at the top, "
        "and provides three main sections:", style_en_body))
    s.append(Paragraph("Create New Exercise", style_en_h2))
    s.append(Paragraph(
        "Enter an exercise name (e.g., OP DEEP FOG) and click <b>Create & Enter as Instructor</b>. "
        "The system generates a unique exercise code (e.g., MS3249) and you enter the simulator as the "
        "instructor with full control permissions.", style_en_body))
    s.append(Paragraph("Join Existing Exercise", style_en_h2))
    s.append(Paragraph(
        "Enter the exercise code provided by your instructor, select your role (Commander Alpha, "
        "Cyber/EW Officer, Air Liaison, or Intel Analyst), and click <b>Join Exercise</b>. "
        "You will be connected to the exercise via Socket.IO and see real-time updates.", style_en_body))
    s.append(Paragraph("Your Exercises", style_en_h2))
    s.append(Paragraph(
        "This section lists all exercises you have created or joined, showing their status (created, "
        "active, ended) and your role in each.", style_en_body))
    s.append(PageBreak())
    
    # === 4. INSTRUCTOR ROLE ===
    s.append(Paragraph("4. Instructor Role — Creating & Controlling Exercises", style_en_h1))
    s.append(Paragraph(
        "As an instructor, you have full control over the exercise. The instructor-only panels are "
        "visible in the left sidebar and include:", style_en_body))
    
    s.append(Paragraph("Exercise Control", style_en_h2))
    s.append(make_bullet_list([
        "<b>Start</b>: Initializes the exercise, resets all state, starts the clock, and notifies all connected participants via Socket.IO",
        "<b>Pause</b>: Temporarily halts the exercise clock and event processing",
        "<b>End</b>: Terminates the exercise, generates the AAR, and broadcasts it to all participants",
    ], style_en_bullet))
    
    s.append(Paragraph("Scenario Configuration", style_en_h2))
    s.append(make_bullet_list([
        "<b>Tempo</b>: Controls event frequency — Slow (30s), Normal (15s), or Fast (8s) between automated events",
        "<b>Info Loss %</b>: Sets the baseline information loss percentage (0-60%) that affects reliability scores",
        "<b>Domains</b>: Toggle which operational domains are active — Land, Air, Cyber, EW",
    ], style_en_bullet))
    s.append(PageBreak())
    
    # === 5. TRAINEE ROLES ===
    s.append(Paragraph("5. Trainee Roles — Joining & Participating", style_en_h1))
    s.append(Paragraph(
        "Trainees join an exercise using the exercise code provided by the instructor. Each role receives "
        "different (asymmetric) information, forcing team coordination:", style_en_body))
    
    role_data = [
        ["Role", "Information Access", "Primary Function"],
        ["Commander Alpha", "Full map, all sources", "Mission command, final decisions"],
        ["Cyber/EW Officer", "Spectrum data, EW/Cyber alerts", "Electronic warfare, cyber defense"],
        ["Air Liaison", "Air corridor data, air reports", "Air asset management, airspace"],
        ["Intel Analyst", "All sources, reliability matrix", "Source assessment, threat analysis"],
    ]
    s.append(make_table(role_data, [110, 180, 150]))
    s.append(Spacer(1, 10))
    s.append(Paragraph(
        "Each role sees a filtered intel feed based on their access level. The Commander sees the full "
        "picture, while specialized roles see only their domain. This forces communication and coordination "
        "under degraded conditions.", style_en_body))
    s.append(PageBreak())
    
    # === 6. TACTICAL MAP & INTEL FEED ===
    s.append(Paragraph("6. Tactical Map & Intel Feed", style_en_h1))
    s.append(Paragraph("Tactical Map", style_en_h2))
    s.append(Paragraph(
        "The central panel displays a tactical grid map of Sector Golf-7 with coordinate labels "
        "(A-J horizontally, 1-5 vertically). The map shows:", style_en_body))
    s.append(make_bullet_list([
        "<b>Friendly units</b> (green circles): ALPHA, BRAVO, AIR-1",
        "<b>Hostile units</b> (red circles): HOSTILE",
        "<b>Unknown units</b> (yellow circles): UNKNOWN, UNCONFIRMED",
        "<b>Communication links</b>: Lines between units — green (normal), amber (delayed), red (blackout)",
        "<b>Objective zones</b>: Dashed rectangles for OBJ ALPHA and ENEMY ZONE",
        "<b>Map badges</b>: Real-time status indicators (LATENCY, SIGNAL LOST, PACKET LOSS, FALSE FLAG)",
        "<b>Conditions bar</b>: Shows NOMINAL or degraded conditions (COMMS DEGRADED, WEATHER, ACTIVE THREATS)",
    ], style_en_bullet))
    
    s.append(Paragraph("Intelligence Feed", style_en_h2))
    s.append(Paragraph(
        "The right panel shows incoming intelligence entries in reverse chronological order. Each entry "
        "displays the timestamp, message, source, and reliability score (HIGH/MEDIUM/LOW). Entries are "
        "color-coded by type: normal (green border), warning (amber), critical (red), conflict (cyan).", style_en_body))
    s.append(PageBreak())
    
    # === 7. DECISION SUBMISSION ===
    s.append(Paragraph("7. Decision Submission & Confidence Slider", style_en_h1))
    s.append(Paragraph(
        "When the exercise is active, the decision panel at the bottom right becomes available. "
        "The trainee selects a course of action, sets their confidence level, and provides a written rationale.", style_en_body))
    
    s.append(Paragraph("Available Decisions", style_en_h2))
    dec_data = [
        ["Decision", "Effect on Map"],
        ["Engage Hostile", "Attack vectors drawn, units move to engage"],
        ["Deploy Recon", "Recon path drawn, unit moves to investigate"],
        ["Fortify Position", "Defensive perimeters appear around friendly units"],
        ["Tactical Withdrawal", "Retreat paths drawn, units reposition to secondary waypoints"],
    ]
    s.append(make_table(dec_data, [140, 290]))
    s.append(Spacer(1, 10))
    
    s.append(Paragraph("Confidence Slider", style_en_h2))
    s.append(Paragraph(
        "After selecting a decision, a confidence slider appears (0-100%). The trainee self-reports their "
        "confidence level. The system tracks how confidence aligns with information quality — detecting "
        "overconfidence (high confidence with limited intel) and hesitation (low confidence with ample intel).", style_en_body))
    s.append(Paragraph(
        "An intel snapshot is automatically captured at the moment of decision submission, recording "
        "exactly what information was available — this supports the What Did You Know at the Time? evaluation "
        "in the AAR.", style_en_body))
    s.append(PageBreak())
    
    # === 8. SCENARIO CONFIGURATION ===
    s.append(Paragraph("8. Scenario Configuration", style_en_h1))
    s.append(Paragraph(
        "Instructors can configure the scenario before or during an exercise using the Scenario "
        "Configuration panel:", style_en_body))
    config_data = [
        ["Setting", "Options", "Description"],
        ["Tempo", "Slow / Normal / Fast", "Controls time between automated intel events"],
        ["Info Loss %", "0% - 60%", "Baseline information degradation affecting reliability"],
        ["Land Domain", "On / Off", "Enables land-based intel and units"],
        ["Air Domain", "On / Off", "Enables air corridor and air reports"],
        ["Cyber Domain", "On / Off", "Enables cyber alerts and EW spectrum data"],
        ["EW Domain", "On / Off", "Enables electronic warfare jamming effects"],
    ]
    s.append(make_table(config_data, [90, 110, 230]))
    s.append(PageBreak())
    
    # === 9. COMMUNICATION DEGRADATION ===
    s.append(Paragraph("9. Injecting Communication Degradation", style_en_h1))
    s.append(Paragraph(
        "The instructor can inject three types of communication degradation at any time during an "
        "active exercise. All connected trainees see the effects in real-time via Socket.IO.", style_en_body))
    deg_data = [
        ["Type", "Visual Effect", "Duration", "Description"],
        ["Comms Delay", "Links turn amber, dashed", "~8s", "3-5 second latency on all feeds"],
        ["Signal Blackout", "Links disappear, NO SIGNAL", "~10s", "Complete communication loss"],
        ["Packet Loss", "Links flicker, 30% drops", "~6s", "Intermittent data loss on channels"],
    ]
    s.append(make_table(deg_data, [80, 120, 50, 170]))
    s.append(Spacer(1, 10))
    s.append(Paragraph(
        "Degradation automatically recovers after the duration expires, and a COMMS RESTORED message "
        "is injected into the intel feed.", style_en_body))
    s.append(PageBreak())
    
    # === 10. RED-TEAM CONSOLE ===
    s.append(Paragraph("10. Red-Team Inject Console", style_en_h1))
    s.append(Paragraph(
        "The Red-Team Inject Console provides advanced scenario control for creating realistic "
        "deception and overload scenarios:", style_en_body))
    rt_data = [
        ["Inject", "Effect"],
        ["Weather Degrade", "Fog overlay on tactical map, sensor effectiveness reduced"],
        ["New Threat", "New hostile unit appears on map at a new position"],
        ["False Flag Op", "Friendly units temporarily appear as hostile — spoofing detected"],
        ["Info Overload", "5 simultaneous intel feeds injected — cognitive load critical, triggers cascade"],
    ]
    s.append(make_table(rt_data, [120, 310]))
    s.append(Spacer(1, 10))
    s.append(Paragraph(
        "The False Flag inject automatically resolves after 12 seconds, restoring friend/foe identification. "
        "The Info Overload inject is the primary cascade trigger — when combined with comms degradation and "
        "conflicting intel, it can trigger a cascade warning.", style_en_body))
    s.append(PageBreak())
    
    # === 11. CASCADE DETECTION ===
    s.append(Paragraph("11. Cascade Detection", style_en_h1))
    s.append(Paragraph(
        "Based on research showing that a single erroneous decision can trigger a self-reinforcing cycle "
        "of cascading failures across the command structure, Sentinel-X automatically detects cascade conditions.", style_en_body))
    s.append(Paragraph("Cascade Trigger Conditions", style_en_h2))
    s.append(make_bullet_list([
        "2+ comms channels degraded AND 1+ conflicting intel present, OR",
        "8+ intel entries (overload) AND 1+ comms channel degraded",
    ], style_en_bullet))
    s.append(Paragraph(
        "When a cascade is detected, a CASCADE WARNING is injected into the intel feed, and the cascade "
        "is recorded in the Cascade Detection panel for the AAR. The research basis is from Hubbard, Kott, "
        "and Martin (arXiv:1607.08139) on self-reinforcing degradation in decision-making teams.", style_en_body))
    s.append(PageBreak())
    
    # === 12. AAR ===
    s.append(Paragraph("12. After-Action Review (AAR) & Export", style_en_h1))
    s.append(Paragraph(
        "When the instructor ends the exercise, an After-Action Review is automatically generated and "
        "displayed. The AAR includes:", style_en_body))
    s.append(make_bullet_list([
        "<b>Score Cards</b>: Decision Quality, Response Time, Info Utilization, Team Coordination (0-100 each, data-driven)",
        "<b>Decision Timeline</b>: Chronological view of all decisions, comms failures, and cascades",
        "<b>Cascade Analysis</b>: Details of any detected cascades with trigger descriptions",
        "<b>Communication Failures Log</b>: All injected degradation events with timestamps",
        "<b>Local AI Evaluation</b>: Overall rating (EXCELLENT/PROFICIENT/DEVELOPING/NEEDS RETRAINING) with findings",
        "<b>Areas for Improvement</b>: Personalized recommendations based on exercise performance",
        "<b>Intel Snapshots</b>: What Did You Know at the Time? — intel available at each decision point",
    ], style_en_bullet))
    
    s.append(Paragraph("Export Options", style_en_h2))
    export_data = [
        ["Format", "Content", "Use Case"],
        ["HTML", "Full formatted report with tables", "Printable, shareable document"],
        ["JSON", "Raw structured data", "Integration with other systems, programmatic analysis"],
    ]
    s.append(make_table(export_data, [80, 200, 150]))
    s.append(PageBreak())
    
    # === 13. MULTIPLAYER ===
    s.append(Paragraph("13. Real-Time Multiplayer (Socket.IO)", style_en_h1))
    s.append(Paragraph(
        "Sentinel-X supports real-time multiplayer via Socket.IO. Multiple users can join the same "
        "exercise from different browsers or devices, each in a different role.", style_en_body))
    s.append(Paragraph("How It Works", style_en_h2))
    s.append(make_bullet_list([
        "The instructor creates an exercise and receives a unique code",
        "Trainees join using the code and select their role",
        "All participants are connected to the same Socket.IO room",
        "When the instructor starts, pauses, injects, or ends the exercise, all participants see updates in real-time",
        "Decisions submitted by any trainee are broadcast to all participants",
        "Team status (which roles are active, degraded, or in decision mode) is synchronized",
    ], style_en_bullet))
    s.append(Paragraph(
        "Each role sees asymmetric information — the Cyber/EW officer sees spectrum data, the Air Liaison "
        "sees air corridors, the Intel Analyst sees all sources. This forces communication and coordination.", style_en_body))
    s.append(Paragraph("Verified Events", style_en_h2))
    events_data = [
        ["Event", "Direction", "Description"],
        ["exercise-started", "Server → All", "Exercise begins, full state broadcast"],
        ["state-update", "Server → All", "Complete state sync (intel, comms, map)"],
        ["inject", "Instructor → All", "Degradation or conflict injected"],
        ["decision-made", "Trainee → All", "A decision was submitted with confidence"],
        ["exercise-ended", "Instructor → All", "Exercise ends, AAR broadcast"],
        ["team-update", "Server → All", "Team role status changed"],
        ["tick", "Server → All", "Clock update every 5 seconds"],
    ]
    s.append(make_table(events_data, [110, 100, 220]))
    s.append(PageBreak())
    
    # === 14. TROUBLESHOOTING ===
    s.append(Paragraph("14. Troubleshooting", style_en_h1))
    trouble_data = [
        ["Problem", "Solution"],
        ["Cannot login", "Verify username and password. Register if you don't have an account."],
        ["Exercise not starting", "Only the instructor can start. Verify you created the exercise."],
        ["Inject button not working", "Exercise must be active. Click Start first."],
        ["Other users not seeing updates", "Verify Socket.IO is connected. Use separate browsers/devices."],
        ["Decision options not showing", "Exercise must be started. The trainee panel shows after Start."],
        ["AAR not generating", "Click End Exercise to trigger AAR generation."],
        ["Export not downloading", "Check browser popup blocker. Allow downloads from the site."],
        ["Comms delay links not changing", "Fixed in v5 — CSS class name corrected to comms-link-delay."],
        ["Team status stuck on STANDBY", "Exercise must be started. Status changes to ACTIVE on Start."],
    ]
    s.append(make_table(trouble_data, [160, 270]))
    s.append(Spacer(1, 20))
    s.append(Paragraph(
        "For additional support, refer to the research backing section on the landing page, which links "
        "to the academic papers that inform the system's design (arXiv:1607.08139, arXiv:2603.21280).", style_en_note))
    
    doc.build(s, onFirstPage=header_footer_en, onLaterPages=header_footer_en)
    print("English manual generated: Sentinel-X-User-Manual-EN.pdf")


# ===================================================================
# BENGALI USER MANUAL
# ===================================================================
def build_bengali_manual():
    doc = SimpleDocTemplate(
        "/home/user/workspace/sentinel-x/Sentinel-X-User-Manual-BN.pdf",
        pagesize=A4,
        title="Sentinel-X ব্যবহারকারী ম্যানুয়াল",
        author="Perplexity Computer",
        leftMargin=40, rightMargin=40, topMargin=60, bottomMargin=40,
    )
    
    s = []  # story
    
    # === COVER ===
    s.append(Spacer(1, 60))
    s.append(Paragraph("SENTINEL-X", style_bn_title))
    s.append(Paragraph("ডিগ্রেডেড কমিউনিকেশন পরিবেশের জন্য মাল্টি-ডোমেইন ডিসিশন ট্রেনার", style_bn_subtitle))
    s.append(Spacer(1, 20))
    s.append(Paragraph("ব্যবহারকারী ম্যানুয়াল", ParagraphStyle("CoverLabel_BN", parent=style_bn_body, fontName="NotoBengali-Bold", fontSize=14, textColor=PRIMARY, alignment=TA_CENTER)))
    s.append(Spacer(1, 6))
    s.append(Paragraph("সংস্করণ ৫.০ | ফুলস্ট্যাক এডিশন", ParagraphStyle("CoverVersion_BN", parent=style_bn_body, fontName="NotoBengali", fontSize=11, textColor=TEXT_MUTED, alignment=TA_CENTER)))
    s.append(PageBreak())
    
    # === TABLE OF CONTENTS ===
    s.append(Paragraph("সূচিপত্র", style_bn_h1))
    toc_data = [
        ["অধ্যায়", "শিরোনাম", "পৃষ্ঠা"],
        ["১", "সিস্টেম পরিচিতি", "৩"],
        ["২", "শুরু করা — রেজিস্ট্রেশন ও লগইন", "৪"],
        ["৩", "কমান্ড লবি", "৫"],
        ["৪", "ইনস্ট্রাক্টর রোল — এক্সারসাইজ তৈরি ও নিয়ন্ত্রণ", "৬"],
        ["৫", "ট্রেইনি রোল — যোগদান ও অংশগ্রহণ", "৮"],
        ["৬", "ট্যাক্টিক্যাল ম্যাপ ও ইন্টেল ফিড", "৯"],
        ["৭", "সিদ্ধান্ত জমা ও কনফিডেন্স স্লাইডার", "১০"],
        ["৮", "সিনারিও কনফিগারেশন", "১১"],
        ["৯", "কমিউনিকেশন ডিগ্রেডেশন ইনজেকশন", "১২"],
        ["১০", "রেড-টিম ইনজেক্ট কনসোল", "১৩"],
        ["১১", "ক্যাসকেড ডিটেকশন", "১৪"],
        ["১২", "আফটার-অ্যাকশন রিভিউ (AAR) ও এক্সপোর্ট", "১৫"],
        ["১৩", "রিয়েল-টাইম মাল্টিপ্লেয়ার (Socket.IO)", "১৬"],
        ["১৪", "সমস্যা সমাধান", "১৭"],
    ]
    s.append(make_table(toc_data, [50, 320, 60], is_bn=True))
    s.append(PageBreak())
    
    # === 1. SYSTEM OVERVIEW ===
    s.append(Paragraph("১. সিস্টেম পরিচিতি", style_bn_h1))
    s.append(Paragraph(
        "Sentinel-X একটি ফুলস্ট্যাক ওয়েব-ভিত্তিক সিদ্ধান্ত গ্রহণের প্রশিক্ষণ প্ল্যাটফর্ম, যা সামরিক "
        "এবং প্রতিরক্ষা পরিবেশের জন্য ডিজাইন করা হয়েছে যেখানে যোগাযোগ ব্যাহত, বিলম্বিত, বা "
        "পরস্পরবিরোধী। ঐতিহ্যবাহী প্রশিক্ষণ ফরম্যাট (TEWT, CPX) যেখানে সম্পূর্ণ তথ্যপ্রবাহ অনুমান করে, "
        "Sentinel-X সচেতনভাবে অসম্পূর্ণ, বিলম্বিত, বা পরস্পরবিরোধী গোয়েন্দা তথ্য ইনজেক্ট করে — "
        "আদর্শ অবস্থার পরিবর্তে অনিশ্চয়তার অধীনে সিদ্ধান্ত গ্রহণের প্রশিক্ষণ দেয়।", style_bn_body))
    s.append(Paragraph("মূল বৈশিষ্ট্য", style_bn_h2))
    s.append(make_bullet_list([
        "ইউজার রেজিস্ট্রেশন এবং অথেন্টিকেশন — পাসওয়ার্ড হ্যাশিং (crypto.scryptSync)",
        "Socket.IO এর মাধ্যমে রিয়েল-টাইম মাল্টিপ্লেয়ার — একই এক্সারসাইজে একাধিক ইউজার আলাদা ডিভাইস থেকে যোগ দিতে পারে",
        "সিনারিও ইঞ্জিন — কনফিগারেবল কমিউনিকেশন ডিগ্রেডেশন (delay, blackout, packet loss)",
        "পরস্পরবিরোধী গোয়েন্দা তথ্য ইনজেকশন (air, cyber, land — ভিন্ন নির্ভরযোগ্যতা স্কোর সহ)",
        "রেড-টিম ইনজেক্ট কনসোল — false flag অপারেশন, info overload, weather degrade, new threat",
        "ডিসিশন কনফিডেন্স স্লাইডার — ট্রেইনি প্রতিটি সিদ্ধান্তে নিজের আত্মবিশ্বাস স্তর সেট করে",
        "\"What Did You Know at the Time?\" — প্রতিটি সিদ্ধান্তের সময় ইন্টেল স্ন্যাপশট ক্যাপচার হয়",
        "ক্যাসকেড ডিটেকশন — সিস্টেম স্বয়ংক্রিয়ভাবে self-reinforcing ডিগ্রেডেশন সাইকেল শনাক্ত করে",
        "স্বয়ংক্রিয় আফটার-অ্যাকশন রিভিউ (AAR) — ডেটা-চালিত স্কোরিং সহ",
        "AAR এক্সপোর্ট — HTML এবং JSON ফাইল ডাউনলোড",
        "রোল-ভিত্তিক অসমমিত তথ্য — প্রতিটি রোল আলাদা ইন্টেল ফিড দেখে",
        "SQLite ডেটাবেস পারসিস্টেন্স — সকল ইউজার, এক্সারসাইজ, সিদ্ধান্ত এবং AAR সার্ভারে সংরক্ষিত",
    ], style_bn_bullet))
    s.append(PageBreak())
    
    # === 2. GETTING STARTED ===
    s.append(Paragraph("২. শুরু করা — রেজিস্ট্রেশন ও লগইন", style_bn_h1))
    s.append(Paragraph("ধাপ ১: প্ল্যাটফর্ম খুলুন", style_bn_h2))
    s.append(Paragraph(
        "আপনার ওয়েব ব্রাউজারে Sentinel-X URL খুলুন। আপনি ল্যান্ডিং পেজ দেখতে পাবেন যেখানে "
        "সিস্টেমের ওভারভিউ, ইনোভেশন, রিসার্চ এবং রোডম্যাপ রয়েছে। উপরে ডানদিকে <b>Enter Platform</b> "
        "বোতামে ক্লিক করুন।", style_bn_body))
    
    s.append(Paragraph("ধাপ ২: নতুন অ্যাকাউন্ট রেজিস্টার করুন", style_bn_h2))
    s.append(Paragraph(
        "আপনি যদি নতুন ইউজার হন, লগইন পেজে <b>Register</b> লিঙ্কে ক্লিক করুন। নিচের তথ্য পূরণ করুন:", style_bn_body))
    s.append(make_bullet_list([
        "<b>Username</b>: একটি ইউনিক ইউজারনেম বেছে নিন (ন্যূনতম ৩ অক্ষর)",
        "<b>Password</b>: একটি নিরাপদ পাসওয়ার্ড বেছে নিন (ন্যূনতম ৪ অক্ষর)",
        "<b>Role</b>: Trainee বা Instructor নির্বাচন করুন",
    ], style_bn_bullet))
    s.append(Paragraph(
        "সফল রেজিস্ট্রেশনের পর, আপনি লগইন পেজে রিডাইরেক্ট হবেন। আপনার পাসওয়ার্ড crypto.scryptSync "
        "দিয়ে নিরাপদে হ্যাশ করা হয় — এটি কখনোই প্লেইনটেক্সটে সংরক্ষিত হয় না।", style_bn_body))
    
    s.append(Paragraph("ধাপ ৩: লগইন", style_bn_h2))
    s.append(Paragraph(
        "লগইন পেজে আপনার ইউজারনেম এবং পাসওয়ার্ড লিখে <b>Sign In</b> বোতামে ক্লিক করুন। সফল "
        "অথেন্টিকেশনের পর আপনি কমান্ড লবিতে নিয়ে যাওয়া হবেন।", style_bn_body))
    s.append(PageBreak())
    
    # === 3. COMMAND LOBBY ===
    s.append(Paragraph("৩. কমান্ড লবি", style_bn_h1))
    s.append(Paragraph(
        "কমান্ড লবি হল লগইনের পর আপনার মূল পেজ। এটি উপরে আপনার ইউজারনেম এবং রোল প্রদর্শন করে এবং "
        "তিনটি প্রধান বিভাগ প্রদান করে:", style_bn_body))
    s.append(Paragraph("নতুন এক্সারসাইজ তৈরি করুন", style_bn_h2))
    s.append(Paragraph(
        "একটি এক্সারসাইজ নাম লিখুন (যেমন OP DEEP FOG) এবং <b>Create & Enter as Instructor</b> বোতামে "
        "ক্লিক করুন। সিস্টেম একটি ইউনিক এক্সারসাইজ কোড তৈরি করে এবং আপনি ইনস্ট্রাক্টর হিসেবে "
        "সিমুলেটরে প্রবেশ করেন।", style_bn_body))
    s.append(Paragraph("বিদ্যমান এক্সারসাইজে যোগ দিন", style_bn_h2))
    s.append(Paragraph(
        "আপনার ইনস্ট্রাক্টর দ্বারা প্রদত্ত এক্সারসাইজ কোড লিখুন, আপনার রোল নির্বাচন করুন "
        "(Commander Alpha, Cyber/EW Officer, Air Liaison, বা Intel Analyst) এবং <b>Join Exercise</b> "
        "বোতামে ক্লিক করুন। আপনি Socket.IO এর মাধ্যমে এক্সারসাইজে সংযুক্ত হবেন।", style_bn_body))
    s.append(Paragraph("আপনার এক্সারসাইজ", style_bn_h2))
    s.append(Paragraph(
        "এই বিভাগে আপনার তৈরি বা যোগ দেওয়া সকল এক্সারসাইজের তালিকা থাকে — সেগুলোর স্ট্যাটাস "
        "(created, active, ended) এবং আপনার রোল সহ।", style_bn_body))
    s.append(PageBreak())
    
    # === 4. INSTRUCTOR ROLE ===
    s.append(Paragraph("৪. ইনস্ট্রাক্টর রোল — এক্সারসাইজ তৈরি ও নিয়ন্ত্রণ", style_bn_h1))
    s.append(Paragraph(
        "ইনস্ট্রাক্টর হিসেবে আপনার এক্সারসাইজের উপর সম্পূর্ণ নিয়ন্ত্রণ আছে। ইনস্ট্রাক্টর-অনলি প্যানেলগুলি "
        "বাম সাইডবারে প্রদর্শিত হয়:", style_bn_body))
    
    s.append(Paragraph("এক্সারসাইজ নিয়ন্ত্রণ", style_bn_h2))
    s.append(make_bullet_list([
        "<b>Start</b>: এক্সারসাইজ শুরু করে, সমস্ত স্টেট রিসেট করে, ঘড়ি চালু করে এবং Socket.IO এর মাধ্যমে সমস্ত সংযুক্ত অংশগ্রহণকারীদের জানায়",
        "<b>Pause</b>: সাময়িকভাবে এক্সারসাইজ ঘড়ি এবং ইভেন্ট প্রসেসিং বন্ধ করে",
        "<b>End</b>: এক্সারসাইজ শেষ করে, AAR তৈরি করে এবং সমস্ত অংশগ্রহণকারীদের কাছে পাঠায়",
    ], style_bn_bullet))
    
    s.append(Paragraph("সিনারিও কনফিগারেশন", style_bn_h2))
    s.append(make_bullet_list([
        "<b>Tempo</b>: ইভেন্ট ফ্রিকোয়েন্সি নিয়ন্ত্রণ — Slow (৩০সে), Normal (১৫সে), বা Fast (৮সে)",
        "<b>Info Loss %</b>: বেসলাইন তথ্য হ্রাস শতাংশ (০-৬০%) যা নির্ভরযোগ্যতা স্কোরকে প্রভাবিত করে",
        "<b>Domains</b>: কোন অপারেশনাল ডোমেইন সক্রিয় তা টগল করুন — Land, Air, Cyber, EW",
    ], style_bn_bullet))
    s.append(PageBreak())
    
    # === 5. TRAINEE ROLES ===
    s.append(Paragraph("৫. ট্রেইনি রোল — যোগদান ও অংশগ্রহণ", style_bn_h1))
    s.append(Paragraph(
        "ট্রেইনিরা ইনস্ট্রাক্টর দ্বারা প্রদত্ত এক্সারসাইজ কোড ব্যবহার করে যোগ দেয়। প্রতিটি রোল ভিন্ন "
        "(অসমমিত) তথ্য গ্রহণ করে, যা টিম কোঅর্ডিনেশনে বাধ্য করে:", style_bn_body))
    
    role_data = [
        ["রোল", "তথ্য অ্যাক্সেস", "প্রাথমিক কার্য"],
        ["Commander Alpha", "সম্পূর্ণ ম্যাপ, সকল উৎস", "মিশন কমান্ড, চূড়ান্ত সিদ্ধান্ত"],
        ["Cyber/EW Officer", "স্পেকট্রাম ডেটা, EW/Cyber অ্যালার্ট", "ইলেকট্রনিক ওয়ারফেয়ার, সাইবার ডিফেন্স"],
        ["Air Liaison", "এয়ার করিডর ডেটা, এয়ার রিপোর্ট", "এয়ার অ্যাসেট ম্যানেজমেন্ট"],
        ["Intel Analyst", "সকল উৎস, নির্ভরযোগ্যতা ম্যাট্রিক্স", "উৎস মূল্যায়ন, হুমকি বিশ্লেষণ"],
    ]
    s.append(make_table(role_data, [110, 180, 150], is_bn=True))
    s.append(Spacer(1, 10))
    s.append(Paragraph(
        "প্রতিটি রোল তাদের অ্যাক্সেস লেভেলের উপর ভিত্তি করে ফিল্টার করা ইন্টেল ফিড দেখে। Commander সম্পূর্ণ "
        "চিত্র দেখে, যখন বিশেষায়িত রোল শুধু তাদের ডোমেইন দেখে। এটি ডিগ্রেডেড অবস্থায় যোগাযোগ এবং "
        "সমন্বয়ে বাধ্য করে।", style_bn_body))
    s.append(PageBreak())
    
    # === 6. TACTICAL MAP & INTEL FEED ===
    s.append(Paragraph("৬. ট্যাক্টিক্যাল ম্যাপ ও ইন্টেল ফিড", style_bn_h1))
    s.append(Paragraph("ট্যাক্টিক্যাল ম্যাপ", style_bn_h2))
    s.append(Paragraph(
        "কেন্দ্রীয় প্যানেলে Sector Golf-7 এর একটি ট্যাক্টিক্যাল গ্রিড ম্যাপ প্রদর্শিত হয় কোঅর্ডিনেট "
        "লেবেল সহ (A-J অনুভূমিকভাবে, 1-5 উল্লম্বভাবে)। ম্যাপে দেখা যায়:", style_bn_body))
    s.append(make_bullet_list([
        "<b>বন্ধুত্বপূর্ণ ইউনিট</b> (সবুজ বৃত্ত): ALPHA, BRAVO, AIR-1",
        "<b>শত্রু ইউনিট</b> (লাল বৃত্ত): HOSTILE",
        "<b>অজানা ইউনিট</b> (হলুদ বৃত্ত): UNKNOWN, UNCONFIRMED",
        "<b>যোগাযোগ লিংক</b>: ইউনিটের মধ্যে লাইন — সবুজ (স্বাভাবিক), অ্যাম্বার (বিলম্বিত), লাল (ব্ল্যাকআউট)",
        "<b>অবজেক্টিভ জোন</b>: OBJ ALPHA এবং ENEMY ZONE এর জন্য ড্যাশড আয়তক্ষেত্র",
        "<b>ম্যাপ ব্যাজ</b>: রিয়েল-টাইম স্ট্যাটাস ইন্ডিকেটর (LATENCY, SIGNAL LOST, PACKET LOSS, FALSE FLAG)",
        "<b>কন্ডিশন বার</b>: NOMINAL বা ডিগ্রেডেড কন্ডিশন দেখায়",
    ], style_bn_bullet))
    
    s.append(Paragraph("ইন্টেলিজেন্স ফিড", style_bn_h2))
    s.append(Paragraph(
        "ডান প্যানেলে বিপরীত কালানুক্রমিক ক্রমে আসা গোয়েন্দা এন্ট্রি প্রদর্শিত হয়। প্রতিটি এন্ট্রিতে "
        "টাইমস্ট্যাম্প, বার্তা, উৎস এবং নির্ভরযোগ্যতা স্কোর (HIGH/MEDIUM/LOW) থাকে। এন্ট্রিগুলি "
        "টাইপ অনুসারে রঙ-কোডেড: normal (সবুজ), warning (অ্যাম্বার), critical (লাল), conflict (সায়ান)।", style_bn_body))
    s.append(PageBreak())
    
    # === 7. DECISION SUBMISSION ===
    s.append(Paragraph("৭. সিদ্ধান্ত জমা ও কনফিডেন্স স্লাইডার", style_bn_h1))
    s.append(Paragraph(
        "এক্সারসাইজ সক্রিয় থাকলে, নিচে ডানদিকে ডিসিশন প্যানেল উপলব্ধ হয়। ট্রেইনি একটি কোর্স অফ অ্যাকশন "
        "নির্বাচন করে, কনফিডেন্স লেভেল সেট করে এবং একটি লিখিত রেশনাল প্রদান করে।", style_bn_body))
    
    s.append(Paragraph("উপলব্ধ সিদ্ধান্ত", style_bn_h2))
    dec_data = [
        ["সিদ্ধান্ত", "ম্যাপে প্রভাব"],
        ["Engage Hostile", "অ্যাটাক ভেক্টর আঁকা হয়, ইউনিট শত্রুকে আক্রমণ করতে চলে"],
        ["Deploy Recon", "রেকন পথ আঁকা হয়, ইউনিট তদন্ত করতে চলে"],
        ["Fortify Position", "বন্ধুত্বপূর্ণ ইউনিটের চারপাশে প্রতিরক্ষামূলক পরিধি দেখা যায়"],
        ["Tactical Withdrawal", "পিছু হটার পথ আঁকা হয়, ইউনিট পুনঃঅবস্থান নেয়"],
    ]
    s.append(make_table(dec_data, [140, 290], is_bn=True))
    s.append(Spacer(1, 10))
    
    s.append(Paragraph("কনফিডেন্স স্লাইডার", style_bn_h2))
    s.append(Paragraph(
        "সিদ্ধান্ত নির্বাচনের পর একটি কনফিডেন্স স্লাইডার প্রদর্শিত হয় (০-১০০%)। ট্রেইনি নিজের "
        "আত্মবিশ্বাস স্তর সেট করে। সিস্টেম ট্র্যাক করে আত্মবিশ্বাস কীভাবে তথ্যের গুণমানের সাথে "
        "সঙ্গতিপূর্ণ — overconfidence (সীমিত ইন্টেলে উচ্চ আত্মবিশ্বাস) এবং hesitation "
        "(প্রচুর ইন্টেলে নিম্ন আত্মবিশ্বাস) শনাক্ত করে।", style_bn_body))
    s.append(Paragraph(
        "সিদ্ধান্ত জমার মুহূর্তে একটি ইন্টেল স্ন্যাপশট স্বয়ংক্রিয়ভাবে ক্যাপচার করা হয় — এটি AAR-এ "
        "\"What Did You Know at the Time?\" মূল্যায়নকে সমর্থন করে।", style_bn_body))
    s.append(PageBreak())
    
    # === 8. SCENARIO CONFIGURATION ===
    s.append(Paragraph("৮. সিনারিও কনফিগারেশন", style_bn_h1))
    s.append(Paragraph(
        "ইনস্ট্রাক্টররা এক্সারসাইজের আগে বা সময় সিনারিও কনফিগার করতে পারেন:", style_bn_body))
    config_data = [
        ["সেটিং", "অপশন", "বর্ণনা"],
        ["Tempo", "Slow / Normal / Fast", "স্বয়ংক্রিয় ইন্টেল ইভেন্টের মধ্যে সময় নিয়ন্ত্রণ"],
        ["Info Loss %", "০% - ৬০%", "নির্ভরযোগ্যতা প্রভাবিত করে এমন বেসলাইন তথ্য ডিগ্রেডেশন"],
        ["Land Domain", "On / Off", "ল্যান্ড-ভিত্তিক ইন্টেল এবং ইউনিট সক্রিয় করে"],
        ["Air Domain", "On / Off", "এয়ার করিডর এবং এয়ার রিপোর্ট সক্রিয় করে"],
        ["Cyber Domain", "On / Off", "সাইবার অ্যালার্ট এবং EW স্পেকট্রাম ডেটা সক্রিয় করে"],
        ["EW Domain", "On / Off", "ইলেকট্রনিক ওয়ারফেয়ার জ্যামিং প্রভাব সক্রিয় করে"],
    ]
    s.append(make_table(config_data, [90, 110, 230], is_bn=True))
    s.append(PageBreak())
    
    # === 9. COMMUNICATION DEGRADATION ===
    s.append(Paragraph("৯. কমিউনিকেশন ডিগ্রেডেশন ইনজেকশন", style_bn_h1))
    s.append(Paragraph(
        "ইনস্ট্রাক্টর সক্রিয় এক্সারসাইজের সময় যেকোনো সময় তিন ধরনের কমিউনিকেশন ডিগ্রেডেশন ইনজেক্ট "
        "করতে পারেন। সমস্ত সংযুক্ত ট্রেইনি Socket.IO এর মাধ্যমে রিয়েল-টাইমে প্রভাব দেখে।", style_bn_body))
    deg_data = [
        ["ধরন", "ভিজ্যুয়াল প্রভাব", "সময়", "বর্ণনা"],
        ["Comms Delay", "লিংক অ্যাম্বার, ড্যাশড", "~৮সে", "সকল ফিডে ৩-৫ সেকেন্ড লেটেন্সি"],
        ["Signal Blackout", "লিংক অদৃশ্য, NO SIGNAL", "~১০সে", "সম্পূর্ণ যোগাযোগ বিচ্ছিন্নতা"],
        ["Packet Loss", "লিংক ফ্লিকার, ৩০% ড্রপ", "~৬সে", "চ্যানেলে ব্যবধানে ডেটা লস"],
    ]
    s.append(make_table(deg_data, [80, 120, 50, 170], is_bn=True))
    s.append(Spacer(1, 10))
    s.append(Paragraph(
        "ডিগ্রেডেশন সময় শেষ হওয়ার পর স্বয়ংক্রিয়ভাবে পুনরুদ্ধার হয় এবং ইন্টেল ফিডে একটি "
        "COMMS RESTORED বার্তা ইনজেক্ট করা হয়।", style_bn_body))
    s.append(PageBreak())
    
    # === 10. RED-TEAM CONSOLE ===
    s.append(Paragraph("১০. রেড-টিম ইনজেক্ট কনসোল", style_bn_h1))
    s.append(Paragraph(
        "রেড-টিম ইনজেক্ট কনসোল বাস্তবসম্মত প্রতারণা এবং ওভারলোড সিনারিও তৈরির জন্য উন্নত "
        "সিনারিও নিয়ন্ত্রণ প্রদান করে:", style_bn_body))
    rt_data = [
        ["ইনজেক্ট", "প্রভাব"],
        ["Weather Degrade", "ম্যাপে কুয়াশার ওভারলে, সেন্সর কার্যকারিতা হ্রাস"],
        ["New Threat", "ম্যাপে নতুন অবস্থানে নতুন শত্রু ইউনিট আবির্ভূত"],
        ["False Flag Op", "বন্ধুত্বপূর্ণ ইউনিট সাময়িকভাবে শত্রু হিসেবে দেখা যায় — স্পুফিং শনাক্ত"],
        ["Info Overload", "৫টি একই সাথে ইন্টেল ফিড ইনজেক্ট — কগনিটিভ লোড ক্রিটিক্যাল, ক্যাসকেড ট্রিগার"],
    ]
    s.append(make_table(rt_data, [120, 310], is_bn=True))
    s.append(Spacer(1, 10))
    s.append(Paragraph(
        "False Flag ইনজেক্ট ১২ সেকেন্ড পর স্বয়ংক্রিয়ভাবে সমাধান হয়। Info Overload ইনজেক্ট হল "
        "প্রাথমিক ক্যাসকেড ট্রিগার — যখন কমিউনিকেশন ডিগ্রেডেশন এবং পরস্পরবিরোধী ইন্টেলের সাথে "
        "মিলিত হয়, এটি একটি ক্যাসকেড সতর্কতা ট্রিগার করতে পারে।", style_bn_body))
    s.append(PageBreak())
    
    # === 11. CASCADE DETECTION ===
    s.append(Paragraph("১১. ক্যাসকেড ডিটেকশন", style_bn_h1))
    s.append(Paragraph(
        "গবেষণা অনুসারে, একটি ভুল সিদ্ধান্ত সমগ্র কমান্ড স্ট্রাকচার জুড়ে self-reinforcing "
        "ক্যাসকেডিং ফেইলিওরের সাইকেল ট্রিগার করতে পারে। Sentinel-X স্বয়ংক্রিয়ভাবে "
        "ক্যাসকেড কন্ডিশন শনাক্ত করে।", style_bn_body))
    s.append(Paragraph("ক্যাসকেড ট্রিগার কন্ডিশন", style_bn_h2))
    s.append(make_bullet_list([
        "২+ কমিউনিকেশন চ্যানেল ডিগ্রেডেড এবং ১+ পরস্পরবিরোধী ইন্টেল উপস্থিত, অথবা",
        "৮+ ইন্টেল এন্ট্রি (ওভারলোড) এবং ১+ কমিউনিকেশন চ্যানেল ডিগ্রেডেড",
    ], style_bn_bullet))
    s.append(Paragraph(
        "ক্যাসকেড শনাক্ত হলে, একটি CASCADE WARNING ইন্টেল ফিডে ইনজেক্ট করা হয় এবং ক্যাসকেডটি "
        "AAR-এর জন্য Cascade Detection প্যানেলে রেকর্ড করা হয়। গবেষণার ভিত্তি Hubbard, Kott, "
        "এবং Martin (arXiv:1607.08139) থেকে নেওয়া।", style_bn_body))
    s.append(PageBreak())
    
    # === 12. AAR ===
    s.append(Paragraph("১২. আফটার-অ্যাকশন রিভিউ (AAR) ও এক্সপোর্ট", style_bn_h1))
    s.append(Paragraph(
        "ইনস্ট্রাক্টর এক্সারসাইজ শেষ করলে, একটি আফটার-অ্যাকশন রিভিউ স্বয়ংক্রিয়ভাবে তৈরি এবং "
        "প্রদর্শিত হয়। AAR-এ অন্তর্ভুক্ত:", style_bn_body))
    s.append(make_bullet_list([
        "<b>স্কোর কার্ড</b>: Decision Quality, Response Time, Info Utilization, Team Coordination (প্রতিটি ০-১০০, ডেটা-চালিত)",
        "<b>সিদ্ধান্ত টাইমলাইন</b>: সকল সিদ্ধান্ত, কমিউনিকেশন ফেইলিওর এবং ক্যাসকেডের কালানুক্রমিক ভিউ",
        "<b>ক্যাসকেড বিশ্লেষণ</b>: শনাক্ত করা ক্যাসকেডের বিস্তারিত ট্রিগার বর্ণনা সহ",
        "<b>কমিউনিকেশন ফেইলিওর লগ</b>: সকল ইনজেক্টেড ডিগ্রেডেশন ইভেন্ট টাইমস্ট্যাম্প সহ",
        "<b>লোকাল AI মূল্যায়ন</b>: সামগ্রিক রেটিং (EXCELLENT/PROFICIENT/DEVELOPING/NEEDS RETRAINING) ফাইন্ডিং সহ",
        "<b>উন্নতির ক্ষেত্র</b>: এক্সারসাইজ পারফরম্যান্সের উপর ভিত্তি করে ব্যক্তিগতকৃত সুপারিশ",
        "<b>ইন্টেল স্ন্যাপশট</b>: What Did You Know at the Time? — প্রতিটি সিদ্ধান্ত বিন্দুতে উপলব্ধ ইন্টেল",
    ], style_bn_bullet))
    
    s.append(Paragraph("এক্সপোর্ট অপশন", style_bn_h2))
    export_data = [
        ["ফরম্যাট", "কন্টেন্ট", "ব্যবহার"],
        ["HTML", "টেবিল সহ সম্পূর্ণ ফরম্যাটেড রিপোর্ট", "প্রিন্টযোগ্য, শেয়ারযোগ্য ডকুমেন্ট"],
        ["JSON", "কাঁচা স্ট্রাকচার্ড ডেটা", "অন্যান্য সিস্টেমের সাথে ইন্টিগ্রেশন"],
    ]
    s.append(make_table(export_data, [80, 200, 150], is_bn=True))
    s.append(PageBreak())
    
    # === 13. MULTIPLAYER ===
    s.append(Paragraph("১৩. রিয়েল-টাইম মাল্টিপ্লেয়ার (Socket.IO)", style_bn_h1))
    s.append(Paragraph(
        "Sentinel-X Socket.IO এর মাধ্যমে রিয়েল-টাইম মাল্টিপ্লেয়ার সমর্থন করে। একাধিক ইউজার "
        "আলাদা ব্রাউজার বা ডিভাইস থেকে একই এক্সারসাইজে যোগ দিতে পারে, প্রত্যেকে আলাদা রোলে।", style_bn_body))
    s.append(Paragraph("কীভাবে কাজ করে", style_bn_h2))
    s.append(make_bullet_list([
        "ইনস্ট্রাক্টর একটি এক্সারসাইজ তৈরি করেন এবং একটি ইউনিক কোড পান",
        "ট্রেইনিরা কোড ব্যবহার করে যোগ দেয় এবং তাদের রোল নির্বাচন করে",
        "সমস্ত অংশগ্রহণকারী একই Socket.IO রুমে সংযুক্ত হয়",
        "ইনস্ট্রাক্টর যখন start, pause, inject, বা end করেন, সমস্ত অংশগ্রহণকারী রিয়েল-টাইমে আপডেট দেখে",
        "যেকোনো ট্রেইনি দ্বারা জমা দেওয়া সিদ্ধান্ত সমস্ত অংশগ্রহণকারীদের কাছে ব্রডকাস্ট করা হয়",
        "টিম স্ট্যাটাস (কোন রোল active, degraded, বা decision mode-এ) সিঙ্ক্রোনাইজড",
    ], style_bn_bullet))
    s.append(Paragraph(
        "প্রতিটি রোল অসমমিত তথ্য দেখে — Cyber/EW অফিসার স্পেকট্রাম ডেটা দেখে, Air Liaison এয়ার "
        "করিডর দেখে, Intel Analyst সব উৎস দেখে। এটি যোগাযোগ এবং সমন্বয়ে বাধ্য করে।", style_bn_body))
    s.append(Paragraph("যাচাইকৃত ইভেন্ট", style_bn_h2))
    events_data = [
        ["ইভেন্ট", "দিক", "বর্ণনা"],
        ["exercise-started", "সার্ভার → সকল", "এক্সারসাইজ শুরু, সম্পূর্ণ স্টেট ব্রডকাস্ট"],
        ["state-update", "সার্ভার → সকল", "সম্পূর্ণ স্টেট সিঙ্ক (intel, comms, map)"],
        ["inject", "ইনস্ট্রাক্টর → সকল", "ডিগ্রেডেশন বা কনফ্লিক্ট ইনজেক্ট করা হয়েছে"],
        ["decision-made", "ট্রেইনি → সকল", "একটি সিদ্ধান্ত কনফিডেন্স সহ জমা দেওয়া হয়েছে"],
        ["exercise-ended", "ইনস্ট্রাক্টর → সকল", "এক্সারসাইজ শেষ, AAR ব্রডকাস্ট"],
        ["team-update", "সার্ভার → সকল", "টিম রোল স্ট্যাটাস পরিবর্তিত"],
        ["tick", "সার্ভার → সকল", "৫ সেকেন্ডে ঘড়ি আপডেট"],
    ]
    s.append(make_table(events_data, [110, 100, 220], is_bn=True))
    s.append(PageBreak())
    
    # === 14. TROUBLESHOOTING ===
    s.append(Paragraph("১৪. সমস্যা সমাধান", style_bn_h1))
    trouble_data = [
        ["সমস্যা", "সমাধান"],
        ["লগইন করতে পারছি না", "ইউজারনেম এবং পাসওয়ার্ড যাচাই করুন। অ্যাকাউন্ট না থাকলে রেজিস্টার করুন।"],
        ["এক্সারসাইজ শুরু হচ্ছে না", "শুধুমাত্র ইনস্ট্রাক্টর শুরু করতে পারে। আপনি এক্সারসাইজ তৈরি করেছেন কিনা যাচাই করুন।"],
        ["Inject বোতাম কাজ করছে না", "এক্সারসাইজ সক্রিয় থাকতে হবে। প্রথমে Start ক্লিক করুন।"],
        ["অন্য ইউজাররা আপডেট দেখছে না", "Socket.IO সংযুক্ত কিনা যাচাই করুন। আলাদা ব্রাউজার/ডিভাইস ব্যবহার করুন।"],
        ["সিদ্ধান্ত অপশন দেখা যাচ্ছে না", "এক্সারসাইজ শুরু হতে হবে। Start এর পরে ট্রেইনি প্যানেল দেখা যায়।"],
        ["AAR তৈরি হচ্ছে না", "AAR ট্রিগার করতে End Exercise ক্লিক করুন।"],
        ["এক্সপোর্ট ডাউনলোড হচ্ছে না", "ব্রাউজার পপআপ ব্লকার চেক করুন। সাইট থেকে ডাউনলোড অনুমোদন করুন।"],
        ["Team status STANDBY-এ আটকে আছে", "এক্সারসাইজ শুরু হতে হবে। Start এ স্ট্যাটাস ACTIVE হয়।"],
    ]
    s.append(make_table(trouble_data, [160, 270], is_bn=True))
    s.append(Spacer(1, 20))
    s.append(Paragraph(
        "অতিরিক্ত সহায়তার জন্য, ল্যান্ডিং পেজের রিসার্চ ব্যাকিং সেকশন দেখুন, যা সিস্টেমের "
        "ডিজাইনকে নির্দেশকারী একাডেমিক পেপারগুলির লিংক করে (arXiv:1607.08139, arXiv:2603.21280)।", style_bn_note))
    
    doc.build(s, onFirstPage=header_footer_bn, onLaterPages=header_footer_bn)
    print("Bengali manual generated: Sentinel-X-User-Manual-BN.pdf")


if __name__ == "__main__":
    build_english_manual()
    build_bengali_manual()
    print("\nBoth manuals generated successfully!")
