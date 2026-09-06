from code_loader import load_codebase
#from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

from github_loader import clone_repo
from llm_utils import get_chat_model

load_dotenv()

print("I AM RUNNING THIS APP FILE")

repo_path = clone_repo(
    "https://github.com/k-shushh/TalentScout"
)

documents = load_codebase(repo_path)

print("REPO PATH:", repo_path)
print("DOCUMENT COUNT:", len(documents))

for doc in documents[:3]:
    print("------")
    print(doc.metadata)
    print(doc.page_content[:300])


embeddings = HuggingFaceEmbeddings()

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings
)

retriever = vectorstore.as_retriever()

llm = get_chat_model()
question = "How does the chatbot store candidate data?"

docs = retriever.invoke(question)

context = "\n\n".join(
    [doc.page_content for doc in docs]
)

prompt = f"""
Answer the question using the context below.

Context:
{context}

Question:
{question}
"""

response = llm.invoke(prompt)

print(response.content)
