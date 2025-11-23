import streamlit as st
import os
from security import SecurityManager
from database import init_db, User, AuditLog, Document
from rag_engine import RAGEngine
from sqlalchemy.orm import Session
import datetime
import tempfile

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

def main_app():
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        log_audit("LOGOUT", "User logged out", st.session_state.user_id)
        del st.session_state.user_id
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["Document Analysis", "Chat Assistant", "Audit Logs"])

    with tab1:
        st.header("Document Ingestion & Analysis")
        uploaded_file = st.file_uploader("Upload Legal Document (PDF)", type="pdf")
        
        if uploaded_file:
            if st.button("Process Document"):
                with st.spinner("Encrypting and Ingesting..."):
                    # Save temp
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    # Encrypt and Store
                    storage_dir = "storage"
                    os.makedirs(storage_dir, exist_ok=True)
                    encrypted_path = os.path.join(storage_dir, f"{uploaded_file.name}.enc")
                    
                    # In a real app, we'd encrypt the content before writing, or encrypt the file after.
                    # Here we simulate: read temp, encrypt, write to storage.
                    st.session_state.security_manager.encrypt_file(tmp_path) # Encrypts in place
                    
                    # Move/Copy to storage (renaming for simplicity)
                    import shutil
                    shutil.move(tmp_path, encrypted_path)
                    
                    # Record in DB
                    new_doc = Document(filename=uploaded_file.name, owner_id=st.session_state.user_id, encrypted_path=encrypted_path)
                    st.session_state.db_session.add(new_doc)
                    st.session_state.db_session.commit()
                    
                    # Ingest into RAG (Need decrypted content for this)
                    # Decrypt temporarily for ingestion
                    decrypted_content = st.session_state.security_manager.decrypt_file(encrypted_path)
                    
                    # Extract text (Simplified for PDF)
                    from langchain_community.document_loaders import PyPDFLoader
                    # We need a file path for PyPDFLoader usually, or use pypdf directly on bytes
                    # For simplicity, let's write decrypted to temp again
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_decrypt:
                        tmp_decrypt.write(decrypted_content)
                        decrypt_path = tmp_decrypt.name
                    
                    loader = PyPDFLoader(decrypt_path)
                    pages = loader.load()
                    full_text = "".join([p.page_content for p in pages])
                    
                    st.session_state.rag_engine.ingest_document(full_text, {"source": uploaded_file.name, "owner": st.session_state.username})
                    
                    # Cleanup temp decrypted
                    os.remove(decrypt_path)
                    
                    log_audit("UPLOAD", f"Uploaded and ingested {uploaded_file.name}", st.session_state.user_id)
                    st.success("Document processed securely!")

    with tab2:
        st.header("Legal Assistant Chat")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about your documents..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = st.session_state.rag_engine.query(prompt)
                answer = response['result']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                log_audit("QUERY", f"Query: {prompt}", st.session_state.user_id)

    with tab3:
        st.header("Audit Logs")
        if st.session_state.role == 'admin' or True: # Allow all for demo
            logs = st.session_state.db_session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50).all()
            for log in logs:
                st.text(f"{log.timestamp} - User {log.user_id} - {log.action}: {log.details}")

if __name__ == "__main__":
    if 'user_id' not in st.session_state:
        login_page()
    else:
        main_app()
