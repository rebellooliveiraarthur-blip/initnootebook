from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os

base_db_dir = os.path.join("database", "vector_storage")

class VectorEngine:
    def __init__(self, collection_name="meu_rag"):
        # Modelo específico para embeddings (rápido e leve)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.db = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=base_db_dir 
        )

    def search(self, query, k=3):
        # Retorna apenas os chunks mais relevantes
        return self.db.similarity_search(query, k=k)
