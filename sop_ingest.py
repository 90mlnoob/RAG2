# # sop_ingest.py
# from langchain_community.vectorstores import Qdrant
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain_community.document_loaders import DirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema import Document
# import re
# import os

# COLLECTION_NAME = "sops"
# sop_path = "sops/"
# LOCAL_QDRANT_PATH = "./local_qdrant"  # Folder where vector DB will be saved

# def ingest_sops():
#     # loader = DirectoryLoader(sop_path, glob="**/*.md")
#     # documents = loader.load()

#     # splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     # docs = splitter.split_documents(documents)

#     # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#     # vectorstore = Qdrant.from_documents(
#     #     documents=docs,
#     #     embedding=embeddings,
#     #     location=LOCAL_QDRANT_PATH,
#     #     collection_name=COLLECTION_NAME,
#     #     force_recreate=True,
#     # )

#     # print("✅ SOPs successfully ingested into local Qdrant DB.")

#     loader = DirectoryLoader(sop_path, glob="**/*.md")
#     documents = loader.load()

#     # Extract SOPs from the document (split by a header pattern like "SOP: ")
#     sop_texts = []
#     for doc in documents:
#         content = doc.page_content
        
#         # Define a regex pattern to match SOPs (assuming "SOP: " followed by the SOP title)
#         sop_pattern = r"(SOP: [^\n]+[\n]+)(.*?)(?=SOP: |$)"
        
#         # Find all SOPs
#         sop_matches = re.findall(sop_pattern, content, flags=re.DOTALL)
        
#         # Each SOP is extracted as a document
#         sop_texts.extend([match[1].strip() for match in sop_matches])

#     # Now we need to split large SOPs into chunks (if they exceed the chunk_size)
#     splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)

#     # Create Document objects for each SOP text
#     sop_documents = [Document(page_content=sop_text) for sop_text in sop_texts]
    
#     # Split each SOP into smaller chunks (if needed)
#     # return splitter.split_documents(sop_documents)
#     document = splitter.split_documents(sop_documents)

#     embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     print(":: ", document)
#     qdrant = Qdrant.from_documents(
#         document,
#         embedding=embedding,
#         path=LOCAL_QDRANT_PATH,
#         collection_name=COLLECTION_NAME  

#     )
#     print("::qdrant", qdrant)
#     return qdrant



# if __name__ == "__main__":
#     ingest_sops()
import os
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from langchain_core.documents import Document
from langchain.chains import RetrievalQA

from langchain_community.llms import Ollama

# === Step 1: Set up the embedding model ===
# embedding = HuggingFaceEmbeddings(
#     model_name="BAAI/bge-small-en-v1.5", 
#     encode_kwargs={"normalize_embeddings": True}
# )

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                   encode_kwargs={"normalize_embeddings": True})

# === Step 2: Load and chunk SOPs ===
sop_folder = "sops/"  # Directory containing your SOP .md files
docs = []

# Custom Splitter to ensure subsections remain within their parent section
class CustomMarkdownHeaderTextSplitter(MarkdownHeaderTextSplitter):
    def __init__(self, headers_to_split_on):
        super().__init__(headers_to_split_on)

    def split_text(self, text):
        chunks = []
        current_chunk = []
        current_section = None

        for line in text.split("\n"):
            if line.startswith("# "):  # Top-level section header
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                current_chunk = [line]  # Start a new chunk for a new section
                current_section = "section"
            elif line.startswith("## "):  # Subsection header
                if current_section == "section":
                    current_chunk.append(line)  # Add to the section's chunk
                else:
                    # This ensures the subsection is included under the parent section
                    current_chunk.append(line)  # Add to the current chunk of section
            else:
                current_chunk.append(line)  # Add regular content

        if current_chunk:
            chunks.append("\n".join(current_chunk))  # Add the last chunk

        return chunks


# Create the splitter with custom logic
splitter = CustomMarkdownHeaderTextSplitter(headers_to_split_on=[("#", "section"), ("##", "subsection")])



# splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "section"), ("##", "subsection")])

for filename in os.listdir(sop_folder):
    if filename.endswith(".md"):
        loader = TextLoader(os.path.join(sop_folder, filename),encoding='utf-8')
        markdown_text = loader.load()[0].page_content
        
        # Split SOP text into manageable chunks
        chunks = splitter.split_text(markdown_text)
        # print("\n\n\n chunk: ", chunks)
        # Add metadata to each chunk
        for chunk in chunks:  # chunks should be strings or already structured content
            doc = Document(
                page_content=chunk,
                metadata={
                    "filename": "all-sops.md",
                    "source": "All-Sops"
                }
            )
            docs.append(doc)

# === Step 3: Create local Qdrant client ===
print("docs: ",     docs)
qdrant = Qdrant.from_documents(
    documents=docs,
    embedding=embedding,
    location=":memory:",  # For in-memory DB, change to "./qdrant_data" for persistent storage
    collection_name="merchant_sops", 
    distance_func="cosine"
)

# Optional: Save to persistent DB if needed
# client = QdrantClient(path="./qdrant_data")
# qdrant = Qdrant.from_documents(
#     documents=docs,
#     embedding=embedding,
#     client=client,
#     collection_name="merchant_sops"
# )

# === Step 4: Set up a retriever ===
# retriever = qdrant.as_retriever(
#     search_type="mmr",  # MMR balances relevance and diversity
#     # search_kwargs={"k": 5}  # Top 5 relevant results
# )
retriever = qdrant.as_retriever()

llm = Ollama(model="llama3.2",
             num_ctx=4096,
             temperature=0,
             verbose=True)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# Example: Use retriever to get relevant documents for a query
query = "How to update recurring billing?"
relevant_docs = qa_chain({"query": query})
# relevant_docs = retriever.get_relevant_documents(query)

print("\n\n\nRelevantDocs: ", relevant_docs)
# Print the results to check
for i, doc in enumerate(relevant_docs):
    if not isinstance(doc, Document):
        print(f"❌ Item {i} is not a Document. It's a {type(doc)}: {repr(doc)[:100]}")
    else:
        print(f"\n✅ Source: {doc.metadata.get('source', 'N/A')}\n📄 Content: {doc.page_content}...")
