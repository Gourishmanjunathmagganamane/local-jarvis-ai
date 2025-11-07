<h1 align="center">🤖 Local Jarvis AI</h1>

<p align="center">
  <b>💬 Your Offline, Privacy-First AI Assistant</b><br>
  Built with <a href="https://ollama.ai" target="_blank">Ollama</a> 🦙 | <a href="https://www.langchain.com" target="_blank">LangChain</a> 🧠 | <a href="https://streamlit.io" target="_blank">Streamlit</a> ⚡
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?logo=python" />
  <img src="https://img.shields.io/badge/LLM-Mistral%7CLLaMA3-green?logo=openai" />
  <img src="https://img.shields.io/badge/Database-ChromaDB-purple?logo=databricks" />
  <img src="https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit" />
  <img src="https://img.shields.io/badge/Status-Offline%20AI-success?logo=github" />
</p>

---

## 🧠 Overview

**Local Jarvis AI** is an **offline RAG-based assistant** that can read your PDFs, learn from them, and answer questions instantly.  
All processing happens **locally** using **Ollama**, **LangChain**, and **ChromaDB** — keeping your data private and secure.

> ⚙️ Think ChatGPT — but completely offline and personalized to your own study material.

---

## 🎯 Features

✅ Runs **fully offline** (no API key or internet needed)  
📄 Upload **PDF / TXT / DOCX** notes  
🧩 Uses **Retrieval Augmented Generation (RAG)**  
⚡ Answers powered by **Mistral / LLaMA 3**  
💬 Interactive **Streamlit chat interface**  
📚 Shows **sources** for every answer  
💾 Embeddings stored locally via **Chroma Vector DB**

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-------------|
| 🧠 LLM | Ollama (Mistral / LLaMA 3) |
| 📚 Framework | LangChain (Community + Core) |
| 💾 Vector DB | Chroma |
| 🎨 Frontend | Streamlit |
| 🐍 Language | Python 3.12+ |

---

## 📁 Project Structure
## 📁 Project Structure

| File / Folder | Description |
|-------------------------------|----------------------------------------------|
| `app_streamlit.py` | Streamlit UI (frontend) |
| `query_data.py` | RAG query logic |
| `populate_database.py` | Loads and embeds PDFs into Chroma |
| `get_embedding_function.py` | Embedding setup (Ollama / LangChain) |
| `test_rag.py` | Unit testing and validation |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |
| `data/` | Folder containing your PDFs |
| `chroma/` | Auto-generated vector database |


yaml
Copy code

---

## ⚙️ Installation

### 1️⃣ Install Ollama

Download 👉 [https://ollama.com/download](https://ollama.com/download)

Verify:
```bash
ollama --version
Start Ollama in background:

bash
Copy code
ollama serve
2️⃣ Pull required models
bash
Copy code
ollama pull mistral
ollama pull nomic-embed-text
ollama pull llama3
Check installed models:

bash
Copy code
ollama list
✅ Example Output:

makefile
Copy code
mistral:latest
nomic-embed-text:latest
llama3:latest
3️⃣ Set up environment
If using Miniconda:

bash
Copy code
conda create -n jarvis python=3.12 -y
conda activate jarvis
Then install dependencies:

bash
Copy code
pip install -r requirements.txt
If no requirements file:

bash
Copy code
pip install streamlit langchain-core langchain-community langchain-chroma chromadb pypdf sentence-transformers pytest boto3
4️⃣ Add your notes or study PDFs
Place all your PDFs in the data/ folder:

kotlin
Copy code
data/
 ├── Data Structures and Algorithms.pdf
 ├── Networking Basics.pdf
 ├── Software Engineering.pdf
 └── Cloud Computing.pdf
🧩 Build Knowledge Base
Run:

bash
Copy code
python populate_database.py --reset
Expected output:

pgsql
Copy code
✨ Clearing Database
👉 Adding new documents: 169
✅ Database updated and persisted successfully!
💬 Query from Terminal
Ask directly:

bash
Copy code
python query_data.py "What are the phases of SDLC?"
Example output:

markdown
Copy code
The phases of SDLC are:
1. Requirement Analysis
2. Design
3. Implementation
4. Testing
5. Deployment
6. Maintenance
🖥️ Launch Streamlit Chat UI
Run:

bash
Copy code
streamlit run app_streamlit.py
Then open the URL displayed:
👉 http://localhost:8501

Ask questions like:

pgsql
Copy code
What is cloud computing?
Difference between array and linked list?
🧠 How It Works (RAG Flow)
1️⃣ PDFs are read and split into small chunks
2️⃣ Chunks are embedded using nomic-embed-text
3️⃣ Stored in Chroma Vector DB
4️⃣ When you ask something → Top matching chunks are retrieved
5️⃣ Mistral generates a detailed answer using that context
6️⃣ Streamlit shows the response + sources

<p align="center"> <img src="https://github.com/microsoft/LLM-RAG-demo/raw/main/docs/rag-diagram.png" width="650"> </p>
⚡ Common Issues & Fixes
Issue	Fix
❌ AttributeError: 'Chroma' object has no attribute 'persist'	Use from langchain_chroma import Chroma and db._client.persist()
❌ Import 'langchain.schema' could not be resolved	Use from langchain_core.documents import Document
❌ JSONDecodeError in Streamlit	Add stream=True and handle multi-line JSON output

🧪 Testing
Run automated RAG tests:

bash
Copy code
pytest test_rag.py
🧱 Future Enhancements
 Add DOCX and TXT support

 Typing animation (ChatGPT style)

 Microphone input & text-to-speech

 Dockerize for one-click setup

 Add dark/light theme toggle in Streamlit

🔐 Privacy
🛡️ 100% local processing
🧠 Your data never leaves your machine
☁️ No cloud APIs or online storage used

👨‍💻 Author
Gourish M.
🎓 MCA Student @ Kristu Jayanti College
💡 Passionate about AI, Data, and Cloud
🌐 GitHub

🏁 Quick Reference
Command	Description
ollama serve	Start Ollama backend
ollama list	Check local models
python populate_database.py --reset	Rebuild vector DB
python query_data.py "<question>"	Query directly
streamlit run app_streamlit.py	Launch UI

<p align="center"> <b>🚀 Local Jarvis AI — Your Personal Offline Knowledge Assistant</b><br> <i>“Because your data deserves privacy.”</i> </p> ```
✅ Steps for you:
Copy everything above.

Open VS Code → local-jarvis-ai/README.md

Paste → Save.

Commit and push to GitHub:

bash
Copy code
git add README.md
git commit -m "Added rich README for Local Jarvis AI"
git push
