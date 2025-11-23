import os
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    from langchain.chains import RetrievalQA
except ImportError:
    try:
        from langchain.chains.retrieval_qa.base import RetrievalQA
    except ImportError:
        # Fallback or error handling if RetrievalQA is moved elsewhere
        pass 

try:
    from langchain.prompts import PromptTemplate
except ImportError:
    from langchain_core.prompts import PromptTemplate

class RAGEngine:
    def __init__(self, model_name="llama3", persist_directory="./chroma_db"):
        self.llm = Ollama(model=model_name)
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.persist_directory = persist_directory
        self.vector_store = Chroma(persist_directory=persist_directory, embedding_function=self.embeddings)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def ingest_document(self, text, metadata):
        chunks = self.text_splitter.create_documents([text], metadatas=[metadata])
        self.vector_store.add_documents(chunks)
        self.vector_store.persist()

    def query(self, question):
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(),
            return_source_documents=True
        )
        return qa_chain({"query": question})

    def analyze_contract(self, contract_text):
        prompt = PromptTemplate(
            input_variables=["text"],
            template="Analyze the following contract clause and identify potential risks:\n\n{text}"
        )
        chain = prompt | self.llm
        return chain.invoke({"text": contract_text})
