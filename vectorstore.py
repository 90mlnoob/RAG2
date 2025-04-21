# vectorstore.py
from langchain_community.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings

COLLECTION_NAME = "sops"
LOCAL_QDRANT_PATH = "./local_qdrant"

def retrieve_relevant_sop(query: str) -> str:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = Qdrant.from_existing_collection(
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
        path=LOCAL_QDRANT_PATH
    )

    docs = vectorstore.similarity_search(query)
    return "\n---\n".join([doc.page_content for doc in docs])
