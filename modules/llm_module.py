import ollama
import re
from core.shared import Bus

class ResponseParser:
    def parse(self, response):
        # Regex melhorado para capturar a string exata do match e evitar erros no re.sub
        action_pattern = r'#ACTION:\s*(\w+)\(([^)]*)\)'
        tool_calls = []
        clean_response = response

        matches = re.finditer(action_pattern, response)
        for match in matches:
            full_match_str = match.group(0)
            tool_name = match.group(1)
            params_str = match.group(2)

            params = {}
            if params_str.strip():
                param_pairs = params_str.split(',')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        params[key.strip()] = value.strip().strip('"').strip("'")
            
            tool_calls.append({'tool_name': tool_name, 'params': params})
            clean_response = clean_response.replace(full_match_str, "").strip()

        return tool_calls, clean_response

class LLMEngine:
    def __init__(self, model_name="smollm2:135m", temperature=0):
        self.model_name = model_name
        self.temperature = temperature
        self.response_parser = ResponseParser()
        
        # Em vez de usar o decorador @Bus.subscribe no método, 
        # usamos o connect aqui para vincular o 'self' corretamente.
        Bus.connect("LLM_Request", self.LLM_Request)

    # O Blinker sempre envia o 'sender' primeiro, seguido pelos kwargs (prompt)
    def LLM_Request(self, sender, prompt=None, **kwargs):
        if not prompt:
            return

        print(f"[LLM Engine] Processando: {prompt}")
        
        # Correção no acesso aos dados do Ollama
        response_obj = ollama.chat(
            model=self.model_name, 
            messages=[{"role": "user", "content": prompt}], 
            options={"temperature": self.temperature}
        )
        raw_text = response_obj['message']['content']
        
        tool_calls, clean_response = self.response_parser.parse(raw_text)

        if clean_response:
            self.handle_response(clean_response)
        
        if tool_calls:
            for tool_call in tool_calls:
                self.handle_tool_call(tool_call)

    def handle_tool_call(self, tool_call):
        payload = {
            "Header": {
                "sender": "LLMModule",
                "event_type": "LLM_TOOL_CALL"
            },
            "Content": {
                "content": tool_call,
                "wait_return": True
            }
        }
        # Sender é obrigatório no seu Bus.publish
        Bus.publish("output", sender="LLMEngine", **payload)

    def handle_response(self, response):
        payload = {
            "Header": {
                "sender": "LLMModule",
                "event_type": "LLM_RESPONSE"
            },
            "Content": {
                "content": response,
                "wait_return": False
            }
        }
        Bus.publish("output", sender="LLMEngine", **payload)

