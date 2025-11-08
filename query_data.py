import os
import json
import requests
import argparse
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma


CHROMA_PATH = "chroma"
DATA_PATH = "data"  # <-- ADD THIS LINE
OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434")

# query_data.py: Replace existing PROMPT_TEMPLATE
PROMPT_TEMPLATE = """
You are Jarvis, a helpful, friendly, and highly intelligent AI assistant designed to summarize private documentation.
Your goal is to provide a comprehensive, structured, and easy-to-read answer based ONLY on the CONTEXT provided below.

CONTEXT:
{context}

QUESTION:
{question}

---
INSTRUCTIONS FOR ANSWERING:
1.  **Adopt a helpful tone.** Answer the user directly and concisely.
2.  **Structure is Key:** Use **Markdown** (headings, bolding, bullet points) for clear organization.
3.  **Code Formatting:** Use code blocks (```...```) for technical examples or commands.
4.  **No Fabrications:** If the answer is not in the context, state: "I couldn't find this specific information in the uploaded notes."
5.  **Citations:** Do NOT include the sources line in your direct response.
"""

def query_rag(query_text: str, k: int = 5, model_name: str = "mistral"):
    embedding_fn = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_fn)

    results = db.similarity_search_with_score(query_text, k=k)
    if not results:
        # Instead of returning a string, we yield it
        yield "⚠️ No relevant context found in the database."
        return # End the generator

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    prompt = PROMPT_TEMPLATE.format(context=context_text, question=query_text)

    # Call Ollama generation endpoint (stream=True is critical)
    url = f"{OLLAMA_API}/api/generate"
    payload = {"model": model_name, "prompt": prompt}

    try:
        resp = requests.post(url, json=payload, stream=True, timeout=180)
        
        full_response = ""
        # Ollama streams newline-delimited JSON objects
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "response" in obj:
                    chunk = obj["response"]
                    full_response += chunk
                    yield chunk  # <<<< CRITICAL: YIELD the chunk for streaming
                
                # Check for the 'done' marker to append sources
                if obj.get("done", False):
                    # After the main response is done, yield the sources separately
                    sources = [doc.metadata.get("id") for doc, _ in results]
                    sources_text = f"\n\n---\n\n**Sources:** {sources}"
                    yield sources_text 
                    break # exit loop
            except json.JSONDecodeError:
                continue
    except Exception as e:
        yield f"⚠️ Error calling Ollama: {e}"

# CLI usage
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--model", type=str, default="mistral")
    args = parser.parse_args()
    print(query_rag(args.query_text, k=args.k, model_name=args.model))