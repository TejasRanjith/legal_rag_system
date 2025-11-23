import streamlit as st
import os
from security import SecurityManager
from database import init_db, User, AuditLog, Document
from rag_engine import RAGEngine
from sqlalchemy.orm import Session
import datetime
import tempfile
import json

# Initialize components
if 'security_manager' not in st.session_state:
    st.session_state.security_manager = SecurityManager()
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = RAGEngine()
if 'db_session' not in st.session_state:
    SessionLocal = init_db()
    st.session_state.db_session = SessionLocal()

def log_audit(action, details, user_id):
    log = AuditLog(user_id=user_id, action=action, details=details)
    st.session_state.db_session.add(log)
    st.session_state.db_session.commit()

def login_page():
    st.title("Secure Legal RAG - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            user = st.session_state.db_session.query(User).filter_by(username=username).first()
            if user and st.session_state.security_manager.verify_password(user.password_hash, password):
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.role = user.role
                log_audit("LOGIN", "User logged in", user.id)
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with col2:
        if st.button("Register"):
            if st.session_state.db_session.query(User).filter_by(username=username).first():
                st.error("Username exists")
            else:
                hashed = st.session_state.security_manager.hash_password(password)
                new_user = User(username=username, password_hash=hashed)
                st.session_state.db_session.add(new_user)
                st.session_state.db_session.commit()
                st.success("Registered! Please login.")
                log_audit("REGISTER", f"New user registered: {username}", new_user.id)

def inject_custom_css():
    st.markdown("""
    <style>
        /* Main Background */
        .stApp {
            background-color: #343541;
        }
        
        /* Sidebar Background */
        [data-testid="stSidebar"] {
            background-color: #202123;
        }
        
        /* Minimalist Buttons in Sidebar */
        div[data-testid="stSidebar"] .stButton > button {
            background-color: transparent !important;
            color: #ececf1 !important;
            border: none !important;
            text-align: left !important;
            padding-left: 0.5rem !important;
            font-weight: normal !important;
            width: 100% !important;
            display: flex !important;
            justify-content: flex-start !important;
            transition: background-color 0.2s !important;
        }
        
        div[data-testid="stSidebar"] .stButton > button:hover {
            background-color: #2A2B32 !important;
            color: #ffffff !important;
            border-radius: 5px !important;
        }
        
        /* Popover Button Styling */
        [data-testid="stPopover"] {
            display: inline-block;
            width: 100%; /* Full width for sidebar */
        }
        
        /* Sidebar Button Styling to match */
        [data-testid="stPopover"] > button {
            background-color: transparent !important;
            color: #ececf1 !important;
            border: none !important;
            text-align: left !important;
            padding-left: 0.5rem !important;
            font-weight: normal !important;
            width: 100% !important;
            display: flex !important;
            justify-content: flex-start !important;
            transition: background-color 0.2s !important;
        }

        [data-testid="stPopover"] > button:hover {
            background-color: #2A2B32 !important;
            color: #ffffff !important;
            border-radius: 5px !important;
        }

        /* Document Card Styling */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
            background-color: #40414f;
            border-radius: 8px;
            padding: 1rem;
        }

        /* Adjust chat input padding back to normal */
        .stChatInput textarea {
            background-color: #40414f !important;
            color: white !important;
            border: 1px solid #565869 !important;
            padding-left: 1rem !important; 
        }
        
        /* Centered Landing Page Styling */
        .landing-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 60vh; /* Vertically center */
            text-align: center;
        }
        
        .landing-header {
            font-size: 2.5rem;
            font-weight: 600;
            color: #ececf1;
            margin-bottom: 2rem;
        }
        
        /* Custom Input Bar Styling */
        .custom-input-container {
            background-color: #40414f;
            border: 1px solid #565869;
            border-radius: 24px;
            padding: 0.5rem 1rem;
            display: flex;
            align-items: center;
            width: 100%;
            max-width: 700px;
            margin: 0 auto;
        }
        
        /* Hide default Streamlit input decoration for custom bar */
        .stTextInput > div > div {
            background-color: transparent !important;
            border: none !important;
            color: white !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #ececf1;
        }
        
        /* Remove default Streamlit top padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem; 
        }
    </style>
    """, unsafe_allow_html=True)

def main_app():
    inject_custom_css()
    # Initialize page state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chat Assistant"

    # Sidebar Navigation
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}")
        
        # Navigation Buttons
        if st.button("💬 Chat Assistant", use_container_width=True):
            st.session_state.current_page = "Chat Assistant"
            st.rerun()
            
        if st.button("📂 Documents", use_container_width=True):
            st.session_state.current_page = "Documents"
            st.rerun()

        if st.button("📜 Audit Logs", use_container_width=True):
            st.session_state.current_page = "Audit Logs"
            st.rerun()
        
        # Upload Popover in Sidebar
        with st.popover("➕ Add Document", use_container_width=True):
            st.markdown("### Upload Document")
            uploaded_file = st.file_uploader("Select PDF", type="pdf", label_visibility="collapsed")
            if uploaded_file:
                if st.button("Process Upload", use_container_width=True):
                    with st.spinner("Processing..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        storage_dir = "storage"
                        os.makedirs(storage_dir, exist_ok=True)
                        encrypted_path = os.path.join(storage_dir, f"{uploaded_file.name}.enc")
                        
                        st.session_state.security_manager.encrypt_file(tmp_path)
                        import shutil
                        shutil.move(tmp_path, encrypted_path)
                        
                        # Auto-generate description
                        desc = f"Uploaded on {datetime.datetime.now().strftime('%Y-%m-%d')}"
                        
                        new_doc = Document(filename=uploaded_file.name, owner_id=st.session_state.user_id, encrypted_path=encrypted_path, description=desc)
                        st.session_state.db_session.add(new_doc)
                        st.session_state.db_session.commit()
                        
                        decrypted_content = st.session_state.security_manager.decrypt_file(encrypted_path)
                        from langchain_community.document_loaders import PyPDFLoader
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_decrypt:
                            tmp_decrypt.write(decrypted_content)
                            decrypt_path = tmp_decrypt.name
                        
                        loader = PyPDFLoader(decrypt_path)
                        pages = loader.load()
                        full_text = "".join([p.page_content for p in pages])
                        
                        st.session_state.rag_engine.ingest_document(full_text, {"source": uploaded_file.name, "owner": st.session_state.username})
                        os.remove(decrypt_path)
                        
                        log_audit("UPLOAD", f"Uploaded {uploaded_file.name}", st.session_state.user_id)
                        st.success("Uploaded!")
                        st.rerun()
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            log_audit("LOGOUT", "User logged out", st.session_state.user_id)
            del st.session_state.user_id
            st.rerun()

    # Main Content Area
    if st.session_state.current_page == "Chat Assistant":
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # LANDING PAGE STATE (Empty Chat)
        if not st.session_state.messages:
            # Use columns to center vertically/horizontally roughly
            st.markdown('<div class="landing-container">', unsafe_allow_html=True)
            st.markdown('<div class="landing-header">What can I help you with today ?</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Custom Input Bar Simulation
            # We use a container with a border to mimic the pill shape
            with st.container(border=True):
                # The actual input
                initial_prompt = st.text_input("Ask anything", label_visibility="collapsed", placeholder="Ask anything...", key="landing_input")
            
            # Handle Submission from Landing Page
            if initial_prompt:
                st.session_state.messages.append({"role": "user", "content": initial_prompt})
                # Process the query immediately
                with st.spinner("Thinking..."):
                    response = st.session_state.rag_engine.query(initial_prompt)
                    answer = response['result']
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    # Log
                    log_details = json.dumps({"prompt": initial_prompt, "response": answer, "refs": []})
                    log_audit("QUERY", log_details, st.session_state.user_id)
                st.rerun()

        # STANDARD CHAT STATE (Messages Exist)
        else:
            st.header("Legal Assistant")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("Ask about your documents..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state.rag_engine.query(prompt)
                        answer = response['result']
                        
                        # Extract references
                        sources = set()
                        if 'source_documents' in response:
                            for doc in response['source_documents']:
                                if 'source' in doc.metadata:
                                    sources.add(doc.metadata['source'])
                        
                        st.markdown(answer)
                        # Sources hidden as per user request
                        
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # Structured Log
                        log_details = json.dumps({
                            "prompt": prompt,
                            "response": answer,
                            "refs": list(sources) if sources else []
                        })
                        log_audit("QUERY", log_details, st.session_state.user_id)

    elif st.session_state.current_page == "Documents":
        st.header("Document Explorer")
        
        # Search Bar
        search_query = st.text_input("🔍 Search Documents", placeholder="Search by filename...")
        
        query = st.session_state.db_session.query(Document).filter_by(owner_id=st.session_state.user_id)
        if search_query:
            query = query.filter(Document.filename.contains(search_query))
        
        docs = query.all()
        
        if not docs:
            st.info("No documents found.")
        else:
            # Grid Layout for Drive Style
            cols = st.columns(3)
            for idx, doc in enumerate(docs):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"#### 📄 {doc.filename}")
                        st.caption(f"📅 {doc.upload_date.strftime('%Y-%m-%d')}")
                        st.caption(f"📝 {doc.description}")
                        
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            # Download Logic
                            # Initial button to trigger decryption
                            if st.button("⬇️", key=f"dl_{doc.id}", help="Prepare Download", use_container_width=True):
                                try:
                                    decrypted = st.session_state.security_manager.decrypt_file(doc.encrypted_path)
                                    st.download_button(
                                        label="💾",
                                        data=decrypted,
                                        file_name=doc.filename,
                                        mime="application/pdf",
                                        key=f"save_{doc.id}",
                                        help="Save File",
                                        use_container_width=True
                                    )
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        
                        with col_d2:
                            if st.button("🗑️", key=f"del_{doc.id}", help="Delete Document", type="primary", use_container_width=True):
                                st.session_state.db_session.delete(doc)
                                st.session_state.db_session.commit()
                                # Optional: Remove from disk and vector store (complex for vector store, simple for disk)
                                if os.path.exists(doc.encrypted_path):
                                    os.remove(doc.encrypted_path)
                                log_audit("DELETE", f"Deleted {doc.filename}", st.session_state.user_id)
                                st.rerun()

    elif st.session_state.current_page == "Audit Logs":
        st.header("Audit Logs")
        
        if st.session_state.role == 'admin' or True:
            # Join AuditLog with User to get username
            logs = st.session_state.db_session.query(AuditLog, User.username)\
                .join(User, AuditLog.user_id == User.id)\
                .order_by(AuditLog.timestamp.desc())\
                .limit(50).all()
            
            for log, username in logs:
                timestamp_str = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                
                if log.action == "QUERY":
                    with st.popover(f"{timestamp_str} - {username} - QUERY", use_container_width=True):
                        try:
                            details = json.loads(log.details)
                            st.markdown("**Conversation Details**")
                            st.divider()
                            st.markdown(f"**{username}:** {details.get('prompt', '')}")
                            st.markdown(f"**DocGPT:** {details.get('response', '')}")
                            st.divider()
                            
                            refs = details.get('refs', [])
                            ref_str = ", ".join([f"'{r}'" for r in refs]) if refs else "'None'"
                            st.markdown(f"**Refs:** {ref_str}")
                        except json.JSONDecodeError:
                            st.text(f"Details: {log.details}")
                else:
                    st.text(f"{timestamp_str} - {username} - {log.action}: {log.details}")

if __name__ == "__main__":
    if 'user_id' not in st.session_state:
        login_page()
    else:
        main_app()
