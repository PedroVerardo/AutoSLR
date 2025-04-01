import re

import nltk

class ChunkText:
    def __init__(self, text):
        self.text = text
    
    def fixed_window_splitter(text: str, chunk_size: int) -> list[str]:
        splits = []
        for i in range(0, len(text), chunk_size):
            splits.append(text[i:i + chunk_size])
        return splits
    
    def fixed_window_splitter_with_overlap(self, chunk_size: int, overlap_size: int) -> list[str]:
        splits = []
        for i in range(0, len(self.text), chunk_size - overlap_size):
            splits.append(self.text[i:i + chunk_size])
        return splits
    
    def token_splitter(self, max_token: int = 512) -> list[str]:
        tokens = nltk.word_tokenize(self.text)
        splits = []
        for i in range(0, len(tokens), max_token):
            splits.append(tokens[i:i + max_token])
        return splits
    
    def regex_splitter(self, regex: str,  max_size: int = 330) -> list[str]:
        splits = []
        split_ini = re.split(regex, self.text)
        for split in split_ini:
            if split != '' and len(split) < max_size:
                splits.append(split)
        
        
        return splits
    
    def regex_splitter_with_overlap(self, regex: str, overlap_size: int, max_size: int = 660) -> list[str]:
        splits = []
        split_ini = re.split(regex, self.text)
        print(split_ini)
        for i in range(0, len(split_ini), overlap_size):
            splited_text = split_ini[i:i + overlap_size]
            print(sum(len(part) for part in splited_text))
            if splited_text != '' and  sum(len(part) for part in splited_text) < max_size:
                combined_text = " ".join(splited_text).strip()
                splits.append(combined_text)

        return splits


if __name__ == "__main__":
    text = "This is a sample text for chunking. We will split this text into chunks."
    chunk_text = ChunkText(text)
    result = chunk_text.fixed_window_splitter_with_overlap(10, 5)
    print(result)
        

