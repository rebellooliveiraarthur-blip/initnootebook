from typing import List
from unittest import result

from langchain.messages import AIMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama

class OlamaEngine():
    def __init__(self, tools=None):
        self.llm = ChatOllama(
            model="qwen3-vl:2b-instruct",
            validate_model_on_init=True,
            temperature=0,
        ).bind_tools(tools or [])
    
    def forward(self, prompt):
        result = self.llm.invoke(prompt)
        return result







