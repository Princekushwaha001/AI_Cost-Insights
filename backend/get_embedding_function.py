# backend/get_embedding_function.py
import os

# prefer Ollama when env var EMBEDDING_PROVIDER=ollama
PROVIDER = os.getenv("EMBEDDING_PROVIDER", "auto").lower()

def get_embedding_function():
    if PROVIDER in ("ollama", "auto"):
        try:
            from langchain_ollama import OllamaEmbeddings
            return OllamaEmbeddings(model="nomic-embed-text")
        except Exception:
            # fallback to sentence-transformers below
            pass

    # fallback: sentence-transformers via LangChain-compatible wrapper
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        class STWrapper:
            def __init__(self, model_name="all-MiniLM-L6-v2"):
                self.model = SentenceTransformer(model_name)
            def embed_documents(self, texts):
                return [v.tolist() for v in self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)]
            def embed_query(self, text):
                return self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0].tolist()
        return STWrapper()
    except Exception as e:
        raise RuntimeError("No embedding provider available. Install `langchain-ollama` or `sentence-transformers`.") from e
