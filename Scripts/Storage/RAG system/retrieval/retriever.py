'''
abbiamo una memoria per i  documenti, una per le procedure e una per le soluzioni. Il retriever prende in input una query e restituisce i risultati più rilevanti da ciascuna memoria, che poi possono essere utilizzati dal LLM per generare risposte informate.
'''
from abc import ABC, abstractmethod

class Retriever(ABC):

    @abstractmethod
    def retrieve(self, query: str):
        pass
