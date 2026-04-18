import numpy as np
from typing import List
# Mocking get_embedding_model for semantic chunking implementation
def get_embedding_model():
    class DummyEmbedder:
        def encode(self, texts):
            # Returns fixed random embeddings for semantic break computations
            return np.random.rand(len(texts), 768)
    return DummyEmbedder()

class SemanticChunker:
    """
    Elite-tier Semantic Chunker.
    Looks at cosine distances between sentence embeddings to determine split boundaries,
    ensuring thoughts aren't artificially broken by static chunk sizes.
    """
    def __init__(self, breakpoint_percentile_threshold: int = 90):
        self.embedder = get_embedding_model()
        self.breakpoint_percentile_threshold = breakpoint_percentile_threshold

    def split_into_sentences(self, text: str) -> List[str]:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)

    def chunk(self, text: str) -> List[str]:
        sentences = self.split_into_sentences(text)
        if len(sentences) < 3:
            return [text]

        embeddings = self.embedder.encode(sentences)
        
        # Calculate sequential distances
        distances = []
        for i in range(len(embeddings) - 1):
            distances.append(1.0 - self.cosine_similarity(embeddings[i], embeddings[i+1]))
            
        # Determine breakpoints based on percentile threshold
        breakpoint_val = np.percentile(distances, self.breakpoint_percentile_threshold)
        
        chunks = []
        current_chunk = [sentences[0]]
        
        for i, dist in enumerate(distances):
            if dist > breakpoint_val:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i+1]]
            else:
                current_chunk.append(sentences[i+1])
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
