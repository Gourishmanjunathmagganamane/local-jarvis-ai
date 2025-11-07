import streamlit as st
import requests
import json
import time
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings

# ============= BASIC CONFIG ====================
OLLAMA_API = "http://localhost:11434/api/generate"
CHROMA_PATH = "chroma"
MODEL = "mistral"

# ============= PAGE SETTINGS ====================
st.set_page_config(page_title="Local Jarvis AI", page_icon="🤖", layout="centered")

st.title("🤖 Your Local Jarvis AI")
st.caption("Running fully offline using Ollama + LangChain + Chroma")

# ============= LOAD DATABASE ====================
with st.spinner("🧠 Loading knowledge base..."):
    embedding_fn = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_fn)
st.success("✅ Database loaded successfully!")

# ============= CHAT UI ====================
user_input = st.text_input("Ask Jarvis anything about your PDFs...")

if user_input:
    with st.spinner("🔍 Retrieving context..."):
        results = db.similarity_search_with_score(user_input, k=3)
        print(f"🧩 Retrieved {len(results)} results from Chroma for: {user_input}")
        for doc, score in results:
            print(f"Source: {doc.metadata.get('source')} (score={score})")

    if len(results) == 0:
        st.warning("⚠️ No relevant context found in the database.")
    else:
        context = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
        prompt = f"Answer the question based only on the following context:\n\n{context}\n\nQuestion: {user_input}"

        st.info("💭 Thinking... please wait, Jarvis is generating your answer...")
        msg_placeholder = st.empty()

        payload = {"model": MODEL, "prompt": prompt, "stream": True}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(OLLAMA_API, headers=headers, json=payload, stream=True, timeout=300)
            full_reply = ""

            # --- STREAM FIX ---
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("response", "")
                        full_reply += token
                        msg_placeholder.markdown(full_reply + "▌")
                        time.sleep(0.02)
                    except json.JSONDecodeError:
                        continue

            msg_placeholder.markdown(full_reply)

            # --- Show Sources ---
            sources = [doc.metadata.get("source", "unknown") for doc, _ in results]
            st.markdown("**📚 Sources used:**")
            for src in sources:
                st.write("- " + src)

        except Exception as e:
            st.error(f"⚠️ Error while communicating with Ollama: {e}")
