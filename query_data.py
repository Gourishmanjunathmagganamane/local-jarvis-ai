import os
import json
import requests
import argparse
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from get_embedding_function import get_embedding_function
# In query_data.py & populate_database.py
from langchain_chroma import Chroma


CHROMA_PATH = "chroma"
OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434")

PROMPT_TEMPLATE = """
Use the following CONTEXT (only these texts) to answer the QUESTION.
If the answer cannot be found in the context, say "I couldn't find this in the uploaded notes."

CONTEXT:
{context}

QUESTION:
{question}

Answer succinctly and add a SOURCES line listing chunk ids (if available).
"""

def query_rag(query_text: str, k: int = 5, model_name: str = "mistral"):
    embedding_fn = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_fn)

    results = db.similarity_search_with_score(query_text, k=k)
    if not results:
        return "⚠️ No relevant context found in the database."

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    prompt = PROMPT_TEMPLATE.format(context=context_text, question=query_text)

    # Call Ollama generation endpoint (stream-safe)
    url = f"{OLLAMA_API}/api/generate"
    payload = {"model": model_name, "prompt": prompt}

    try:
        resp = requests.post(url, json=payload, stream=True, timeout=180)
        full_response = ""
        # Ollama streams newline-delimited JSON objects; parse safely
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "response" in obj:
                    full_response += obj["response"]
            except json.JSONDecodeError:
                # skip non-json lines
                continue
        if not full_response:
            return "⚠️ Model returned no text."
        # prepare sources
        sources = [doc.metadata.get("id") for doc, _ in results]
        formatted = f"{full_response.strip()}\n\nSOURCES: {sources}"
        print(formatted)
        return full_response.strip()
    except Exception as e:
        return f"⚠️ Error calling Ollama: {e}"

# CLI usage
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--model", type=str, default="mistral")
    args = parser.parse_args()
    print(query_rag(args.query_text, k=args.k, model_name=args.model))
