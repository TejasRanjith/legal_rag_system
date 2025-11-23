try:
    print("Importing RAGEngine...")
    from rag_engine import RAGEngine
    print("RAGEngine imported.")
    engine = RAGEngine()
    print("RAGEngine initialized.")
except Exception as e:
    print(f"Error: {e}")
