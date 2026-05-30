"""
Login / authentication component.
Users are stored as a plain dict — for production, use a database with hashed passwords.
Add or remove users by editing the USERS dict below.
"""
import streamlit as st
import hashlib

# ── Authorized users ─────────────────────────────────────────────────────────
# Format: "username": "password"
# To add a new user just add a new line here.
USERS = {
    "dumbo":   "dumbo123",
    "akshat": "akshat123",
    "admin":  "admin123",
}


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Pre-hash all passwords so plain text isn't compared at runtime
_HASHED = {u: _hash(p) for u, p in USERS.items()}


def check_credentials(username: str, password: str) -> bool:
    username = username.strip().lower()
    return _HASHED.get(username) == _hash(password)


def render_login() -> bool:
    """
    Renders the login page.
    Returns True if the user is authenticated, False otherwise.
    """
    # Already logged in?
    if st.session_state.get("authenticated"):
        return True

    # ── Page styling ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* Hide default streamlit header on login page */
    header[data-testid="stHeader"] { display: none; }

    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 80px;
    }
    .login-logo {
        font-size: 64px;
        text-align: center;
        margin-bottom: 8px;
    }
    .login-title {
        font-size: 36px;
        font-weight: 800;
        text-align: center;
       background: linear-gradient(90deg, #4285F4, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .login-subtitle {
        font-size: 15px;
        color: #888;
        text-align: center;
        margin-bottom: 32px;
    }
    .login-box {
        background: #1e1e2e;
        border: 1px solid #333;
        border-radius: 16px;
        padding: 36px 40px;
        width: 100%;
        max-width: 400px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Center the form ───────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-title">Welcome to Bigbee</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sign in to continue</div>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤  Username", placeholder="Enter your username")
            password = st.text_input("🔒  Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif check_credentials(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["logged_in_user"] = username.strip().lower()
         #           st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        st.markdown(
            '<p style="text-align:center;color:#555;font-size:12px;margin-top:16px;">'
            'Contact admin to get access</p>',
            unsafe_allow_html=True
        )

    return False


def render_logout_button():
    """Small logout button — call this from the sidebar."""
    user = st.session_state.get("logged_in_user", "user")
    st.markdown(f"**👤 Logged in as:** `{user}`")
    if st.button(" Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["logged_in_user"] = ""
        st.session_state["messages"] = []
        st.rerun()
