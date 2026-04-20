from services.pre_processor import PreProcessor
import config

class RAG():
    def __init__(self):
        self.pre_processor = PreProcessor()
        self.db_name = config.get_db_name()
    
    def forward(self, user_message):
        relevant_chunks = self.pre_processor.forward(user_message, self.db_name)
        context = " ".join(relevant_chunks)

        context = f""" 
        Use the informations below to answer the question. 
        If the answer is not in the text, say you don't know.
        
        CONTEXT:
        {context}
        USER QUESTION:
        {user_message}"""

        return context

