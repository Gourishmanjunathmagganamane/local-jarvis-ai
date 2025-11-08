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
        file_count = len([name for name in os.listdir(DATA_PATH) if not name.startswith('.')])
        if os.path.exists(CHROMA_PATH):
             return file_count, "Indexed"
        return file_count, "Empty/Needs Indexing"
    except Exception:
        return 0, "Error"

def local_css(file_name):
    """Loads custom CSS from a local file and injects it into the Streamlit page."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ CSS file '{file_name}' not found. UI styling may be default.")


# --- Streamlit Setup & Configuration ---

st.set_page_config(page_title="Jarvis AI", page_icon="🤖", layout="wide")

# Inject Custom CSS for the hacker/robot vibe (MUST be called first)
local_css("style.css") 

# --- J.A.R.V.I.S. Header Layout ---
col_logo, col_title, col_status = st.columns([1, 4, 2])

# Col 1: Stylized Logo/Icon
col_logo.markdown(
    """
    <div style='text-align:center; font-size: 40px; color: #00FF41; line-height: 1.2;'>
        ◆
    </div>
    """, unsafe_allow_html=True
)
# Col 2: Main Title
col_title.markdown(
    "## Local Jarvis AI <sub>(Offline RAG System)</sub>", 
    unsafe_allow_html=True
)

# Col 3: Dynamic Status Dashboard
ollama_up = check_ollama_health()
db_files, db_status_text = get_db_status()
status_icon = '🟢' if ollama_up else '🔴'
# Use the status-box class for vertical alignment
col_status.markdown(
    f"<div class='status-box'>**OLLAMA:** {status_icon}<br>DB: {db_status_text}</div>", 
    unsafe_allow_html=True
)
st.markdown("---") # Visual separator

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Ensure data folder exists
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# --- Sidebar Control Panel ---
# Use st.container() for better control over blocks
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.markdown("---") 

    # RAG Settings Container
    with st.container(border=False):
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

    st.markdown("---") # Separator between RAG and Knowledge Base
    
    # Knowledge Base Container
    with st.container(border=False):
        st.subheader("📂 Manage Knowledge Base")
        uploaded_files = st.file_uploader(
            "Upload Notes (PDF, DOCX, TXT, etc.)",
            accept_multiple_files=True,
            type=["pdf", "txt", "docx", "csv", "md"]
        )

        if uploaded_files:
            st.info("Processing files...")
            
            for uploaded_file in uploaded_files:
                file_path = os.path.join(DATA_PATH, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                st.success(f"✅ Uploaded: {uploaded_file.name}")

            try:
                with st.spinner("🧠 Updating the database..."):
                    docs = load_documents()
                    st.caption(f"Loaded {len(docs)} pages.")
                    chunks = split_documents(docs)
                    st.caption(f"Created {len(chunks)} chunks.")
                    add_to_chroma(chunks)
                
                st.success("✅ Database updated successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"⚠️ Error while updating database: {e}")

    # Use a blank element to push the "Clear Chat" button to the bottom
    st.empty()
    st.markdown("<br><br>", unsafe_allow_html=True) # Add some final space

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
if prompt := st.chat_input("Enter Command or Query..."):
    
    if not ollama_up:
        st.error("🔴 Ollama is not running. Please start the service (e.g., `ollama serve`) before asking a question.")
        st.stop()
        
    # 1. Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Display assistant response (Streaming)
    with st.chat_message("assistant"):
        with st.spinner("🤖 Jarvis is processing..."):
            
            try:
                response_generator = query_rag(
                    prompt, 
                    k=k_chunks, 
                    model_name=selected_model
                )
                
                full_response = st.write_stream(response_generator)
                
                # Check for SOURCES and append final response to history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
            except Exception as e:
                error_message = f"⚠️ System Error during generation: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})