import sqlite3
import json
import os
import numpy as np

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_DIR, "database", "databases")
os.makedirs(DB_FOLDER, exist_ok=True)

def get_db_path_by_name(nome_buscado):
    """Padroniza o nome do arquivo e retorna o caminho completo."""
    # Remove .sqlite se o usuário tiver passado no nome, para não duplicar a extensão
    nome_limpo = nome_buscado.replace(".sqlite", "")
    nome_sanitizado = nome_limpo.replace(" ", "_").lower()
    return os.path.join(DB_FOLDER, f"{nome_sanitizado}.sqlite")

def create_database(database_name):
    """Cria o banco e as tabelas usando o caminho padronizado."""
    filename = get_db_path_by_name(database_name)
    
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    
    # Tabela de Histórico
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de Conhecimento
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_arquivo TEXT,
            conteudo_texto TEXT,
            vetor BLOB,
            metadata TEXT,
            data_upload DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    return filename

def save_file(db_name, nome_arquivo, texto, metadata=None):
    """Salva um fragmento de texto e seu vetor."""
    db_path = get_db_path_by_name(db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    vetor = gerar_vetor_ollama(texto)
    vetor_blob = np.array(vetor, dtype=np.float32).tobytes()
    metadata_json = json.dumps(metadata) if metadata else None

    cursor.execute("""
        INSERT INTO knowledge (nome_arquivo, conteudo_texto, vetor, metadata)
        VALUES (?, ?, ?, ?)
    """, (nome_arquivo, texto, vetor_blob, metadata_json))
    
    conn.commit()
    conn.close()
    print(f"Fragmento de '{nome_arquivo}' indexado com sucesso.")

def vector_search(db_name, query_text, top_k=3):
    db_path = get_db_path_by_name(db_name)
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Busca os vetores que já estão salvos como BLOB no banco
    cursor.execute("SELECT conteudo_texto, vetor, metadata FROM knowledge")
    rows = cursor.fetchall()
    
    if not rows:
        conn.close()
        return []

    # 2. Transforma o TEXTO da pergunta em VETOR usando o OLLAMA
    query_vector = gerar_vetor_ollama(query_text)
    if query_vector is None:
        conn.close()
        return []
    
    q_vec = np.array(query_vector, dtype=np.float32)
    norm_q = np.linalg.norm(q_vec)
    
    results = []
    for row in rows:
        # 3. Transforma o BLOB do banco de volta para um array numpy
        db_vec = np.frombuffer(row[1], dtype=np.float32)
        norm_db = np.linalg.norm(db_vec)
        
        # 4. Cálculo de similaridade (Cosseno) entre os dois vetores do Ollama
        if norm_q > 0 and norm_db > 0:
            score = np.dot(q_vec, db_vec) / (norm_q * norm_db)
        else:
            score = 0.0
            
        results.append({
            "content": row[0],
            "metadata": json.loads(row[2]) if row[2] else {},
            "score": float(score)
        })

    # Ordena pelo maior score e fecha conexão
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    conn.close()
    contexto_formatado = "\n".join([item["content"] for item in results[:top_k]])
    return contexto_formatado

def save_message(db_name, role, content):
    db_path = get_db_path_by_name(db_name)
    create_database(db_name) # Garante que existe
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO context (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def load_context(db_name):
    db_path = get_db_path_by_name(db_name)
    if not os.path.exists(db_path): return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp FROM context ORDER BY timestamp ASC")
    historico = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return historico

def list_databases():
    databases = []
    for file in os.listdir(os.path.join(BASE_DIR, "database", "databases")):
        if file.endswith(".sqlite"):
            databases.append(file)
    return databases

def gerar_vetor_ollama(texto):
    import requests
    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": "nomic-embed-text:v1.5",
        "prompt": texto
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        # Verifica se a chave 'embedding' existe na resposta
        if 'embedding' in data:
            return data['embedding']
        else:
            print(f"Erro do Ollama: {data.get('error', 'Resposta desconhecida')}")
            # Dica: Verifique se você deu 'ollama pull nomic-embed-text'
            return None
            
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

