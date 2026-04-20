from database.database_manager import vector_search
import spacy

#nlp = spacy.load("pt_core_news_lg", disable=["ner", "parser", "attribute_ruler"])

class PreProcessor():
    def forward(self, last_user_message, database_name):
        relevant_chunks = vector_search(database_name, last_user_message, top_k=5)
        return relevant_chunks
    
"""
def split_into_chunks(text, window_size=3, overlap=1):
    # Divide o texto em linhas e remove linhas vazias
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    chunks = []
    i = 0
    while i < len(lines):
        # Pega o pedaço (janela) de 3 linhas
        chunk = lines[i : i + window_size]
        
        # Junta as linhas de volta em um texto único para o pedaço
        chunks.append("\n".join(chunk))
        
        # O pulo do gato: avança o índice mas subtrai o overlap
        # Se i era 0 e o tamanho 3, o próximo i seria 3. 
        # Com overlap 1, o próximo i será 2.
        i += (window_size - overlap)
        
        # Evita loops infinitos se o overlap for maior que a janela
        if window_size <= overlap:
            break
            
    return chunks

def compare_chunks_spacy(self, query_doc, chunk_text, threshold=0.7):
    chunk_doc = nlp(chunk_text)
    
    # 1. Pegamos apenas os radicais (lemmas) de substantivos e verbos
    # Ex: "cancelar" e "cancelamento" -> "cancelar"
    tokens_query = {t.lemma_.lower() for t in query_doc if t.pos_ in ('NOUN', 'VERB')}
    tokens_chunk = {t.lemma_.lower() for t in chunk_doc if t.pos_ in ('NOUN', 'VERB')}
    
    if not tokens_query: return False

    # 2. Calculamos a interseção (quantas palavras-chave batem)
    palavras_em_comum = tokens_query.intersection(tokens_chunk)
    
    # 3. Score baseado na proporção de palavras da pergunta encontradas no texto
    score = len(palavras_em_comum) / len(tokens_query)
    
    print(f"DEBUG: Score: {score:.2f} | Comum: {palavras_em_comum} | Texto: {chunk_text[:30]}...")
    
    return score >= threshold
"""
