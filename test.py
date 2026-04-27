import ollama
import re
from core.shared import Bus
from modules.llm_module import LLMEngine

if __name__ == "__main__":
    # 1. Instancia o motor (isso já faz o subscribe via __init__)
    engine = LLMEngine()

    # 2. Cria um receptor para ver a saída
    @Bus.subscribe("output")
    def mostrar_resultado(sender, Content=None, **kwargs):
        print(f"\n[SAÍDA DO SISTEMA]: {Content['content']}")

    # 3. Dispara o pedido
    Bus.publish("LLM_Request", sender="User", prompt="hello")
