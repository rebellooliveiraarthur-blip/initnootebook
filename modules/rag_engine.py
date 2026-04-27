from modules.vector_engine import VectorEngine
from modules.llm_module import LLMEngine

class RAG:
    def __init__(self):
        self.vector_engine = VectorEngine()
        self.llm_engine = LLMEngine()

    def retrivial(self, question):
        # 1. Recuperação (Retrieval)
        chunks = self.vector_engine.search(question)
        
        return chunks

# Exemplo de uso:
# rag = RAG()
# print(rag.ask("Qual o faturamento do último trimestre?"))
