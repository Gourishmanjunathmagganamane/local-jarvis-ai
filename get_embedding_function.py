# get_embedding_function.py
import os
from langchain_community.embeddings.ollama import OllamaEmbeddings
# from langchain_community.embeddings.bedrock import BedrockEmbeddings
# In get_embedding_function.py
from langchain_ollama import OllamaEmbeddings

def get_embedding_function():
    """
    Returns an embeddings object. By default this uses Ollama local embeddings
    (nomic-embed-text). To use AWS Bedrock, swap implementation below.
    """
    use_bedrock = os.getenv("USE_BEDROCK", "false").lower() == "true"

    if use_bedrock:
        # If you want Bedrock, uncomment import above and configure credentials.
        # return BedrockEmbeddings(credentials_profile_name="default", region_name="us-east-1")
        raise RuntimeError("Bedrock mode requested but not configured.")
    else:
        # Local embeddings via Ollama (make sure you've pulled the model: ollama pull nomic-embed-text)
        return OllamaEmbeddings(model="nomic-embed-text")