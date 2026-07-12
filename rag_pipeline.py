from github_loader import clone_repo
from code_loader import load_codebase
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def create_vectorstore(repo_url):

    repo_path = clone_repo(repo_url)

    documents = load_codebase(repo_path)

    embeddings = HuggingFaceEmbeddings()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings
    )

    return vectorstore