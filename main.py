from services.rag_engine import RAG
from database.database_manager import create_database, load_context,list_databases, save_message, save_file, get_db_path_by_name
from services.ollama_engine import OlamaEngine
import streamlit as st
from services.file_processor import FileProcessor
import config

class Orquestrador():
    def __init__(self):
        self.rag = RAG()
        self.ollama = OlamaEngine()
    
    def forward(self, user_message):
        save_message(config.get_db_name(), "user", user_message)

        final_prompt = self.build_prompt(user_message)
        result = self.ollama.forward(final_prompt)
        if hasattr(result, 'content'):
            save_message(config.get_db_name(), "assistant", result.content)
            return result.content
        return result
        
    def build_prompt(self, user_message):
        previous_messages = load_context(config.get_db_name())
        context = self.rag.forward(user_message)
        
        messages_str = ""
        if previous_messages:
            for msg in previous_messages:
                messages_str += f"{msg['role']}: {msg['content']}\n"
        
        final_prompt = f"""{messages_str}you are a assistant named Init.
        Você é uma assistente virtual chamada Init. {context}"""
        
        return final_prompt
    
    def upload_file(self, uploaded_file, file_bytes):
        from services.file_processor import FileProcessor
        processor = FileProcessor()
        try:
            extracted_text = processor.process(uploaded_file, file_bytes)
            
            # Correção no banco de dados (passando o nome, não o path)
            save_file(config.get_db_name(), uploaded_file.name, extracted_text)
            
            # ADICIONE A CHAVE 'text' AQUI:
            return { 
                "status": "success", 
                "filename": uploaded_file.name,
                "text": extracted_text  # <--- Isso resolve o KeyError
            }
        except Exception as e:
            return { "status": "error", "error": str(e) }


    
    def list_databases(self):
        return list_databases()
    
    def set_database(self, db_name):
        config.set_active_database(db_name)
        return f"Database switched to {db_name}"


if __name__ == "__main__":
    create_database("test")
    config.set_active_database("test")
    a = Orquestrador()
    message = "o que precisa de piada de tio?"
    result = a.forward(message)
    print(result)


