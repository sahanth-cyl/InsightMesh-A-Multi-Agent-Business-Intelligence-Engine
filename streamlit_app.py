import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import requests
import base64
import os

st.set_page_config(
    page_title="InsightMesh: Multi-Agent BI Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
custom_css = """
<style>
body {
    background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%);
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}
.header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem 2rem 1rem 2rem;
    border-radius: 18px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 24px rgba(44,83,100,0.12);
}
.header h1 {
    color: #fff;
    margin-bottom: 0.5rem;
    font-size: 2.5rem;
    font-weight: 700;
}
.header h3 {
    color: #e0e0e0;
    font-weight: 400;
    margin-bottom: 0.5rem;
}
.header .branding {
    color: #b3c6e6;
    font-size: 1rem;
    margin-top: 0.5rem;
}
.main-row {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    justify-content: stretch;
    width: 100%;
    gap: 2rem;
    margin-bottom: 2rem;
}
.chat-panel, .visual-panel {
    flex: 0.8;
    min-width: 0;
}
.visual-panel {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(44,83,100,0.10);
    padding: 1.2rem;
    min-height: 320px;
    max-width: 500px;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.visual-header {
    font-size: 1.3rem;
    font-weight: 600;
    color: #2c5364;
    margin-bottom: 1rem;
    letter-spacing: 0.02em;
}
</style>
"""
components.html(custom_css, height=0)

# Professional Header
st.markdown("""
<div class="header">
    <h1>InsightMesh: A Multi-Agent Business Intelligence Engine</h1>
    <h3>Enterprise AI for Data-driven Decisions</h3>
    <div class="branding">Powered by Claude API &mdash; Built for Accel-Anthropic AI Dev Day Hackathon</div>
</div>
""", unsafe_allow_html=True)

# Layout: Chat + Graphical Output

# Side-by-side layout: half chat, half graph

# Use HTML/CSS for true side-by-side layout, no scroll
st.markdown("""
<div class="main-row">
  <div class="chat-panel">
    <h2 style='color:#1976d2;'>Chat with Copilot</h2>
""", unsafe_allow_html=True)

# Only show the latest Q&A and graph
user_input = st.text_input("Type your question...", key="user_input")
last_question = st.session_state.get("last_question", "")
last_answer = st.session_state.get("last_answer", "")
image_base64 = st.session_state.get("last_image_base64")

if st.button("Send") and user_input:
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={"question": user_input},
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state["last_question"] = user_input
            st.session_state["last_answer"] = data.get("answer", "No answer received.")
            st.session_state["last_image_base64"] = data.get("image_base64")
        else:
            st.session_state["last_question"] = user_input
            st.session_state["last_answer"] = f"Error: {response.text}"
            st.session_state["last_image_base64"] = None
    except Exception as e:
        st.session_state["last_question"] = user_input
        st.session_state["last_answer"] = f"Backend error: {e}"
        st.session_state["last_image_base64"] = None
    last_question = st.session_state["last_question"]
    last_answer = st.session_state["last_answer"]
    image_base64 = st.session_state["last_image_base64"]

# Display only the latest Q&A
if last_question:
    st.markdown(f"<div style='text-align:right; color:#0f2027; font-size:1.5rem; font-weight:600; margin-bottom:0.5rem;'><span style='font-family:serif;'>Q:</span> {last_question}</div>", unsafe_allow_html=True)
if last_answer:
    # Remove code blocks (triple backticks) and troubleshooting links
    clean_answer = last_answer.split('For troubleshooting, visit:')[0].strip()
    if '```' in clean_answer:
        clean_answer = clean_answer.split('```')[0].strip()
    st.markdown(f"<div style='text-align:left; color:#2c5364; font-size:1.35rem; font-weight:500; margin-bottom:1.2rem;'><span style='font-family:serif;'>A:</span> {clean_answer}</div>", unsafe_allow_html=True)

st.markdown("""
  </div>
  <div class="visual-panel">
    <div class='visual-header'>Business Visualizations</div>
""", unsafe_allow_html=True)
chart_title = "Business Insight Chart"
if image_base64:
    st.markdown(f"<div style='font-weight:600; color:#1976d2; margin-bottom:0.5rem; font-size:1.5rem;'>{chart_title}</div>", unsafe_allow_html=True)
    st.image(base64.b64decode(image_base64.split(',')[-1]), caption=chart_title, use_container_width=True)
    b64 = image_base64.split(',')[-1]
    st.download_button("Download Chart", data=base64.b64decode(b64), file_name="business_chart.png", mime="image/png", key="download_chart")
else:
    if last_answer:
        # Remove code blocks (triple backticks) and troubleshooting links
        clean_answer = last_answer.split('For troubleshooting, visit:')[0].strip()
        if '```' in clean_answer:
            clean_answer = clean_answer.split('```')[0].strip()
        st.markdown(f"<div style='color:#2c5364; font-size:1.2rem; padding:1rem 0; font-weight:500;'>📝 <b>Insight:</b> {clean_answer}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; color:#b0b0b0; margin-top:2rem;'><span style='font-size:2.5rem;'>&#128202;</span><br><b>No visualizations yet</b><br><span style='font-size:1rem;'>Ask a question to generate a chart.</span></div>", unsafe_allow_html=True)
st.markdown("""
  </div>
</div>
""", unsafe_allow_html=True)

# Footer Branding
st.markdown("""
    <hr style="margin-top:2rem; margin-bottom:1rem;">
    <div style="text-align:center; color:#b3c6e6; font-size:0.95rem;">
        Built for Accel-Anthropic AI Dev Day Hackathon &mdash; Powered by Claude API<br>
        &copy; 2025 InsightMesh. All rights reserved.
    </div>
""", unsafe_allow_html=True)
