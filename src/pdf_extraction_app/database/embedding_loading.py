from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

def load_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return tokenizer, model

def generate_embedding(text, tokenizer, model):
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    embeddings = outputs.last_hidden_state.mean(dim=1)
    
    embedding = embeddings[0].numpy()
    embedding = embedding / np.linalg.norm(embedding)
    
    return embedding.tolist()
