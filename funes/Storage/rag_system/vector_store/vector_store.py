from abc import ABC, abstractmethod

'''
interfaccia del db vettoriale che definisce operazioni base.
'''
class VectorStore(ABC):

    @abstractmethod
    def add(self, ids, documents, embeddings, metadata):
        pass

    @abstractmethod
    def search(self, embedding, k):
        pass

    @abstractmethod
    def get_all(self):
        pass
