🤖 Local Jarvis AI — Offline RAG Chat Assistant

A fully offline AI-powered document assistant built using
🧠 Ollama (Mistral + Embedding Model),
📚 LangChain + Chroma, and
🎨 Streamlit for an interactive chat interface.

This project lets you upload your own PDF notes or documents and then ask natural language questions.
The AI finds relevant context from your local files and responds intelligently — no internet or API key required.

🚀 Features

🔒 100% Offline (uses local Ollama models)

📄 Upload and query your own PDFs

🧩 Uses Retrieval Augmented Generation (RAG) for contextual answers

🧠 Embeddings stored locally in Chroma vector database

💬 Interactive web interface using Streamlit

⚙️ Built modularly with modern LangChain ecosystem

🧱 Works with Mistral or LLaMA 3 models

🧰 Tech Stack
Component	Purpose
Python 3.12+	Core programming language
Ollama	Local LLM hosting (Mistral / LLaMA 3 / Nomic Embed)
LangChain Community	Document loading, text splitting, and RAG logic
LangChain Core	Data structures and document schema
LangChain Chroma	Vector storage and retrieval
Streamlit	Frontend web app
ChromaDB	Local vector store for embeddings
📦 Folder Structure
local-jarvis-ai/
│
├── app_streamlit.py             # Main chat app (Streamlit UI)
├── query_data.py                # Core query pipeline for RAG
├── populate_database.py         # Loads and indexes PDFs into Chroma
├── get_embedding_function.py    # Sets up local Ollama embeddings
├── test_rag.py                  # Evaluation tests for QA
├── requirements.txt             # Project dependencies
│
├── data/                        # Folder containing user-uploaded PDFs
│   ├── Software Engineering.pdf
│   ├── Data Structures and Algorithms.pdf
│   ├── Networking Basics.pdf
│   └── Cloud Computing.pdf
│
├── chroma/                      # Vector database (auto-generated)
└── README.md                    # Project documentation

⚙️ Installation Guide
1️⃣ Install Ollama

Download from https://ollama.com/download

Then verify installation:

ollama --version


Start the Ollama server (if not running automatically):

ollama serve

2️⃣ Pull Required Models
ollama pull mistral
ollama pull nomic-embed-text
ollama pull llama3


Check available models:

ollama list


✅ Expected:

mistral:latest
nomic-embed-text:latest
llama3:latest

3️⃣ Set Up Python Environment

If using Miniconda:

conda create -n jarvis python=3.12 -y
conda activate jarvis


Then install dependencies:

pip install -r requirements.txt


If requirements.txt doesn’t exist, manually install:

pip install streamlit langchain-community langchain-core langchain-chroma chromadb pypdf sentence-transformers pytest boto3

🧠 Build Vector Database

Place your notes or PDFs in the data/ folder.

Then run:

python populate_database.py --reset


Expected output:

✨ Clearing Database
👉 Adding new documents: 169
✅ Database updated and persisted successfully!

💬 Query Your AI Locally

Try a direct question from your terminal:

python query_data.py "What are the phases of SDLC?"


Example output:

The phases of SDLC include:
1. Requirement Analysis
2. Design
3. Implementation
4. Testing
5. Deployment
6. Maintenance

🖥️ Run the Streamlit App

Start the web interface:

streamlit run app_streamlit.py


Expected terminal output:

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501


Now open the given local URL in your browser.

🗣️ Chat with Jarvis

Once open, you can:

Upload new PDFs

Ask questions like:

What is cloud computing?
Difference between array and linked list?


See responses appear in real-time

View sources used from your uploaded files

⚡ Common Fixes
❌ AttributeError: 'Chroma' object has no attribute 'persist'

→ Install and use updated langchain-chroma:

pip install -U langchain-chroma


and replace:

from langchain.vectorstores.chroma import Chroma


with:

from langchain_chroma import Chroma

❌ Import "langchain.schema" could not be resolved

→ Replace with:

from langchain_core.documents import Document

❌ JSONDecodeError in Streamlit

→ Ollama returns multiple JSON lines. Fix by reading in streaming mode or parsing only first valid JSON object.

🧪 Test Setup

Run validation tests for question-answer quality:

pytest test_rag.py

🔐 Privacy

All processing happens locally —
no data leaves your machine.
Ollama, LangChain, and Chroma run offline, making this a secure personal assistant setup.

💡 Future Improvements

Add support for DOCX, TXT uploads

Stream typing animations (like ChatGPT)

Include voice input/output

Dockerize the entire setup for one-click deployment

🧑‍💻 Author

Gourish M.
📘 MCA Student @ Kristu Jayanti College
💬 Interested in AI, Data Analysis, and Web Development

🏁 Quick Summary
Command	Purpose
ollama serve	Start Ollama server
ollama list	Check available models
python populate_database.py	Build vector DB from PDFs
python query_data.py "<question>"	Ask a question
streamlit run app_streamlit.py	Launch chat UI