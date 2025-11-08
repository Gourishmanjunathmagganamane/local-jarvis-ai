import streamlit as st
import os
import requests
from populate_database import load_documents, split_documents, add_to_chroma
from query_data import query_rag, CHROMA_PATH, DATA_PATH, OLLAMA_API 
# Note: CHROMA_PATH, DATA_PATH, OLLAMA_API are imported from query_data now

# --- Utility Functions ---

def check_ollama_health():
    """Checks if the Ollama API is reachable."""
    try:
        response = requests.get(f"{OLLAMA_API}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_db_status():
    """Returns the number of files and chunks in the database (simple count)."""
    try:
        # A simple way to estimate: check number of files in data/
        file_count = len([name for name in os.listdir(DATA_PATH) if not name.startswith('.')])
        
        # A rough estimate of chunks (if chroma folder exists)
        if os.path.exists(CHROMA_PATH):
             # Cannot easily count chunks without initializing Chroma, so we'll just check for folder existence
             return file_count, "Indexed"
        return file_count, "Empty/Needs Indexing"
    except Exception:
        return 0, "Error"


# --- Streamlit Setup & Configuration ---

st.set_page_config(page_title="Jarvis AI", page_icon="🤖", layout="wide")
st.title("🤖 Your Local Jarvis AI")
st.caption("A private, offline RAG assistant built with Ollama, LangChain, and ChromaDB.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Ensure data folder exists
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# --- Sidebar Control Panel ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Status Check
    ollama_up = check_ollama_health()
    db_files, db_status_text = get_db_status()
    st.markdown(f"**Ollama Status:** {'🟢 Running' if ollama_up else '🔴 Offline'}")
    st.markdown(f"**Data Folder:** {db_files} files")
    st.markdown(f"**DB Status:** {db_status_text}")
    st.markdown("---")


    st.subheader("🧠 RAG Settings")
    
    # 1. Model Selection
    selected_model = st.selectbox(
        "Select LLM Model",
        options=["mistral", "llama3"],
        index=0,
        help="Make sure the model is pulled via Ollama (e.g., 'ollama pull mistral')."
    )

    # 2. RAG Parameter Tuning
    k_chunks = st.slider(
        "Context Chunks (k)",
        min_value=3, max_value=10, value=5, step=1,
        help="Number of relevant text chunks retrieved from the database to answer your question."
    )
    st.markdown("---")
    
    # 3. Knowledge Base Upload/Rebuild
    st.subheader("📂 Manage Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload Notes (PDF, DOCX, TXT, etc.)",
        accept_multiple_files=True,
        type=["pdf", "txt", "docx", "csv", "md"]
    )

    if uploaded_files:
        st.info("Processing files...")
        
        # Upload files to data folder
        for uploaded_file in uploaded_files:
            file_path = os.path.join(DATA_PATH, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            st.success(f"✅ Uploaded: {uploaded_file.name}")

        # Process and update database with progress bar
        try:
            with st.spinner("🧠 Updating the database..."):
                docs = load_documents()
                st.caption(f"Loaded {len(docs)} pages.")
                chunks = split_documents(docs)
                st.caption(f"Created {len(chunks)} chunks.")
                add_to_chroma(chunks)
            
            st.success("✅ Database updated successfully!")
            st.experimental_rerun() # Refresh to update DB status
        except Exception as e:
            st.error(f"⚠️ Error while updating database: {e}")

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state["messages"] = []
        st.experimental_rerun()


# --- Main Chat Interface ---

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask Jarvis a question here..."):
    
    if not ollama_up:
        st.error("🔴 Ollama is not running. Please start the service (e.g., `ollama serve`) before asking a question.")
        st.stop()
        
    # 1. Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Display assistant response (Streaming)
    with st.chat_message("assistant"):
        with st.spinner("🤖 Jarvis is thinking..."):
            
            try:
                # Call the generator function with user-selected parameters
                response_generator = query_rag(
                    prompt, 
                    k=k_chunks, 
                    model_name=selected_model
                )
                
                # Stream the response and capture the full output
                full_response = st.write_stream(response_generator)
                
                # Check for SOURCES in the full response (appended by the generator)
                if "SOURCES:" in full_response:
                    # Append the final full response to session state
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    # Handle error message or context-not-found message
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
            except Exception as e:
                error_message = f"⚠️ Something went wrong during generation: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})