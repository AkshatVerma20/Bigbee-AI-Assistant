"""
Streamlit frontend — with login + Google-style vibrant theme.
Run: streamlit run frontend/app.py
"""
import streamlit as st
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from frontend.utils.api_client import APIClient
from frontend.components.sidebar import render_sidebar
from frontend.components.auth import render_login

st.set_page_config(
    page_title="Bigbee",
    page_icon="frontend/static/bee.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d0d;
    color: #f0f0f0;
    font-family: 'Google Sans', 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #13111f 0%, #0f0d1a 100%);
    border-right: 1px solid #1f2937;
}
[data-theme="light"] html,
[data-theme="light"] body,
[data-theme="light"] [data-testid="stAppViewContainer"] {
    background-color: #f5f5ff !important;
    color: #1a1a2e !important;
}
[data-theme="light"] [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ede9fe 0%, #f0eeff 100%) !important;
}
[data-theme="light"] [data-testid="stChatInput"] > div > div {
    background: #ffffff !important;
    border-color: #c4b5fd !important;
}
[data-theme="light"] [data-testid="stChatInput"] textarea {
    color: #1a1a2e !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0d1117 100%);
    border-right: 1px solid #1f2937;
}

/* ── Top header bar ── */
header[data-testid="stHeader"] {
    background: #0d0d0d;
    border-bottom: 1px solid #1f1f1f;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 20px;
    margin-bottom: 14px;
    padding: 6px 10px;
}

/* User message bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #1a237e22, #1565c022);
    border: 1px solid #1565c044;
}

/* Assistant message bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #1b5e2022, #2e7d3222);
    border: 1px solid #2e7d3244;
}

/* ── Chat input box ── */
[data-testid="stChatInput"] textarea {
    background: #1a1a2e !important;
    border: 4px solid #333 !important;
    border-radius: 4px !important;
    color: #fff !important;
    font-size: 15px !important;
    transition: border-color 0.2s;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #4285F4 !important;
    box-shadow: 0 0 0 3px #4285F422 !important;
}

/* ── Buttons ── */
.stButton > button {
    bbackground: linear-gradient(135deg, #4285F4, #1a73e8);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1a73e8, #1557b0);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px #4285F444;
}

/* ── Form submit button (login) ── */
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #4285F4 0%, #EA4335 50%, #34A853 100%);
background-size: 200%;
color: white;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 700;
    padding: 12px;
    transition: all 0.3s;
}
/* ── Chat input box ── */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
}
[data-testid="stChatInput"] > div > div {
    background: #1a1a2e !important;
    border: 1px solid #333 !important;
    border-radius: 30px !important;
    overflow: hidden !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: #fff !important;
    font-size: 15px !important;
    box-shadow: none !important;
    padding: 12px 16px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #4285F4, #7c3aed) !important;
    border-radius: 50% !important;
    border: none !important;
    margin-right: 8px !important;
    flex-shrink: 0 !important;
}
[data-testid="stBottom"], section[data-testid="stBottom"] > div,
div[class*="stChatFloatingInputContainer"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0 !important;
}
/* ── Text inputs ── */
[data-testid="stTextInput"] input {
    background: #111 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #fff !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #4285F4 !important;
}
[data-testid="stChatInput"] > div {
    border: none !important;
    outline: none !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label {
    color: #ccc !important;
}

/* ── Divider ── */
hr {
    border-color: #222;
}

/* ── Gradient title ── */
.gradient-title {
    background: linear-gradient(90deg, #4285F4, #EA4335, #FBBC05, #34A853);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 38px;
    font-weight: 900;
    margin-bottom: 2px;
}

/* ── Subtitle ── */
.subtitle {
    color: #666;
    font-size: 14px;
    margin-bottom: 16px;
}
/* ── Chat input box ── */
[data-testid="stChatInput"] {
    background: #1a1a2e !important;
    border: 1px solid #333 !important;
    border-radius: 30px !important;
    padding: 4px 8px !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: #fff !important;
    font-size: 15px !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 10px 16px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #4285F4, #7c3aed) !important;
    border-radius: 50% !important;
    border: none !important;
    margin-right: 4px !important;
}
[data-testid="stBottom"], section[data-testid="stBottom"] > div,
div[class*="stChatFloatingInputContainer"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0 !important;
}

/* ── Spinner text ── */
[data-testid="stSpinner"] p { color: #4285F4; }

/* ── Success / error ── */
[data-testid="stAlert"] { border-radius: 10px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #111; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4285F4; }
</style>
""", unsafe_allow_html=True)

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not render_login():
    st.stop()   # Stop rendering everything below until logged in

# ── Init session state ────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
api = APIClient(BACKEND_URL)

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "streaming" not in st.session_state:
    st.session_state["streaming"] = True


user_id, session_id, mode = render_sidebar(api)


st.markdown('<div class="gradient-title">Bigbee</div>', unsafe_allow_html=True)

if mode == "Multi-Agent (complex tasks)":
    st.markdown(
        '<div class="subtitle"> Multi-Agent mode — research + code + write. Slower but thorough.</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '<div class="subtitle"> Standard Agent — web search · calculator · code · document Q&A</div>',
        unsafe_allow_html=True
    )


for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


placeholder = (
    "Describe a complex task to research, analyse and write about..."
    if mode == "Multi-Agent (complex tasks)"
    else "Ask me anything — I can search the web, run code, read documents..."
)

if prompt := st.chat_input(placeholder):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "Multi-Agent (complex tasks)":
            with st.spinner("🧠 Agents working... (30–60 seconds)"):
                try:
                    result = api.multi_agent(prompt, user_id)
                    full_response = result.get("answer", "No answer generated")
                    st.markdown(full_response)
                    if result.get("research"):
                        with st.expander("📰 Research findings"):
                            st.markdown(result["research"])
                    if result.get("code"):
                        with st.expander("💻 Code & output"):
                            st.markdown(result["code"])
                except Exception as e:
                    full_response = f"⚠️ Error: {e}"
                    st.markdown(full_response)
        else:
            with st.spinner("Thinking..."):
                try:
                    full_response = api.chat(prompt, user_id, session_id)
                except Exception as e:
                    full_response = f"⚠️ Error: {e}"
            st.markdown(full_response)

    st.session_state["messages"].append({"role": "assistant", "content": full_response})
