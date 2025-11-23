try:
    import streamlit
    import langchain
    import chromadb
    import sqlalchemy
    import cryptography
    import bcrypt
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)

from database import init_db, User
try:
    Session = init_db()
    session = Session()
    print("Database initialized.")
    if not session.query(User).first():
        print("No users found (expected for fresh install).")
    session.close()
except Exception as e:
    print(f"Database initialization failed: {e}")
    exit(1)

print("Verification passed!")
