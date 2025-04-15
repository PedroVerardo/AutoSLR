import os
from typing import Dict, List, Optional, Union
from enum import Enum
import torch
from sentence_transformers import SentenceTransformer


class EmbeddingMethod(str, Enum):
    ALL_MINI_LM = "all-MiniLM-L6-v2"
    ALL_MPNET = "all-mpnet-base-v2"
    MULTI_QA_MPNET = "multi-qa-mpnet-base-dot-v1"
    MULTI_QA_MINI_LM = "multi-qa-MiniLM-L6-cos-v1"
    CUSTOM = "custom"


class PoolingStrategy(str, Enum):
    MEAN = "mean"
    MAX = "max"
    CLS = "cls"
    WEIGHTED_MEAN = "weighted_mean"


class EmbeddingConfig:
    
    DEFAULT_MODEL = EmbeddingMethod.ALL_MINI_LM
    
    CACHE_DIR = os.getenv('EMBEDDING_CACHE_DIR', '~/.cache/sentence_transformers')
    
    DEVICE = os.getenv('EMBEDDING_DEVICE', 'cuda' if torch.cuda.is_available() else 'cpu')
    
    POOLING_STRATEGY = os.getenv('EMBEDDING_POOLING', PoolingStrategy.MEAN)
    
    DEFAULT_DIMENSION = 384
    
    BATCH_SIZE = int(os.getenv('EMBEDDING_BATCH_SIZE', '32'))
    
    NORMALIZE_EMBEDDINGS = os.getenv('NORMALIZE_EMBEDDINGS', 'True').lower() == 'true'
    
    MODEL_DIMENSIONS: Dict[str, int] = {
        EmbeddingMethod.ALL_MINI_LM: 384,
        EmbeddingMethod.ALL_MPNET: 768,
        EmbeddingMethod.MULTI_QA_MPNET: 768,
        EmbeddingMethod.MULTI_QA_MINI_LM: 384,
    }
    
    MAX_SEQ_LENGTH = int(os.getenv('MAX_SEQ_LENGTH', '256'))
    
    @staticmethod
    def get_model_config(model_name: Optional[str] = None) -> Dict[str, Union[str, int, bool]]:
        model = model_name or EmbeddingConfig.DEFAULT_MODEL
        
        return {
            'model_name': model,
            'cache_dir': EmbeddingConfig.CACHE_DIR,
            'device': EmbeddingConfig.DEVICE,
            'pooling_strategy': EmbeddingConfig.POOLING_STRATEGY,
            'dimension': EmbeddingConfig.get_dimension_for_model(model),
            'batch_size': EmbeddingConfig.BATCH_SIZE,
            'normalize': EmbeddingConfig.NORMALIZE_EMBEDDINGS,
            'max_seq_length': EmbeddingConfig.MAX_SEQ_LENGTH,
        }
    
    @staticmethod
    def get_dimension_for_model(model_name: str) -> int:
        if model_name in EmbeddingConfig.MODEL_DIMENSIONS:
            return EmbeddingConfig.MODEL_DIMENSIONS[model_name]
        elif model_name == EmbeddingMethod.CUSTOM:

            return EmbeddingConfig.DEFAULT_DIMENSION
        else:
            
            return EmbeddingConfig.DEFAULT_DIMENSION
    
model = SentenceTransformer(
    EmbeddingConfig.get_model_config()['model_name'],
    cache_folder=EmbeddingConfig.get_model_config()['cache_dir'],
    device=EmbeddingConfig.get_model_config()['device']
)