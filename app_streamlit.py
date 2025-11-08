import streamlit as st
import os
from populate_database import load_documents, split_documents, add_to_chroma
from query_data import query_rag

# Paths
DATA_PATH = "data"
CHROMA_PATH = "chroma"

# Streamlit Setup
st.set_page_config(page_title="Jarvis AI", page_icon="🤖", layout="wide")
st.title("🤖 Your Local Jarvis AI")
st.caption("Running fully offline using Ollama + LangChain + Chroma")

# Create data folder
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# -------------------------------------------------------------
# 📂 Upload Section
# -------------------------------------------------------------
st.subheader("📂 Upload new files to teach Jarvis")
uploaded_files = st.file_uploader(
    "Upload PDFs, DOCX, TXT, CSV, or Markdown files",
    accept_multiple_files=True,
    type=["pdf", "txt", "docx", "csv", "md"]
)

status_box = st.empty()

if uploaded_files:
    st.write("📥 Uploading your files...")
    for uploaded_file in uploaded_files:
        file_path = os.path.join(DATA_PATH, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"✅ Uploaded: {uploaded_file.name}")

    status_box.info("🧠 Processing and updating the database...")
    try:
        status_box.write("📄 Loading documents...")
        docs = load_documents()
        status_box.write(f"✅ Loaded {len(docs)} pages from uploaded files.")

        status_box.write("✂️ Splitting into chunks...")
        chunks = split_documents(docs)
        status_box.write(f"✅ Created {len(chunks)} chunks for embedding.")

        status_box.write("🧠 Adding embeddings to Chroma...")
        add_to_chroma(chunks)
        status_box.success("✅ Database updated successfully!")
    except Exception as e:
        st.error(f"⚠️ Error while updating database: {e}")

# -------------------------------------------------------------
# 💬 Chat Section
# -------------------------------------------------------------
st.subheader("💬 Ask Jarvis a Question")

query = st.text_input("Ask your question here:")
if st.button("Ask Jarvis"):
    if not query.strip():
        st.warning("Please enter a question first!")
    else:
        st.info("🤖 Thinking...")
        try:
            response = query_rag(query)
            response_clean = response.replace("Response:", "").strip()
            st.markdown(f"### 🧠 Jarvis says:\n\n{response_clean}")
        except Exception as e:
            st.error(f"⚠️ Something went wrong: {e}")
