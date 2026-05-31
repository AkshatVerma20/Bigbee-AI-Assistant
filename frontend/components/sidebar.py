import streamlit as st
from frontend.utils.api_client import APIClient
from frontend.components.auth import render_logout_button


def render_sidebar(api: APIClient):
    """Render the sidebar. Returns (user_id, session_id, mode)."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:10px 0 4px 0;">
            <span style="font-size:40px;">🤖</span>
            <h2 style="margin:0;
          background: linear-gradient(90deg, #4285F4, #7c3aed);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:22px;">
               🐝Bigbee
            </h2>
        </div>
        """, unsafe_allow_html=True)


        healthy = api.health()
        dot = "🟢" if healthy else "🔴"
        st.markdown(
            f'<p style="text-align:center;font-size:13px;color:#888;">{dot} '
            f'{"Backend online" if healthy else "Backend offline"}</p>',
            unsafe_allow_html=True
        )

        st.divider()


        render_logout_button()
        st.divider()

    
        st.markdown("###  Session")
        user_id = st.session_state.get("logged_in_user", "user")
        st.markdown(f"**User:** `{user_id}`")
        session_id = st.text_input("Session ID", value="session_1", key="session_id_input")
        st.divider()

        st.markdown("###  Mode")
        mode = st.radio(
            "Chat mode",
            ["Standard Agent", "Multi-Agent (complex tasks)"],
            index=0
        )
        st.divider()

        
        st.markdown("###  Upload Documents")
        uploaded = st.file_uploader("PDF / TXT / CSV / MD", type=["pdf", "txt", "md", "csv"])
        if uploaded and st.button("📥 Upload & Index", use_container_width=True):
            with st.spinner(f"Uploading {uploaded.name}..."):
                try:
                    result = api.upload_file(uploaded.read(), uploaded.name, uploaded.type or "text/plain")
                    indexed = result.get("rag_indexed", False)
                    st.success(f" {result['filename']}" + (" + RAG indexed" if indexed else ""))
                except Exception as e:
                    st.error(f"Upload failed: {e}")

        files = api.list_uploads()
        if files:
            st.caption(f"Files: {', '.join(files)}")
        st.divider()


        st.markdown("###  History")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📂 Load", use_container_width=True):
                try:
                    msgs = api.get_history(user_id, session_id)
                    st.session_state["messages"] = [
                        {"role": m["role"], "content": m["content"]} for m in msgs
                    ]
                    st.success(f"Loaded {len(msgs)}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state["messages"] = []
                try:
                    api.clear_history(user_id, session_id)
                except Exception:
                    pass
                st.rerun()

        st.divider()
        st.markdown(
            '<p style="text-align:center;font-size:11px;color:#444;">'
            'Powered by GPT • LangGraph • ChromaDB</p>',
            unsafe_allow_html=True
        )

    return user_id, session_id, mode
