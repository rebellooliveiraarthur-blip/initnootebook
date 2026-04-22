from langchain_ollama import OllamaEmbeddings

class PreProcessor():
    def __init__(self):
        # Aqui você define o segundo modelo (Embedding)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")

    def forward(self, user_message, db_name):
        # A lógica aqui deve usar self.embeddings para buscar no seu banco (ex: FAISS, Chroma)
        # O Ollama manterá o 'nomic-embed-text' e o 'smollm2' carregados juntos
        pass
