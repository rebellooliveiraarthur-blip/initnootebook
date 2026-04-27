

from core.bus import EventBus
from core.shared import (
    EVENT_PROCESS_FILE,
    EVENT_SAVE_MESSAGE,
    EVENT_SAVE_KNOWLEDGE,
    EVENT_LOAD_HISTORY,
    EVENT_VECTOR_SEARCH,
    EVENT_PREPARE_CONTEXT,
    EVENT_GENERATE_ANSWER,
)
from database.database_manager import DatabaseManager
from modules.llm_module import LLMEngineModule
from modules.preprocessor_rag import PreprocessorRAGModule

class Orquestrador:
    def __init__(self, section="default"):
        self.section = section.replace(" ", "_").lower()
        self.bus = EventBus()
        self.db_manager = DatabaseManager(self.section)

        self.preprocessor_rag = PreprocessorRAGModule(self.bus)
        self.llm_module = LLMEngineModule(self.bus)
        self._register_database_handlers()

    def _register_database_handlers(self):
        self.bus.subscribe(EVENT_SAVE_MESSAGE, self._handle_save_message)
        self.bus.subscribe(EVENT_SAVE_KNOWLEDGE, self._handle_save_knowledge)
        self.bus.subscribe(EVENT_LOAD_HISTORY, self._handle_load_history)
        self.bus.subscribe(EVENT_VECTOR_SEARCH, self._handle_vector_search)

    def _handle_save_message(self, payload):
        role = payload.get("role")
        content = payload.get("content")
        if role and content:
            self.db_manager.save_message(role, content)

    def _handle_save_knowledge(self, payload):
        text = payload.get("text")
        metadata = payload.get("metadata")
        if text:
            self.db_manager.save_knowledge(text, metadata)

    def _handle_load_history(self, payload):
        return self.db_manager.load_history()

    def _handle_vector_search(self, payload):
        query = payload.get("query")
        top_k = payload.get("top_k", 3)
        if query is None:
            return []
        return self.db_manager.vector_search(query, top_k=top_k)

    def forward(self, user_message):
        self.bus.request(EVENT_SAVE_MESSAGE, {"role": "user", "content": user_message})

        context_payload = self.bus.request(EVENT_PREPARE_CONTEXT, {
            "question": user_message,
            "section": self.section,
            "top_k": 3,
        })

        if context_payload is None:
            return "Desculpe, não foi possível preparar o contexto."

        result = self.bus.request(EVENT_GENERATE_ANSWER, context_payload)

        if result:
            self.bus.request(EVENT_SAVE_MESSAGE, {"role": "assistant", "content": result})
            return result

        return "Desculpe, não foi possível gerar uma resposta."

    def upload_file(self, uploaded_file, file_bytes):
        result = self.bus.request(EVENT_PROCESS_FILE, {
            "uploaded_file": uploaded_file,
            "file_bytes": file_bytes,
            "section": self.section,
        })

        if result is None:
            return {"status": "error", "error": "Não foi possível processar o arquivo."}
        return result

if __name__ == "__main__":
    orquestrer = Orquestrador()
    response = orquestrer.forward("Qual o faturamento do último trimestre?")
    print(response)