# config.py

# Esta variável guarda o nome do banco que está "ativo" no momento
CURRENT_DB_NAME = None

def set_active_database(db_name):
    """Define o banco de dados ativo pelo nome"""
    global CURRENT_DB_NAME
    CURRENT_DB_NAME = db_name

def get_db_name():
    """Retorna o nome do banco de dados ativo"""
    if CURRENT_DB_NAME is None:
        raise Exception("Nenhum banco de dados foi selecionado!")
    return CURRENT_DB_NAME
