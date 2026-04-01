from sentence_transformers import SentenceTransformer
from .embedding_model import EmbeddingModel

'''
usa sentence transformer per creare embedding dei testi. Implementa l'interfaccia EmbeddingModel, quindi può essere usato in modo intercambiabile con altri modelli di embedding se necessario.
'''
class SentenceTransformerEmbedding(EmbeddingModel):

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str):
        return self.model.encode(text).tolist()
