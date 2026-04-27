from services.file_processor import FileProcessor
from core.shared import (
    EVENT_PROCESS_FILE,
    EVENT_SAVE_KNOWLEDGE,
    EVENT_LOAD_HISTORY,
    EVENT_VECTOR_SEARCH,
    EVENT_PREPARE_CONTEXT,
)

class PreprocessorRAGModule:
    def __init__(self, bus):
        self.bus = bus
        self.file_processor = FileProcessor()

        bus.subscribe(EVENT_PROCESS_FILE, self.handle_process_file)
        bus.subscribe(EVENT_PREPARE_CONTEXT, self.handle_prepare_context)

    def handle_process_file(self, payload):
        uploaded_file = payload.get("uploaded_file")
        file_bytes = payload.get("file_bytes")
        section = payload.get("section")

        if uploaded_file is None or file_bytes is None:
            return {"status": "error", "error": "File data missing."}

        try:
            extracted_text = self.file_processor.process(uploaded_file, file_bytes)
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

        self.bus.publish(EVENT_SAVE_KNOWLEDGE, {
            "text": extracted_text,
            "metadata": {"filename": uploaded_file.name},
            "section": section,
        })

        return {
            "status": "success",
            "filename": uploaded_file.name,
            "text": extracted_text,
        }

    def handle_prepare_context(self, payload):
        question = payload.get("question")
        section = payload.get("section")
        top_k = payload.get("top_k", 3)

        if question is None or section is None:
            return None

        messages = self.bus.request(EVENT_LOAD_HISTORY, {"section": section}) or []
        context_chunks = self.bus.request(
            EVENT_VECTOR_SEARCH,
            {"query": question, "section": section, "top_k": top_k},
        ) or []

        messages_str = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in messages
        ])

        return {
            "question": question,
            "context_chunks": context_chunks,
            "messages_str": messages_str,
        }
