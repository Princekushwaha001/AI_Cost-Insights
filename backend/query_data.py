import os
import sys
import ollama
import requests
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
import time
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from backend.get_embedding_function import get_embedding_function

# CHROMA_PATH = "chroma"

CHROMA_PATH = os.path.join(project_root, "backend", "chroma")

# --- LLM provider configuration ---
# Supported providers: "perplexity" (Ollama disabled)
# Load environment variables from project root .env
load_dotenv(dotenv_path=os.path.join(project_root, ".env"))
# Hybrid provider selection with safe defaults
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "perplexity").lower()
PPLX_API_KEY = os.getenv("PPLX_API_KEY")
PPLX_MODEL = os.getenv("PPLX_MODEL", "sonar")
# Support either OLLAMA_MODEL or legacy ollama_model env var; default to 'mistral'
ollama_model = os.getenv("OLLAMA_MODEL") or os.getenv("ollama_model") or "mistral"
PROMPT_WITH_CONTEXT = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

FALLBACK_PROMPT = """
If the context cannot generate the answer, then go and fetch the details from your database and provide the final generated response .
{question}
"""

# Phrases that signal the LLM couldn't answer from the context
_NO_INFO_PHRASES = [
    "not mentioned in the provided context",
    "no mention of",
    "no relevant information",
    "cannot answer based on the provided context",
    "uncertain from the provided context",
    "based on the provided context",
]


def query_open_source_llm(prompt: str) -> str:
    """
    Route to the configured LLM provider.

    Providers:
    - perplexity: Uses Perplexity's OpenAI-compatible chat completions API
    - ollama:     Uses local Ollama generate()

    The prompt is treated as a single user message.
    """
    if LLM_PROVIDER == "perplexity":
        if not PPLX_API_KEY:
            raise RuntimeError("PPLX_API_KEY not set but LLM_PROVIDER=perplexity")
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {PPLX_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": PPLX_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        # Basic validation to avoid accidental non-serializable entries
        assert isinstance(payload["messages"], list) and all(
            isinstance(m, dict) and "role" in m and "content" in m for m in payload["messages"]
        ), "Invalid messages payload for Perplexity API"
        t0 = time.perf_counter()
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        dt_s = (time.perf_counter() - t0)
        print(f"⏱️ LLM provider=perplexity model={PPLX_MODEL} time_s={dt_s:.3f}")
        return text

    if LLM_PROVIDER == "ollama":
        # Local Ollama branch
        t0 = time.perf_counter()
        result = ollama.generate(model=ollama_model, prompt=prompt)
        dt_s = (time.perf_counter() - t0)
        print(f"⏱️ LLM provider=ollama model={ollama_model} time_s={dt_s:.3f}")
        return result["response"]

    # Unknown provider
    raise RuntimeError(
        f"Unknown LLM_PROVIDER='{LLM_PROVIDER}'. Use 'perplexity' or 'ollama'."
    )


# def query_rag_with_fallback(query_text: str) -> str:
#     """
#     1) Embed + get top-5 from Chroma.
#     2) If zero hits, fallback immediately.
#     3) Otherwise, build context from ALL top-5 chunks and ask the LLM.
#     4) If the LLM says “no info” in context, do a pure-LLM fallback.
#     5) Else, return the context-based answer + those chunk IDs.
#     """
#     embed_fn = get_embedding_function()
#     db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embed_fn)
#
#     # 1) Top-5 with scores
#     results = db.similarity_search_with_score(query_text, k=5)
#
#     # If no results, fallback
#     if not results:
#         resp_fb = query_open_source_llm(FALLBACK_PROMPT.format(question=query_text))
#         return f"Response (LLM Fallback): {resp_fb}\nSources: None"
#
#     # 2) Build context from ALL top-5
#     context = "\n\n---\n\n".join(doc.page_content for doc, _ in results)
#
#     # 3) Ask the LLM with context
#     prompt_with_ctx = ChatPromptTemplate.from_template(PROMPT_WITH_CONTEXT).format(
#         context=context, question=query_text
#     )
#     resp_ctx = query_open_source_llm(prompt_with_ctx)
#
#     # 4) Check for “no info” in the context-based answer
#     lower = resp_ctx.lower()
#     if any(phrase in lower for phrase in _NO_INFO_PHRASES):
#         # True fallback
#         resp_fb = query_open_source_llm(FALLBACK_PROMPT.format(question=query_text))
#         return f"Response (LLM Fallback): {resp_fb}\nSources: None"
#
#     # 5) Success: return the context answer and the chunk IDs
#     src_ids = [doc.metadata.get("id") for doc, _ in results]
#     return f"Response: {resp_ctx}\nSources: {src_ids}"

def query_rag_with_fallback(query_text: str) -> tuple[str, str]:
    """
    Returns:
        tuple: (response_text, source_type)
               source_type: "rag" or "fallback"
    """
    embed_fn = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embed_fn)

    # Step 1: Top-5 search similarity_search_with_score module of Chroma library
    results = db.similarity_search_with_score(query_text, k=5)

    # Step 2: No results → fallback
    if not results:
        resp_fb = query_open_source_llm(FALLBACK_PROMPT.format(question=query_text))
        return f"Response (LLM Fallback): {resp_fb}\nSources: None", "fallback"

    # Step 3: Build context from results
    context = "\n\n---\n\n".join(doc.page_content for doc, _ in results)
    prompt_with_ctx = ChatPromptTemplate.from_template(PROMPT_WITH_CONTEXT).format(
        context=context, question=query_text
    )
    resp_ctx = query_open_source_llm(prompt_with_ctx)

    # Step 4: If answer says "no info", fallback again
    if any(phrase in resp_ctx.lower() for phrase in _NO_INFO_PHRASES):
        resp_fb = query_open_source_llm(FALLBACK_PROMPT.format(question=query_text))
        return f"Response (LLM Fallback): {resp_fb}\nSources: None", "fallback"

    # Step 5: Return RAG answer
    src_ids = [doc.metadata.get("id") for doc, _ in results]
    return f"Response: {resp_ctx}\nSources: {src_ids}", "rag"


if __name__ == "__main__":
    # CLI convenience
    q = input("Enter your query: ").strip()
    ans = query_rag_with_fallback(q)
    print(ans)


