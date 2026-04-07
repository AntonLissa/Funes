from abc import ABC, abstractmethod

'''
Abbiamo una classe astratta Memory che definisce l'interfaccia per le memorie dei documenti, delle procedure e delle soluzioni. 
Ogni memoria implementa i metodi add e search, che permettono di aggiungere nuovi elementi e di cercare elementi rilevanti in base a una query.
Il retriever non deve sapere come sono implementate le memorie, ma solo che hanno questi metodi, il che permette di cambiare l'implementazione delle memorie senza dover modificare il retriever o altre parti del sistema.
'''
class Memory(ABC):

    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def search(self, query):
        pass

    @abstractmethod
    def get_all(self):
        pass
