import json
import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Caminhos base
BASE_DIR = "database"
VECTOR_FOLDER = os.path.join(BASE_DIR, "vector_storage")
JSON_FOLDER = os.path.join(BASE_DIR, "history_storage")

# Garante que as pastas existam
os.makedirs(VECTOR_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)

class DatabaseManager:
    def __init__(self, section_name):
        self.section_name = section_name.replace(" ", "_").lower()
        
        # Caminho do JSON específico desta seção
        self.json_path = os.path.join(JSON_FOLDER, f"{self.section_name}_history.json")
        
        # Inicializa o motor de Embeddings (Ollama)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Inicializa o Chroma para a coleção específica
        self.vector_db = Chroma(
            collection_name=self.section_name,
            embedding_function=self.embeddings,
            persist_directory=VECTOR_FOLDER
        )

    # --- GERENCIAMENTO DE SEÇÃO ---
    
    def delete_section(self):
        """Remove os vetores da coleção e o arquivo JSON de histórico."""
        # 1. Deleta a coleção no Chroma
        self.vector_db.delete_collection()
        
        # 2. Deleta o arquivo JSON de histórico
        if os.path.exists(self.json_path):
            os.remove(self.json_path)
        
        print(f"Seção '{self.section_name}' excluída com sucesso.")

    # --- LÓGICA DO HISTÓRICO (JSON INDIVIDUAL) ---

    def save_message(self, role, content):
        messages = self.load_history()
        messages.append({"role": role, "content": content})
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)

    def load_history(self):
        if not os.path.exists(self.json_path):
            return []
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # --- LÓGICA DO CONHECIMENTO (CHROMA) ---

    def save_knowledge(self, text, metadata=None):
        """Adiciona texto à base de conhecimento da seção."""
        self.vector_db.add_texts(texts=[text], metadatas=[metadata or {}])

    def vector_search(self, query, top_k=3):
        """Busca apenas dentro dos documentos desta seção."""
        results = self.vector_db.similarity_search(query, k=top_k)
        return results

# --- EXEMPLO DE USO ---
# rh = DatabaseManager("RH")
# rh.save_knowledge("O plano de saúde é Bradesco.", {"doc": "manual_rh.pdf"})
# rh.save_message("user", "Qual o plano de saúde?")
# print(rh.vector_search("plano de saúde"))
# rh.delete_section() # Limpa tudo do RH
