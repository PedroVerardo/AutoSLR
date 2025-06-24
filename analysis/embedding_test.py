from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import google.generativeai as genai
import json
import sqlite3
from gensim.downloader import load
import pandas as pd
from dotenv import load_dotenv
import os




def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def most_similar_word2vec(input_text: str, candidates: list[str]) -> str:
    model = load("word2vec-google-news-300")
    def vectorize(text):
        tokens = [t for t in text.lower().split() if t in model]
        if not tokens:
            return np.zeros(300)
        return np.mean([model[t] for t in tokens], axis=0)

    input_vec = vectorize(input_text)
    sims = [cosine_similarity(input_vec, vectorize(c)) for c in candidates]
    return candidates[np.argmax(sims)]

def most_similar_bert(input_text: str, candidates: list[str]) -> str:
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")
    def embed(text):
        tokens = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            output = model(**tokens)
        return output.last_hidden_state[:, 0, :].squeeze().numpy()  # CLS
    input_vec = embed(input_text)
    sims = [cosine_similarity(input_vec, embed(c)) for c in candidates]
    return candidates[np.argmax(sims)]

def most_similar_sbert(input_text: str, candidates: list[str]) -> str:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([input_text] + candidates)
    input_vec, candidate_vecs = embeddings[0], embeddings[1:]
    sims = [cosine_similarity(input_vec, c) for c in candidate_vecs]
    return candidates[np.argmax(sims)]


def most_similar_scibert(input_text: str, candidates: list[str]) -> str:
    tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
    model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
    def embed(text):
        tokens = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            output = model(**tokens)
        return output.last_hidden_state[:, 0, :].squeeze().numpy()
    input_vec = embed(input_text)
    sims = [cosine_similarity(input_vec, embed(c)) for c in candidates]
    return candidates[np.argmax(sims)]


def most_similar_gemini(input_text: str, candidates: list[str], api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash-002")

    # Construct the prompt clearly
    # Instruct Gemini to return only the number of the best option.
    prompt = f"""Given the following text: "{input_text}"

Which of the following phrases is most similar or equivalent to the given text? Please respond with ONLY the number corresponding to the best option, no additional text or explanation.

Options:
"""
    # Add the candidates with their numbers
    prompt += "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))

    try:
        # Generate content with a clear instruction
        response = model.generate_content(prompt)
        
        # Clean the response and try to convert to an integer
        response_text = response.text.strip()
        
        # We can add some basic validation here for robustness
        if response_text.isdigit():
            idx = int(response_text) - 1
            if 0 <= idx < len(candidates): # Ensure the index is within bounds
                return candidates[idx]
            else:
                return "Erro: O índice retornado pelo Gemini está fora dos limites."
        else:
            # If it's not just a digit, try to extract a digit if present, or return error
            import re
            match = re.search(r'\d+', response_text) # Look for any digit sequence
            if match:
                idx = int(match.group(0)) - 1
                if 0 <= idx < len(candidates):
                    return candidates[idx]
                else:
                    return "Erro: O Gemini retornou um número, mas está fora dos limites."
            else:
                return f"Erro: O Gemini não retornou um número válido. Resposta crua: '{response_text}'"

    except Exception as e:
        # Catch more specific exceptions if needed, but a general one is okay for now
        return f"Erro ao comunicar com o Gemini ou processar resposta: {e}"
    

def read_sqlite_db(db_path: str, name: str) -> pd.DataFrame:
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pdfs WHERE pdf_name = ?", (name + ".pdf",))
    pdf_id_row = cursor.fetchone()
    pdf_id = pdf_id_row[0]
    df = pd.read_sql_query(f"SELECT section_number, section_title FROM extracted_text WHERE pdf_id = {pdf_id}", conn)
    conn.close()
    return df

if __name__ == "__main__":
    input_texts = ["Introduction", "Methodology"]

    load_dotenv("/home/pramos/Documents/AutoSLR/validations/regex_validation/.env")
    

    with open('/home/pramos/Documents/AutoSLR/analysis/topic_finding_template.json', 'r') as f:
        topic_answare = json.load(f)
    
    df_ref = pd.read_csv("/home/pramos/Documents/AutoSLR/analysis/test_df.csv")
    ref_list = df_ref['reference'].tolist()

    for ref in ref_list:
        print(f"Processing reference: {ref}")
        df = read_sqlite_db("/home/pramos/Documents/AutoSLR/validations/regex_validation/results/extern_llm-gemini.db", ref)
        for input_text in input_texts:
            print(f"Input text: {input_text}")
            candidates = df['section_title'].tolist()
            print("Candidates:", candidates)

            # Word2Vec
            result_w2v = most_similar_word2vec(input_text, candidates)
            print(f"Word2Vec {input_text} Result:", result_w2v)

            # BERT
            result_bert = most_similar_bert(input_text, candidates)
            print(f"BERT {input_text} Result:", result_bert)

            # SBERT
            result_sbert = most_similar_sbert(input_text, candidates)
            print(f"SBERT {input_text} Result:", result_sbert)

            # SciBERT
            result_scibert = most_similar_scibert(input_text, candidates)
            print(f"SciBERT {input_text} Result:", result_scibert)

            # Gemini
            result_gemini = most_similar_gemini(input_text, candidates, os.getenv("GEMINI_API"))
            print(f"Gemini {input_text} Result:", result_gemini)
    