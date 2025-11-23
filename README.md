# Secure Local Legal RAG System

## 📜 Overview
The **Secure Local Legal RAG System** is a privacy-first, AI-powered assistant designed for legal professionals to analyze, query, and manage sensitive documents entirely offline. Built with a focus on data sovereignty, it leverages **Local LLMs (Ollama)** and **Retrieval-Augmented Generation (RAG)** to provide accurate answers from your own PDF contracts and legal texts without ever sending data to the cloud.

The application features a modern, **Perplexity-inspired UI** with a dual-state interface (Clean Landing Page -> Deep Chat), robust audit logging, and military-grade encryption for stored documents.

---

## 🛠️ Tech Stack & Tools

### Core Frameworks
*   **[Streamlit](https://streamlit.io/)**: The frontend framework used to build the interactive web application.
*   **[LangChain](https://www.langchain.com/)**: The orchestration framework for RAG, managing the flow between the LLM, vector store, and document loaders.
*   **[Ollama](https://ollama.com/)**: The local LLM runner. We use the **Llama 3** model for high-quality, offline inference.

### Data & Storage
*   **[ChromaDB](https://www.trychroma.com/)**: The local vector database used to store document embeddings for semantic search.
*   **[SQLAlchemy](https://www.sqlalchemy.org/)** & **SQLite**: Manages relational data including User Accounts, Document Metadata, and Audit Logs.
*   **[Cryptography](https://pypi.org/project/cryptography/)**: Handles AES encryption for documents at rest (Fernet symmetric encryption).

### Key Libraries
*   `pypdf`: For robust PDF text extraction.
*   `sentence-transformers`: For generating local embeddings (`all-MiniLM-L6-v2`) that run efficiently on CPU/GPU.
*   `bcrypt`: For secure password hashing.

---

## ✨ Key Features

1.  **🔒 Privacy-First Architecture**:
    *   **Local Inference**: All AI processing happens on your machine via Ollama.
    *   **Encryption at Rest**: Uploaded PDFs are encrypted immediately upon receipt. They are only decrypted in memory during processing or download.
    *   **Role-Based Access**: Secure login system with user isolation.

2.  **🧠 Advanced RAG Engine**:
    *   **Context-Aware**: Retrieves precise chunks of legal text to answer queries.
    *   **Source Citations**: (Optional) Can track exactly which document and page an answer came from.

3.  **🎨 Modern UI/UX**:
    *   **Perplexity-Style Landing**: A clean, centered "What can I help you with today?" interface for starting new sessions.
    *   **Seamless Transition**: Automatically switches to a chat history view once the conversation begins.
    *   **Integrated Tools**: Sidebar document management and audit logs.

4.  **📝 Comprehensive Audit Logging**:
    *   Tracks every action: Logins, Uploads, Queries, and Deletions.
    *   Admins can review who asked what and when, ensuring compliance.

---

## 🏗️ Architecture & Workarounds

### 1. Dual-State UI Logic
To achieve the "Perplexity" look in Streamlit (which is typically a top-down script), we implemented a state-machine approach in `app.py`:
*   **Landing State**: Checks if `st.session_state.messages` is empty. If so, renders a custom HTML/CSS container centered on the page.
*   **Chat State**: Once a message exists, the standard `st.chat_message` layout takes over.

### 2. Custom CSS Injection
Streamlit's native styling is limited. We use `st.markdown(..., unsafe_allow_html=True)` to inject robust CSS for:
*   **Hiding Default Elements**: Removing the default top padding and input decorations.
*   **Centering Content**: Using Flexbox (`display: flex`) to vertically center the landing page components.
*   **Upload Button Positioning**: (Previously) We used aggressive CSS selectors (`:first-of-type`, `!important`) to force elements into specific positions, though the current version uses a cleaner Sidebar approach.

### 3. Local Vector Store Persistence
ChromaDB is configured to persist data to the `./chroma_db` directory. This ensures that embeddings survive application restarts, so you don't have to re-index your legal library every time.

---

## 🚀 Installation & Setup

### Prerequisites
1.  **Python 3.10+** installed.
2.  **[Ollama](https://ollama.com/)** installed and running.
3.  Pull the Llama 3 model:
    ```bash
    ollama pull llama3
    ```

### Steps
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/TejasRanjith/legal_rag_system.git
    cd legal_rag_system
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

4.  **Login**:
    *   Register a new user on the login screen.
    *   Start uploading documents!

---

## 📂 Project Structure

*   `app.py`: The main entry point and UI logic (Streamlit).
*   `rag_engine.py`: Handles the LLM interaction, embedding generation, and vector retrieval.
*   `database.py`: Defines the SQL schema (Users, Documents, AuditLogs).
*   `security.py`: Manages encryption, decryption, and password hashing.
*   `storage/`: (Created at runtime) Stores encrypted PDF files.
*   `chroma_db/`: (Created at runtime) Stores vector embeddings.

---

## ⚠️ Notes
*   **Performance**: The speed of responses depends heavily on your hardware (GPU recommended for Ollama).
*   **Security**: While files are encrypted, ensure the `secret.key` file is kept secure and backed up. Losing it means losing access to all uploaded documents.
