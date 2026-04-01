from abc import ABC, abstractmethod
'''
interfaccia astratta per i modelli di embedding, che definisce il metodo embed che prende in input un testo e restituisce un vettore di embedding. 
Permette di cambiare modello senza cambaire il resto del sistema.
'''
class EmbeddingModel(ABC):

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass
