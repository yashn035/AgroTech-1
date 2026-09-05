"""
AgroTech RAG Engine & AI Copilot Synthesizer
Provides document indexing, semantic vector retrieval (SentenceTransformers/TF-IDF),
and LLM response synthesis with graceful API & keyword fallbacks.
"""

import os
import re
import pandas as pd
import streamlit as st

import warnings

# Optional LLM integration
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    genai = None

# Optional SentenceTransformer vector embedding integration
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_ST = True
except ImportError:
    HAS_ST = False
    SentenceTransformer = None

AGRO_KNOWLEDGE_DOCS = [
    {
        "topic": "Banana Disease & Pest Management",
        "text": "For Banana Bract Mosaic Virus, apply Carbendazim 50% WP at 2 g/L. For Sigatoka Leaf Spot, apply Azoxystrobin 23% SC at 1 mL/L. For Panama Wilt, chemical treatment is ineffective; use Trichoderma viride soil drenching and resistant cultivars."
    },
    {
        "topic": "Cauliflower Black Rot & Downy Mildew",
        "text": "For Cauliflower Black Rot, use Streptocycline (0.1 g/L) + Copper Oxychloride (2 g/L). For Downy Mildew, apply Metalaxyl 8% + Mancozeb 64% WP at 2.5 g/L. Ensure seedbed solarization."
    },
    {
        "topic": "Chilli Anthracnose & Leaf Curl Virus",
        "text": "For Chilli Anthracnose, apply Azoxystrobin 18.2% + Difenoconazole 11.4% SC at 1 mL/L. For Leaf Curl Virus vector control, spray Imidacloprid 17.8% SL at 0.5 mL/L or Acetamiprid 20% SP for Whiteflies."
    },
    {
        "topic": "Groundnut & Radish Protection",
        "text": "For Groundnut Early/Late Leaf Spot, apply Carbendazim + Mancozeb at 2 g/L. For Radish Black Leaf Spot, spray Copper Oxychloride 50% WP at 2.5 g/L."
    },
    {
        "topic": "Soil NPK & Fertilization Advisory",
        "text": "Nitrogen promotes vegetative leaf growth (Urea 46% N). Phosphorus encourages root development and flowering (SSP 16% P2O5). Potassium enhances drought tolerance and pest resistance (MOP 60% K2O). Maintain soil pH between 6.0 and 7.5."
    },
    {
        "topic": "Irrigation & Extreme Weather Strategy",
        "text": "During heavy rainfall (>150mm), open field drainage channels to prevent root asphyxiation and damping off. During heat stress (>35°C), irrigate during early morning or late evening using drip systems to cut evaporation."
    },
    {
        "topic": "Mandi Market Prices & Selling Advisory",
        "text": "Check live daily prices on data.gov.in. Commodities like Onion, Potato, and Tomato exhibit high price volatility in Mandis. Store non-perishables in dry godowns when prices dip."
    },
    {
        "topic": "Tomato & Potato Blight Control",
        "text": "For Potato and Tomato Late Blight, apply Mancozeb 75% WP at 2 g/L or Chlorothalonil 75% WP at 2 g/L. Ensure proper crop rotation and avoid overhead sprinkling."
    }
]

@st.cache_data(show_spinner=False)
def load_rag_knowledge_base() -> list:
    """
    Assembles the complete agricultural knowledge base by merging CSV database mappings 
    and static agronomic advisories.
    
    Returns:
        list: List of dictionaries with 'topic' and 'text' keys.
    """
    kb = list(AGRO_KNOWLEDGE_DOCS)
    
    # Load pesticide mapping CSV if available
    csv_path = os.path.join("data", "model_class_to_pesticide_mapping.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, keep_default_na=False)
            for idx, row in df.iterrows():
                lbl = str(row.get("Model_Label", ""))
                status = str(row.get("Match_Status", ""))
                disease = str(row.get("Matched_Disease_in_DB", ""))
                product = str(row.get("Best_Product", ""))
                dose = str(row.get("Formulation_dose", ""))
                dilution = str(row.get("Dilution_in_water", ""))
                
                kb.append({
                    "topic": f"Pesticide Rule for {lbl}",
                    "text": f"Crop Label: {lbl} | Status: {status} | Disease: {disease} | Product: {product} | Dose: {dose} | Water Dilution: {dilution}"
                })
        except Exception:
            pass
            
    return kb

@st.cache_resource(show_spinner=False)
def load_embedding_model():
    """
    Loads and caches sentence-transformers model if installed.
    Returns None if package is unavailable.
    """
    if HAS_ST:
        try:
            return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        except Exception:
            return None
    return None

def retrieve_context_chunks(query_text: str, top_k: int = 3) -> list:
    """
    Retrieves the top-k relevant knowledge chunks using SentenceTransformers if available,
    falling back to keyword term overlap.
    
    Args:
        query_text (str): Farmer user prompt.
        top_k (int): Number of chunks to retrieve.
        
    Returns:
        list: List of retrieved document dicts.
    """
    kb = load_rag_knowledge_base()
    embedder = load_embedding_model()
    
    if embedder is not None:
        try:
            corpus_texts = [d["text"] for d in kb]
            corpus_embeddings = embedder.encode(corpus_texts, convert_to_tensor=True)
            query_embedding = embedder.encode(query_text, convert_to_tensor=True)
            
            # Compute cosine similarity
            from sentence_transformers import util
            hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)[0]
            retrieved = [kb[hit['corpus_id']] for hit in hits]
            if retrieved:
                return retrieved
        except Exception:
            pass
            
    # Fallback: Term Overlap Matching
    query_words = set(re.findall(r'\w+', query_text.lower()))
    scored_docs = []
    for doc in kb:
        doc_words = set(re.findall(r'\w+', doc["text"].lower()))
        overlap = len(query_words.intersection(doc_words))
        scored_docs.append((overlap, doc))
        
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    retrieved = [doc for score, doc in scored_docs[:top_k] if score > 0]
    
    if not retrieved:
        retrieved = [kb[0], kb[4]]  # Default fallback chunks
        
    return retrieved

def query_rag_copilot(query_text: str, top_k: int = 3) -> dict:
    """
    Queries the RAG engine and generates a response.
    Tries Gemini API if GEMINI_API_KEY is set, otherwise generates structured rule-based advisory.
    
    Args:
        query_text (str): Farmer prompt query.
        top_k (int): Number of context chunks.
        
    Returns:
        dict: Containing 'answer' (str) and 'sources' (list).
    """
    retrieved_docs = retrieve_context_chunks(query_text, top_k=top_k)
    sources = [f"**{d['topic']}**: {d['text']}" for d in retrieved_docs]
    
    # Check for Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if HAS_GEMINI and api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            context_str = "\n".join([f"- {d['topic']}: {d['text']}" for d in retrieved_docs])
            prompt = f"""You are AgroCopilot, an expert AI agricultural assistant helping farmers in India.
Use the following retrieved context to answer the user's question accurately, concisely, and in simple farmer-friendly bullet points.

Retrieved Context:
{context_str}

User Question: {query_text}

Provide clear, actionable recommendations:"""
            
            response = model.generate_content(prompt)
            if response and response.text:
                return {
                    "answer": response.text.strip(),
                    "sources": sources
                }
        except Exception:
            pass # Fall through to structured rule synthesis
            
    # Rule-Based Synthesis Fallback
    answer_parts = []
    answer_parts.append(f"🤖 **AgroCopilot Knowledge Synthesis:**\n\nBased on your query *'{query_text}'*, here are the verified recommendations from our agricultural database:\n")
    
    for idx, doc in enumerate(retrieved_docs, start=1):
        answer_parts.append(f"**{idx}. {doc['topic']}**\n{doc['text']}")
        
    answer_parts.append("\n💡 **Farmer Tip:** Always verify chemical dosages with local Krishi Vigyan Kendra (KVK) officers before field application.")
    
    full_answer = "\n\n".join(answer_parts)
    return {
        "answer": full_answer,
        "sources": sources
    }
