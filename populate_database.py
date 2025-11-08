import argparse
import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
)

# Define constants
CHROMA_PATH = "chroma"
DATA_PATH = "data"

# ---------------------------------------------------------------------
# ✅ Universal Loader — Handles multiple file types
# ---------------------------------------------------------------------
def load_documents():
    documents = []
    for filename in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, filename)
        ext = filename.lower().split(".")[-1]

        try:
            if ext == "pdf":
                loader = PyPDFLoader(file_path)
            elif ext == "txt":
                loader = TextLoader(file_path, encoding="utf-8")
            elif ext in ["docx", "doc"]:
                loader = UnstructuredWordDocumentLoader(file_path)
            elif ext == "csv":
                loader = CSVLoader(file_path)
            elif ext == "md":
                loader = UnstructuredMarkdownLoader(file_path)
            else:
                print(f"⚠️ Skipping unsupported file type: {filename}")
                continue

            docs = loader.load()
            documents.extend(docs)
            print(f"✅ Loaded {filename}")

        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")

    return documents

# ---------------------------------------------------------------------
# ✅ Document splitting
# ---------------------------------------------------------------------
def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

# ---------------------------------------------------------------------
# ✅ Add chunks to Chroma vector store
# ---------------------------------------------------------------------
def add_to_chroma(chunks: list[Document]):
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Existing items in DB: {len(existing_ids)}")

    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        print("✅ Database updated successfully (auto-persisted by Chroma)!")
    else:
        print("✅ No new documents to add.")

# ---------------------------------------------------------------------
# ✅ Utility functions
# ---------------------------------------------------------------------
def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0
    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
        chunk.metadata["id"] = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
    return chunks

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print("🗑️ Database cleared!")

# ---------------------------------------------------------------------
# ✅ Main entry
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    print("📥 Loading documents...")
    documents = load_documents()

    print("✂️ Splitting into chunks...")
    chunks = split_documents(documents)

    print("🧠 Adding to Chroma...")
    add_to_chroma(chunks)

if __name__ == "__main__":
    main()
