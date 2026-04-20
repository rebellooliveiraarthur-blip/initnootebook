import subprocess
import sys
import subprocess
import time
import os

def iniciar_ollama():
    """Tenta subir o servidor Ollama localmente."""
    print("Iniciando o serviço Ollama...")
    try:
        # Abre o processo em segundo plano (background)
        # O 'ollama serve' inicia o servidor local
        processo = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguarda alguns segundos para o servidor subir totalmente
        time.sleep(10)
        print("Servidor Ollama iniciado com sucesso.")
        return processo
    except FileNotFoundError:
        print("Erro: Ollama não encontrado. Verifique se está instalado no PATH.")
        return None

# Iniciar o servidor Ollama
processo_ollama = iniciar_ollama()

# Run the Streamlit app
subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py"]) 

