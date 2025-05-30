import os
import fitz  # PyMuPDF
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from sentence_transformers import SentenceTransformer
# import chromadb
# from chromadb.config import Settings
from chromadb import PersistentClient
from nomic import embed

# import os
# os.environ["NOMIC_API_KEY"] = "Your_api_key"

def extract_text_from_pdfs(folder_path):
    all_texts = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            doc = fitz.open(os.path.join(folder_path, file))
            text = ""
            for page in doc:
                text += page.get_text()
            all_texts.append((file, text))
    return all_texts

def chunk_text(text, chunk_size=300, overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)

def get_embeddings(texts):
    response = embed.text(
        texts=texts,
        model='nomic-embed-text-v1',
        task_type='search_document'
    )
    return response['embeddings']

def store_in_chroma(docs, embeddings, ids, collection_name="compliance-laws"):
    chroma_client = PersistentClient(path="chroma_db")
    collection = chroma_client.get_or_create_collection(name=collection_name)
    collection.add(documents=docs, embeddings=embeddings, ids=ids)
    # chroma_client.persist()
    print(f"Stored {len(docs)} chunks into Chroma collection '{collection_name}'")

if __name__ == "__main__":
    folder_path = "laws"
    raw_docs = extract_text_from_pdfs(folder_path)

    all_chunks = []
    all_ids = []
    for filename, text in tqdm(raw_docs):
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
        all_ids.extend([f"{filename}_{i}" for i in range(len(chunks))])

    embeddings = get_embeddings(all_chunks)
    store_in_chroma(all_chunks, embeddings, all_ids)
