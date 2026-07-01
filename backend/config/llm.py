from langchain_openai import (
    ChatOpenAI
)

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7
)

def get_llm():
    return llm