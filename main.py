

class Orquestrador():
    def __init__(self, section="default"):
        from engines.rag_engine import RAG
        from engines.llm_engine import LLMEngine
        from engines.vector_engine import VectorEngine
        from database.database_manager import DatabaseManager

        self.rag = RAG()
        self.ollama = LLMEngine()
        self.vector_engine = VectorEngine()
        self.db_manager = DatabaseManager(section)

    def forward(self, user_message):
        self.db_manager.save_message("user", user_message)

        # Get context from knowledge base
        context_chunks = self.db_manager.vector_search(user_message)

        # Get history
        messages = self.db_manager.load_history()
        messages_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        result = self.ollama.generate(user_message, context_chunks, messages_str)
        if hasattr(result, 'content'):
            self.db_manager.save_message("assistant", result.content)
            return result.content
        return result
    
    def upload_file(self, uploaded_file, file_bytes):
        from services.file_processor import FileProcessor
        processor = FileProcessor()
        try:
            extracted_text = processor.process(uploaded_file, file_bytes)
            self.db_manager.save_knowledge(extracted_text, {"filename": uploaded_file.name})
            return { 
                "status": "success", 
                "filename": uploaded_file.name,
                "text": extracted_text
            }
        except Exception as e:
            return { "status": "error", "error": str(e) }

if __name__ == "__main__":
    orquestrer = Orquestrador()
    response = orquestrer.forward("Qual o faturamento do último trimestre?")
    print(response)