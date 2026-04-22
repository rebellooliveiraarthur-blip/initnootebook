from typing import List
from langchain.messages import AIMessage, SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class LLMEngine:
    def __init__(self):
        self.model = ChatOllama(model="smollm2:135m", temperature=0)
        
        # System message
        system_template = """You are a helpful AI assistant named Init. You are bilingual (English and Portuguese).
Your task is to answer questions using the provided context. If you cannot find the answer in the context, say that you don't have that information.

Guidelines:
- Be concise and direct
- Use the context provided to answer
- Respond in the same language as the question"""
        
        # Human message template with context and conversation history
        human_template = """PREVIOUS MESSAGES:
{messages_str}

CONTEXT:
{context}

USER QUESTION: {question}

Please answer the question based on the context above."""
        
        self.system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        self.human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        self.prompt_template = ChatPromptTemplate.from_messages([
            self.system_prompt,
            self.human_prompt
        ])

    def generate(self, question, context_chunks, messages_str=""):
        context_text = "\n\n".join([doc.page_content for doc in context_chunks]) if context_chunks else "No context available."
        
        chain = self.prompt_template | self.model
        result = chain.invoke({
            "messages_str": messages_str or "No previous messages.",
            "context": context_text,
            "question": question
        })
        
        return result








