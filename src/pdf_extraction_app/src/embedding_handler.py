from sentence_transformers import SentenceTransformer
import numpy as np
from .pdf_handler import PDFHandler
from typing import Dict, List

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding(text: str) -> List[float]:
    """
    Create an embedding for a given text with the appropriate size.
    
    Args:
        text (str): The input text to generate an embedding for.
        
    Returns:
        List[float]: The embedding vector for the input text.
    """
    try:
        return model.encode(text).tolist()
    except Exception as e:
        print(f"An error occurred while creating the embedding: {e}")
        return []
    
def chunk_and_embed(text: str, chunk_size: int = 384) -> List[List[float]]:
    """
    Break the text into chunks and generate embeddings for each chunk.
    
    Args:
        text (str): The input text to be chunked and embedded.
        chunk_size (int): The size of each chunk. Default is 384.
        
    Returns:
        List[List[float]]: A list of embeddings for each chunk.
    """
    try:
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        embeddings = [model.encode(chunk) for chunk in chunks]
        return embeddings
    except Exception as e:
        print(f"An error occurred while chunking and embedding: {e}")
        return []

def generate_embeddings(text_data: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, List[float]]]:
    """
    Generate embeddings for the text data using a Hugging Face sentence transformer model.
    
    Args:
        text_data (Dict[str, Dict[str, str]]): A dictionary containing structured text data.
        
    Returns:
        Dict[str, Dict[str, List[float]]]: A dictionary containing the embeddings for each section.
    """
    try:
        embeddings = {}
        
        for section_id, content in text_data.items():
            embeddings[section_id] = {}
            
            title_embedding = model.encode(content['title'])
            embeddings[section_id]["title"] = title_embedding.tolist()
            
            text = content['text']
            
            chunk_size = 384
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
            # Embed each chunk
            for i, chunk in enumerate(chunks):
                chunk_embedding = model.encode(chunk)
                embeddings[section_id][f"chunk_{i+1}"] = {}
                embeddings[section_id][f"chunk_{i+1}"]["text"] = chunk
                embeddings[section_id][f"chunk_{i+1}"]["embedding"] = chunk_embedding.tolist()
        
        return embeddings
        
    except Exception as e:
        print(f"An error occurred while generating embeddings: {e}")
        return None

if __name__ == "__main__":
    path = "/home/pedro/Documents/Rag_test/grpc/papers_pdf/ScienceDirect/Arcaini2020.pdf"
    
    doc = PDFHandler.try_open(path)

    text, _ = PDFHandler.tagged_extraction(doc, "bold")
    # print("Extracted Text:", text)

    metadata = PDFHandler.get_metadata(doc)
    # print("Metadata:", metadata)

    regex_pattern = r"\n(\d)\.\s+(?!\d)[\w\s]+<--bold-->\n"

    extracted_text = PDFHandler.extract_text_with_regex(text, regex_pattern)

    print(generate_embeddings(extracted_text))

    doc.close()
