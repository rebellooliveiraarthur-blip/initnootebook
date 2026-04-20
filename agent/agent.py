from langchain_ollama import ChatOllama

from agent.tools import validate_user

from langchain.messages import AIMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2:1b", 
    validate_model_on_init=True,
    temperature=0,
).bind_tools([validate_user])


def get_response(question):
    
    result = llm.invoke(
        "Could you validate user 123? They previously lived at "
        "123 Fake St in Boston MA and 234 Pretend Boulevard in "
        "Houston TX."
    )
    return result




# tool calling ja ta funcionando, falta todo o resto agora👌