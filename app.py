import streamlit as st
import tempfile
import json
import os
import textwrap
from schema import AuditReport
from report import build_html

# Check query params for home navigation
if st.query_params.get("screen") == "home":
    st.session_state.current_screen = "home"
    st.session_state.report = None
    st.query_params.clear()
    st.rerun()

# Set page config
st.set_page_config(page_title="The Auditor", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if "current_screen" not in st.session_state:
    st.session_state.current_screen = "home"
if "report" not in st.session_state:
    st.session_state.report = None

# Helper to get severity color matching Stitch AI design
def get_severity_color(severity):
    colors = {
        "Critical": "#ef4444", # Red
        "High": "#f97316",     # Orange
        "Medium": "#eab308",   # Yellow/Gold
        "Low": "#22c55e"       # Green
    }
    return colors.get(severity, "#cbd5e1")

# Helper to render clean HTML without markdown paragraph wrapper bugs
def render_html(html_str):
    clean_html = textwrap.dedent(html_str)
    # Remove empty lines and leading/trailing whitespace per line to avoid markdown code-block triggers
    clean_html = "\n".join([line.strip() for line in clean_html.split("\n") if line.strip()])
    st.markdown(clean_html, unsafe_allow_html=True)

# Custom CSS matching Stitch AI's premium, state-of-the-art design
css_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Global overrides */
.stApp {
    background-color: #f8fafc;
    font-family: 'Outfit', sans-serif !important;
}

/* Hide default streamlit header/decorations */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stDecoration"] {display: none;}

/* Adjust block container padding for full width navbar and alignment */
[data-testid="stAppViewBlockContainer"], .main .block-container {
    padding-top: 100px !important;
    padding-left: 48px !important;
    padding-right: 48px !important;
    max-width: 100% !important;
}

/* Custom top navbar styling */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 14px 40px;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px;
    z-index: 1000;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.navbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.navbar-logo-link {
    text-decoration: none !important;
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
}
.navbar-logo-icon {
    background-color: #0b57d0;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
    font-family: 'Outfit', sans-serif;
}
.navbar-logo-text {
    font-size: 20px;
    font-weight: 700;
    color: #0f172a;
    transition: color 0.2s ease;
}
.navbar-logo-link:hover .navbar-logo-text {
    color: #0b57d0;
}
.navbar-right {
    display: flex;
    align-items: center;
    gap: 20px;
}
.navbar-doc-title {
    font-size: 14px;
    color: #475569;
    font-weight: 500;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-right: 180px; /* Leave space for absolute-positioned streamlit download button */
}
.navbar-pill {
    background-color: #f1f5f9;
    color: #475569;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 9999px;
}
.navbar-link {
    font-size: 14px;
    color: #64748b;
    text-decoration: none;
    font-weight: 500;
}

/* Home Screen Layout */
.home-container {
    max-width: 960px;
    margin: 40px auto 20px auto;
    text-align: center;
}
.home-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background-color: #e0f2fe;
    color: #0369a1;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 16px;
    border-radius: 9999px;
    margin-bottom: 28px;
}
.home-title {
    font-size: 44px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
    margin-bottom: 20px;
    letter-spacing: -0.8px;
}
.home-subtitle {
    font-size: 18px;
    color: #475569;
    max-width: 720px;
    margin: 0 auto 48px auto;
    line-height: 1.6;
}

/* Home Features Grid Layout */
.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin: 48px auto 0 auto;
    max-width: 900px;
}
.feature-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    text-align: left;
    box-shadow: 0 1px 3px rgba(0,0,0,0.01);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}
.feature-icon {
    font-size: 28px;
    background-color: #f0f4f9;
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 18px;
}
.feature-title {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 13.5px;
    color: #475569;
    line-height: 1.5;
}

.home-footer-features {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 64px;
    border-top: 1px solid #e2e8f0;
    padding-top: 32px;
}
.home-footer-feature {
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: 0.5px;
}

/* Uploader components */
.uploader-label {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 12px;
    margin-left: 4px;
}

/* Native Sidebar Styling integration */
[data-testid="stSidebar"] {
    background-color: #f0f4f9 !important;
    border-right: 1px solid #e2e8f0 !important;
    top: 70px !important;
    height: calc(100vh - 70px) !important;
    width: 280px !important;
}
[data-testid="stSidebarContent"] {
    background-color: #f0f4f9 !important;
}
[data-testid="stSidebarUserContent"] {
    padding-top: 24px !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
}
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Sidebar inner components */
.sidebar-profile {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 32px;
}
.sidebar-avatar {
    background-color: #0b57d0;
    color: white;
    font-weight: 700;
    font-size: 16px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.sidebar-profile-info {
    display: flex;
    flex-direction: column;
}
.sidebar-profile-name {
    font-size: 15px;
    font-weight: 600;
    color: #0f172a;
}
.sidebar-profile-title {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}
.sidebar-menu {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.sidebar-item {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14.5px;
    font-weight: 500;
    color: #475569;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: default;
    transition: all 0.2s ease;
}
.sidebar-item:hover {
    background-color: rgba(203, 213, 225, 0.4);
    color: #0f172a;
}
.sidebar-item.active {
    background-color: #cbd5e1;
    color: #0f172a;
    font-weight: 600;
}
.sidebar-footer-item {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14.5px;
    font-weight: 500;
    color: #475569;
    cursor: default;
    padding: 8px 12px;
    border-radius: 6px;
}

/* Dashboard Header */
.dashboard-header {
    margin-bottom: 24px;
}
.dashboard-title {
    font-size: 32px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 4px;
}
.dashboard-subtitle {
    font-size: 16px;
    color: #64748b;
}

/* Executive Summary styling */
.summary-card {
    background: linear-gradient(135deg, #0f2b6b 0%, #0b57d0 100%);
    border-radius: 16px;
    padding: 24px;
    color: #ffffff;
    margin-bottom: 32px;
    box-shadow: 0 4px 15px rgba(11, 87, 208, 0.15);
}
.summary-title {
    font-size: 15px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    opacity: 0.9;
}
.summary-body {
    font-size: 15.5px;
    line-height: 1.55;
    font-weight: 400;
}

/* Metric Cards Layout */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    margin-bottom: 32px;
}
.metric-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 120px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.01);
    transition: transform 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
}
.metric-card-left {
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.metric-card-label {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.metric-card-value {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
}
.metric-card-subvalue {
    font-size: 13px;
    color: #64748b;
    margin-top: 4px;
}
.metric-card-pill {
    background-color: #ffedd5;
    color: #ea580c;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 9999px;
    margin-left: 10px;
    display: inline-block;
}

/* Analytics Row Layout */
.analytics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 32px;
}
.analytics-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.01);
}
.analytics-card-title {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 24px;
}

/* Issues by Category items */
.category-item {
    margin-bottom: 16px;
}
.category-header {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
}
.category-bar-bg {
    background-color: #f1f5f9;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
}
.category-bar-fill {
    background-color: #0b57d0;
    height: 100%;
    border-radius: 4px;
}

/* Filter Card Wrap */
.filter-wrapper {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 16px 24px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.01);
}

/* Findings Card Layout */
.finding-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    position: relative;
    box-shadow: 0 1px 3px rgba(0,0,0,0.01);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.finding-card:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}
.finding-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
.finding-card-badges {
    display: flex;
    gap: 8px;
    align-items: center;
}
.badge-severity {
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    text-transform: uppercase;
    font-family: 'Outfit', sans-serif;
}
.badge-severity.critical { background-color: #fee2e2; color: #ef4444; }
.badge-severity.high { background-color: #ffedd5; color: #f97316; }
.badge-severity.medium { background-color: #fef9c3; color: #ca8a04; }
.badge-severity.low { background-color: #dcfce7; color: #22c55e; }

.badge-clause {
    background-color: #f1f5f9;
    color: #475569;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
}
.finding-card-confidence {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: 0.5px;
}
.confidence-bar-bg {
    background-color: #e2e8f0;
    width: 60px;
    height: 6px;
    border-radius: 3px;
    overflow: hidden;
}
.confidence-bar-fill {
    height: 100%;
    border-radius: 3px;
}
.confidence-bar-fill.high { background-color: #22c55e; }
.confidence-bar-fill.medium { background-color: #0b57d0; }
.confidence-bar-fill.low { background-color: #cbd5e1; }

.finding-card-title {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
    line-height: 1.3;
}
.finding-card-desc {
    font-size: 14.5px;
    color: #475569;
    line-height: 1.5;
    margin-bottom: 16px;
}
.suggested-fix-box {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
    padding: 14px 18px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.suggested-fix-icon {
    font-size: 18px;
    color: #22c55e;
    margin-top: 1px;
}
.suggested-fix-text {
    font-size: 14px;
    color: #166534;
    line-height: 1.5;
}

/* Custom styling for Streamlit widgets */
div.stDownloadButton > button {
    background-color: #ffffff !important;
    color: #0b57d0 !important;
    border: 1.5px solid #0b57d0 !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
    font-size: 14px !important;
    box-shadow: none !important;
}
div.stDownloadButton > button:hover {
    background-color: #0b57d0 !important;
    color: #ffffff !important;
}
div.stButton > button {
    background-color: #0b57d0 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    font-size: 16px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
}
div.stButton > button:hover {
    background-color: #0045b3 !important;
    box-shadow: 0 4px 12px rgba(11, 87, 208, 0.15) !important;
}
div[data-testid="stFileUploader"] {
    background-color: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 16px !important;
    padding: 24px !important;
    min-height: 204px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}
div[data-testid="stFileUploader"] section {
    background-color: transparent !important;
    padding: 0 !important;
    border: none !important;
    width: 100% !important;
}
div[data-testid="stFileUploaderDropzone"] {
    border: none !important;
    background-color: transparent !important;
    padding: 0 !important;
}
div[data-testid="stSidebar"] button {
    background-color: transparent !important;
    color: #475569 !important;
    border: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 14.5px !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    box-shadow: none !important;
    width: 100% !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
}
div[data-testid="stSidebar"] button:hover {
    background-color: rgba(203, 213, 225, 0.4) !important;
    color: #0f172a !important;
}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ----------------- SCREEN 1: HOME SCREEN -----------------
if st.session_state.current_screen == "home":
    # Ensure sidebar is collapsed on Home screen
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] {display: none;}
    [data-testid="stAppViewBlockContainer"], .main .block-container {
        padding-left: 48px !important;
        padding-right: 48px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Home navbar with clickable logo that links to /?screen=home
    render_html("""
    <div class="navbar">
      <div class="navbar-left">
        <a href="/?screen=home" target="_self" class="navbar-logo-link">
          <div class="navbar-logo-icon">🛡️</div>
          <div class="navbar-logo-text">The Auditor</div>
        </a>
      </div>
      <div class="navbar-right">
        <span class="navbar-pill">EU MDR 2017/745</span>
      </div>
    </div>
    """)

    # Home Content
    render_html("""
    <div class="home-container">
      <div class="home-badge">
        <span>✓</span> Regulatory AI Engine v4.2
      </div>
      <h1 class="home-title">AI-powered medical device<br>compliance audit</h1>
      <p class="home-subtitle">Upload your Clinical Evaluation Report and we check it against EU MDR regulations in seconds. Reduce audit preparation time by up to 80%.</p>
    </div>
    """)

    # Centered File Uploader
    st.markdown('<div class="uploader-label" style="text-align: center; font-size: 18px; margin-bottom: 16px;">Clinical Evaluation Report (PDF)</div>', unsafe_allow_html=True)
    c_upload = st.columns([1, 2, 1])
    with c_upload[1]:
        cer_file = st.file_uploader("Clinical Evaluation Report (PDF)", type="pdf", label_visibility="collapsed", key="cer_file")

    # Options and Run Audit
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c_check = st.columns([1, 2, 1])
    with c_check[1]:
        run_real = st.button("Run Compliance Audit", use_container_width=True)

    # Platform Capabilities Grid under uploader to fill space nicely
    render_html("""
    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">LLM Regulatory Agent</div>
        <div class="feature-desc">Powered by Groq Llama-3.3-70B model to verify protocol wording and identify hidden regulatory gaps.</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Semantic Retrieval</div>
        <div class="feature-desc">Uses semantic search to cross-reference report contents with the exact matching EU MDR guidelines.</div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Readiness Scoring</div>
        <div class="feature-desc">Provides a quantified readiness rating based on the severity and category density of identified violations.</div>
      </div>
    </div>
    """)

    if run_real:
        if cer_file:
            from ingest import extract_text, chunk_text
            from retriever import Retriever
            from auditor import audit_section, readiness_score
            
            def save(f):
                t = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                t.write(f.read())
                t.close()
                return t.name
            
            # Placeholders for dynamic progress feedback
            status_placeholder = st.empty()
            progress_bar = st.progress(0.0)
            
            def update_status(title, estimate, steps_list, progress_val):
                progress_bar.progress(progress_val)
                steps_html = ""
                for step, state in steps_list:
                    if state == "active":
                        steps_html += f"<li style='color:#0b57d0; font-weight:bold; margin-bottom:8px;'>⏳ {step}</li>"
                    elif state == "done":
                        steps_html += f"<li style='color:#22c55e; margin-bottom:8px;'>✓ {step}</li>"
                    else:
                        steps_html += f"<li style='color:#94a3b8; margin-bottom:8px;'>○ {step}</li>"
                
                status_box = f"""
                <div style="background-color:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:24px; margin-bottom:24px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
                  <h3 style="margin-top:0; color:#0f172a; font-family:'Outfit', sans-serif;">{title}</h3>
                  <p style="color:#64748b; font-size:14px; margin-bottom:16px;">Estimated total time: <b>{estimate}</b></p>
                  <ul style="padding-left:0; list-style-type:none; font-family:'Outfit', sans-serif; font-size:15px; margin:0;">
                    {steps_html}
                  </ul>
                </div>
                """
                status_placeholder.markdown(textwrap.dedent(status_box), unsafe_allow_html=True)

            audit_steps = [
                ("Extracting and chunking Clinical Evaluation Report", "active"),
                ("Searching MDR regulatory guidelines", "pending"),
                ("Running compliance audit with AI models", "pending")
            ]
            update_status("Starting Compliance Audit...", "~20-30 seconds", audit_steps, 0.1)

            try:
                # Step 1: Ingest
                cer_path = save(cer_file)
                cer_text = extract_text(cer_path)
                cer_chunks = chunk_text(cer_text)
                
                if len(cer_chunks) == 0:
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.error("Error: No text could be extracted from the uploaded PDF. Please make sure the PDF contains selectable text (not scanned images without OCR).")
                    st.stop()
                
                audit_steps[0] = ("Extracting and chunking Clinical Evaluation Report", "done")
                audit_steps[1] = ("Searching MDR regulatory guidelines", "active")
                update_status("Analyzing guidelines...", "~20-30 seconds", audit_steps, 0.3)
                
                # Step 2: Retrieve from system default guideline
                guideline_path = "data/guideline.pdf"
                if not os.path.exists(guideline_path):
                    status_placeholder.empty()
                    progress_bar.empty()
                    st.error("Error: Default guideline.pdf not found in data/ directory.")
                    st.stop()
                    
                guideline_text = extract_text(guideline_path)
                guideline_chunks = chunk_text(guideline_text)
                retriever = Retriever(guideline_chunks)
                
                audit_steps[1] = ("Searching MDR regulatory guidelines", "done")
                audit_steps[2] = ("Running compliance audit with AI models", "active")
                update_status("Executing compliance checks...", "~20-30 seconds", audit_steps, 0.5)

                # Limit sections to exactly 5 sections of 800 words
                cer_chunks = cer_chunks[:5]
                    
                findings = []
                for idx, sec in enumerate(cer_chunks):
                    progress_val = 0.5 + 0.5 * ((idx + 1) / len(cer_chunks))
                    audit_steps[2] = (f"Running compliance audit with AI models (section {idx+1}/{len(cer_chunks)})...", "active")
                    update_status("Executing compliance checks...", "~20-30 seconds", audit_steps, progress_val)
                    
                    clauses = "\n---\n".join(retriever.search(sec, k=3))
                    findings.extend(audit_section(sec, clauses))
                
                audit_steps[2] = ("Running compliance audit with AI models", "done")
                update_status("Audit complete! Redirecting...", "0 seconds", audit_steps, 1.0)
                
                # Dynamic category counts for summary
                from collections import Counter
                category_counts = Counter()
                for f in findings:
                    category_counts[f.category] += 1
                
                st.session_state.report = AuditReport(
                    document_name=cer_file.name,
                    findings=findings,
                    readiness_score=readiness_score(findings),
                    summary={
                        "total_findings": len(findings),
                        "categories": dict(category_counts)
                    }
                )
                st.session_state.current_screen = "dashboard"
                st.rerun()
                
            except Exception as e:
                status_placeholder.empty()
                progress_bar.empty()
                st.error(f"Error during compliance audit: {e}\n\nPlease check that your GROQ_API_KEY environment variable is set correctly in your .env file.")
        else:
            st.warning("Please upload a Clinical Evaluation Report (PDF) to run the audit.")

    # Sample data handler removed

    # Home Footer features
    render_html("""
    <div class="home-footer-features">
      <div class="home-footer-feature"><span>🔗</span> CLAUSE-GROUNDED</div>
      <div class="home-footer-feature"><span>📊</span> CONFIDENCE-SCORED</div>
      <div class="home-footer-feature"><span>📄</span> EXPORTABLE REPORT</div>
    </div>
    """)


# ----------------- SCREEN 2: DASHBOARD SCREEN -----------------
elif st.session_state.current_screen == "dashboard" and st.session_state.report:
    report = st.session_state.report

    # Dashboard Navbar with clickable logo that links to /?screen=home
    render_html(f"""
    <div class="navbar">
      <div class="navbar-left">
        <a href="/?screen=home" target="_self" class="navbar-logo-link">
          <div class="navbar-logo-icon">🛡️</div>
          <div class="navbar-logo-text">The Auditor</div>
        </a>
      </div>
      <div class="navbar-right">
        <span class="navbar-doc-title">{report.document_name}</span>
        <div id="dl-btn-container"></div>
      </div>
    </div>
    """)
    
    # We overlay the streamlit download button over the top-right navbar placeholder using CSS
    st.markdown("""
    <style>
    /* Position the streamlit download button absolute over the navbar right side */
    .stDownloadButton {
        position: fixed;
        top: 14px;
        right: 40px;
        z-index: 1001;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Actually render the download button (Streamlit handles PDF export with build_html)
    st.download_button("⬇ Download report", build_html(report), file_name="audit_report.html", mime="text/html")

    # Left Sidebar content
    with st.sidebar:
        sidebar_html = """
        <div class="sidebar-profile">
          <div class="sidebar-avatar">MA</div>
          <div class="sidebar-profile-info">
            <span class="sidebar-profile-name">Medical Auditor</span>
            <span class="sidebar-profile-title">Level 4 Certification</span>
          </div>
        </div>
        <div class="sidebar-menu">
          <div class="sidebar-item active"><span>📊</span> Overview</div>
        </div>
        """
        render_html(sidebar_html)
        
        # Clickable native button for Back to Home
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 Back to Home", key="btn_sidebar_home", use_container_width=True):
            st.session_state.current_screen = "home"
            st.session_state.report = None
            st.rerun()

    # Dashboard Header
    render_html("""
    <div class="dashboard-header">
      <h1 class="dashboard-title">Audit Results</h1>
      <p class="dashboard-subtitle">Comprehensive compliance analysis of MDR clinical technical documentation.</p>
    </div>
    """)

    # Compute stats dynamically from findings
    total_findings = len(report.findings)
    avg_confidence = int(sum(f.confidence for f in report.findings) / total_findings * 100) if total_findings else 0

    # Severity stats
    sev_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for f in report.findings:
        sev_counts[f.severity] = sev_counts.get(f.severity, 0) + 1

    crit_high_count = sev_counts["Critical"] + sev_counts["High"]
    crit_high_pill = '<span class="metric-card-pill">Requires Attention</span>' if crit_high_count > 0 else ''

    # 0. Executive Summary Card (fills blank spaces, looks extremely premium)
    summary_text = (
        f"The technical clinical document achieved a Regulatory Readiness Score of <b>{report.readiness_score:.0f}/100</b>. "
        f"We identified a total of <b>{total_findings} gaps</b> relative to the EU MDR 2017/745 guidelines. "
        f"Key areas of exposure are in <b>{', '.join([f'{count} {cat}' for cat, count in sorted(report.summary.get('categories', {}).items(), key=lambda x: x[1], reverse=True)[:2]]) if isinstance(report.summary, dict) and report.summary.get('categories') else 'Clinical Evaluation'}</b>. "
        f"Immediate action is recommended to resolve the <b>{crit_high_count} High-severity violation(s)</b>."
    )
    
    executive_summary_html = f"""
    <div class="summary-card">
      <div class="summary-title">Executive Summary & Key Insights</div>
      <div class="summary-body">{summary_text}</div>
    </div>
    """
    render_html(executive_summary_html)

    # Circular Readiness Score SVG
    score = int(report.readiness_score)
    circular_svg = f"""
    <svg width="68" height="68" viewBox="0 0 36 36">
      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#f1f5f9" stroke-width="3.5" />
      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#0b57d0" stroke-width="3.5" stroke-dasharray="{score}, 100" stroke-linecap="round" />
      <text x="18" y="20.35" font-family="'Outfit', sans-serif" font-size="8px" font-weight="bold" text-anchor="middle" fill="#0b57d0">{score}%</text>
    </svg>
    """

    # 1. Metrics Grid
    metrics_grid_html = f"""
    <div class="metrics-grid">
      <!-- Card 1: Readiness Score -->
      <div class="metric-card">
        <div class="metric-card-left">
          <div class="metric-card-label">Readiness Score</div>
          <div class="metric-card-value">{score}/100</div>
        </div>
        {circular_svg}
      </div>

      <!-- Card 2: Total Findings -->
      <div class="metric-card">
        <div class="metric-card-left">
          <div class="metric-card-label">Total Findings</div>
          <div class="metric-card-value">{total_findings}</div>
          <div class="metric-card-subvalue">Across {len(set(f.category for f in report.findings))} major sections</div>
        </div>
      </div>

      <!-- Card 3: Critical + High -->
      <div class="metric-card">
        <div class="metric-card-left">
          <div class="metric-card-label">Critical + High</div>
          <div style="display: flex; align-items: center;">
            <span class="metric-card-value">{crit_high_count}</span>
            {crit_high_pill}
          </div>
        </div>
      </div>

      <!-- Card 4: Avg Confidence -->
      <div class="metric-card">
        <div class="metric-card-left" style="width: 100%;">
          <div class="metric-card-label">Avg Confidence</div>
          <div class="metric-card-value">{avg_confidence}%</div>
          <div class="progress-container" style="background:#e2e8f0; height:6px; border-radius:3px; margin-top:12px; overflow:hidden; width: 100%;">
            <div class="progress-bar" style="width:{avg_confidence}%; background:#0b57d0; height:100%;"></div>
          </div>
        </div>
      </div>
    </div>
    """
    render_html(metrics_grid_html)

    # Compute severity percentages for the bar chart
    if total_findings > 0:
        crit_pct = (sev_counts["Critical"] / total_findings) * 100
        high_pct = (sev_counts["High"] / total_findings) * 100
        med_pct = (sev_counts["Medium"] / total_findings) * 100
        low_pct = (sev_counts["Low"] / total_findings) * 100
    else:
        crit_pct = high_pct = med_pct = low_pct = 0

    severity_bar_html = f"""
    <div style="display:flex; height:10px; border-radius:5px; overflow:hidden; background:#e2e8f0; margin-bottom:24px; margin-top: 10px;">
      <div style="width: {crit_pct}%; background: #ef4444;" title="Critical: {sev_counts['Critical']}"></div>
      <div style="width: {high_pct}%; background: #f97316;" title="High: {sev_counts['High']}"></div>
      <div style="width: {med_pct}%; background: #eab308;" title="Medium: {sev_counts['Medium']}"></div>
      <div style="width: {low_pct}%; background: #22c55e;" title="Low: {sev_counts['Low']}"></div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:600; color:#64748b; padding: 0 10px;">
      <span><span style="color:#ef4444; margin-right:6px;">●</span>Critical ({sev_counts['Critical']})</span>
      <span><span style="color:#f97316; margin-right:6px;">●</span>High ({sev_counts['High']})</span>
      <span><span style="color:#eab308; margin-right:6px;">●</span>Medium ({sev_counts['Medium']})</span>
      <span><span style="color:#22c55e; margin-right:6px;">●</span>Low ({sev_counts['Low']})</span>
    </div>
    """

    # Category progress bars
    category_counts = {}
    for f in report.findings:
        category_counts[f.category] = category_counts.get(f.category, 0) + 1

    # Sort categories by count descending
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    max_count = max(category_counts.values()) if category_counts else 1

    category_bars_html = ""
    for cat, count in sorted_categories:
        pct = (count / max_count) * 100
        category_bars_html += f"""
        <div class="category-item">
          <div class="category-header">
            <span>{cat}</span>
            <span>{count}</span>
          </div>
          <div class="category-bar-bg">
            <div class="category-bar-fill" style="width: {pct}%;"></div>
          </div>
        </div>
        """

    # 2. Analytics grid HTML blocks
    st.markdown('<div class="analytics-grid">', unsafe_allow_html=True)
    
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">Severity Distribution</div>', unsafe_allow_html=True)
    render_html(severity_bar_html)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-card-title">Issues by Category</div>', unsafe_allow_html=True)
    render_html(category_bars_html)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Filters wrapper
    st.markdown('<div class="filter-wrapper">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([5, 2, 3])
    with f_col1:
        search_query = st.text_input("Search finding or regulation...", placeholder="Search finding or regulation...", label_visibility="collapsed", key="search_query")
    with f_col2:
        severity_filter = st.selectbox("Severity", ["All Severities", "Critical", "High", "Medium", "Low"], label_visibility="collapsed", key="severity_filter")
    with f_col3:
        confidence_threshold = st.slider("CONFIDENCE THRESHOLD", min_value=0, max_value=100, value=80, step=5, format="%d%%", key="confidence_threshold")
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Filter findings
    filtered_findings = []
    for f in report.findings:
        # Search query matching
        if search_query:
            q = search_query.lower()
            if q not in f.violating_statement.lower() and q not in f.guideline_clause.lower() and q not in f.explanation.lower():
                continue
        # Severity matching
        if severity_filter != "All Severities":
            if f.severity != severity_filter:
                continue
        # Confidence matching
        if f.confidence * 100 < confidence_threshold:
            continue
        filtered_findings.append(f)

    # Sort findings by severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    filtered_findings.sort(key=lambda x: severity_order.get(x.severity, 4))

    # Render findings
    if filtered_findings:
        for f in filtered_findings:
            sev_class = f.severity.lower()
            conf_pct = int(f.confidence * 100)
            
            # Confidence styling
            conf_class = "low"
            if conf_pct >= 85:
                conf_class = "high"
            elif conf_pct >= 70:
                conf_class = "medium"

            suggested_fix_html = ""
            if f.suggested_correction:
                text = f.suggested_correction
                if not text.lower().startswith("suggested fix"):
                    text = f"Suggested fix: {text}"
                suggested_fix_html = f"""
                <div class="suggested-fix-box">
                  <div class="suggested-fix-icon">💡</div>
                  <div class="suggested-fix-text">{text}</div>
                </div>
                """

            card_html = f"""
            <div class="finding-card" style="border-left: 4px solid {get_severity_color(f.severity)};">
              <div class="finding-card-header">
                <div class="finding-card-badges">
                  <span class="badge-severity {sev_class}">{f.severity}</span>
                  <span class="badge-clause">{f.guideline_clause}</span>
                </div>
                <div class="finding-card-confidence">
                  <span>CONFIDENCE</span>
                  <div class="confidence-bar-bg">
                    <div class="confidence-bar-fill {conf_class}" style="width: {conf_pct}%;"></div>
                  </div>
                  <span style="color: #0f172a; font-weight: 700;">{conf_pct}%</span>
                </div>
              </div>
              <div class="finding-card-title">{f.violating_statement}</div>
              <div class="finding-card-desc">{f.explanation}</div>
              {suggested_fix_html}
            </div>
            """
            render_html(card_html)
    else:
        st.markdown("<div style='text-align:center; padding:40px; color:#64748b;'>No findings match the current filters.</div>", unsafe_allow_html=True)