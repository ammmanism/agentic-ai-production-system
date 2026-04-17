from typing import List, Tuple
import numpy as np
# Mocking CrossEncoder and get_embedding_model for now
class CrossEncoder:
    def __init__(self, model_name):
        self.model_name = model_name
    def predict(self, pairs):
        return [0.8] * len(pairs)
def get_embedding_model():
    return None

class ContextCompressor:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2", threshold=0.5):
        self.cross_encoder = CrossEncoder(model_name)
        self.threshold = threshold
        self.embed_model = get_embedding_model()

    def split_into_sentences(self, text: str) -> List[str]:
        """Simple sentence splitter – replace with nltk or regex if needed."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    async def compress(self, query: str, documents: List[str]) -> Tuple[str, List[str]]:
        """
        Returns (compressed_text, kept_sentences)
        """
        all_sentences = []
        sent_to_doc = []  # map sentence index -> original doc index

        for doc_idx, doc in enumerate(documents):
            sents = self.split_into_sentences(doc)
            all_sentences.extend(sents)
            sent_to_doc.extend([doc_idx] * len(sents))

        if not all_sentences:
            return "", []

        # Cross-encoder scoring (query, sentence)
        pairs = [(query, sent) for sent in all_sentences]
        scores = self.cross_encoder.predict(pairs)  # list of floats

        # Keep sentences above threshold
        kept_indices = [i for i, score in enumerate(scores) if score > self.threshold]
        kept_sentences = [all_sentences[i] for i in kept_indices]

        # Reconstruct compressed text (preserve original document order)
        compressed_text = " ".join(kept_sentences)
        return compressed_text, kept_sentences
