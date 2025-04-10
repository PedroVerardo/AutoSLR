class EmbeddingModelConfig:
    def __init__(self, name: str, embedding_size: int):
        self.name = name
        self.embedding_size = embedding_size

    def __repr__(self):
        return f"EmbeddingModelConfig(name='{self.name}', embedding_size={self.embedding_size})"


if __name__ == "__main__":
    config = EmbeddingModelConfig(name="all-MiniLM-L6-v2", embedding_size=384)
    print(config)