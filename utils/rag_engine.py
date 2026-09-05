import os
import re
import pandas as pd
import streamlit as st

AGRO_KNOWLEDGE_DOCS = [
    {
        "topic": "Banana Disease Treatment",
        "text": "For Banana Bract Mosaic Virus, apply Carbendazim 50% WP at 2 g/L. For Sigatoka Leaf Spot, apply Azoxystrobin 23% SC at 1 mL/L. For Panama Wilt, chemical treatment is ineffective; use Trichoderma viride soil drenching and resistant cultivars."
    },
    {
        "topic": "Cauliflower Pest & Rot Care",
        "text": "For Cauliflower Black Rot, use Streptocycline (0.1 g/L) + Copper Oxychloride (2 g/L). For Downy Mildew, apply Metalaxyl 8% + Mancozeb 64% WP at 2.5 g/L. Ensure seedbed solarization."
    },
    {
        "topic": "Chilli Disease Management",
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
        "topic": "Irrigation & Weather Water Management",
        "text": "During heavy rainfall (>150mm), open field drainage channels to prevent root asphyxiation and damping off. During heat stress (>35°C), irrigate during early morning or late evening using drip systems to cut evaporation."
    },
    {
        "topic": "Mandi Prices & Marketing Strategy",
        "text": "Check live daily prices on data.gov.in. Commodities like Onion and Potato exhibit high price volatility in Maharashtra and UP mandis. Store non-perishables in dry godowns when prices dip."
    }
]

@st.cache_data(show_spinner=False)
def load_rag_knowledge_base():
    """
    Assembles complete knowledge base from CSVs and static advisories.
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
                    "text": f"Label: {lbl} | Status: {status} | Disease: {disease} | Product: {product} | Dose: {dose} | Dilution: {dilution}"
                })
        except Exception:
            pass
            
    return kb

def query_rag_copilot(query_text: str, top_k: int = 3) -> dict:
    """
    Retrieves top relevant knowledge chunks and synthesizes copilot response.
    
    Args:
        query_text (str): Farmer prompt query.
        top_k (int): Number of top chunks to retrieve.
        
    Returns:
        dict: Answer string and list of source citations.
    """
    kb = load_rag_knowledge_base()
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
        
    sources = [f"**{d['topic']}**: {d['text']}" for d in retrieved]
    
    # Synthesize answer
    answer_parts = []
    answer_parts.append(f"🤖 **AgroCopilot Advisory:**\nBased on your query *'{query_text}'*, here is the recommended guidance:\n")
    
    for idx, doc in enumerate(retrieved, start=1):
        answer_parts.append(f"{idx}. **{doc['topic']}**: {doc['text']}")
        
    answer_parts.append("\n💡 *Always verify specific chemical applications with your local KVK or agricultural extension office.*")
    
    full_answer = "\n\n".join(answer_parts)
    return {
        "answer": full_answer,
        "sources": sources
    }
