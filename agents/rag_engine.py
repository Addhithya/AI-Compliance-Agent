from chromadb import PersistentClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from nomic import embed

def fetch_relevant_regulations(text):
    client = PersistentClient(path="chroma_db")
    collection = client.get_collection(name="compliance-laws")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(text)

    query_embeddings = embed.text(
        texts=chunks,
        model='nomic-embed-text-v1',
        task_type='search_document'
    )['embeddings']

    regulation_chunks = []
    for emb in query_embeddings:
        results = collection.query(query_embeddings=[emb], n_results=3)
        for doc in results['documents'][0]:
            regulation_chunks.append(doc)

    return "\n\n".join(set(regulation_chunks))
