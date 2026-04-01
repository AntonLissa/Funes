from retrieval.retriever import Retriever
'''
retriever naive che prende in input una query e restituisce i risultati più rilevanti da ciascuna memoria, che poi possono essere utilizzati dal LLM per generare risposte informate.
Le memorie sono passate come lista in modo da essere flessibile e permettere di aggiungere o rimuovere memorie senza dover modificare il retriever.
'''
class SimpleRetriever(Retriever):

    def __init__(self, memories, top_k=3):
        self.memories = memories
        self.top_k = top_k

    def retrieve(self, query):

        results = []
        seen = set()

        for memory in self.memories:

            memory_results = memory.search(query, k=self.top_k)

            for item in memory_results:

                text = item["text"]

                if text not in seen: # evitiamo di duplicare
                    seen.add(text)
                    results.append(item)

        return results
