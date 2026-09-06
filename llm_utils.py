import os

from langchain_groq import ChatGroq


DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"


def get_chat_model():
    model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip()
    return ChatGroq(model=model)
