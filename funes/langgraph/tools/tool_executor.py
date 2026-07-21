class ToolExecutor:
    def __init__(self):
        # Qui memorizziamo le istanze delle classi Tool
        self._tools = {}

    def register(self, tool):
        """Aggiunge un tool al registro."""
        self._tools[tool.name] = tool

    def execute(self, tool_name: str, query: str) -> str:
        """Esegue il tool corrispondente al nome ricevuto."""
        print('[EXECUTOR] Ricevuto comando per eseguire:', tool_name, "con query:", query)
        tool = self._tools.get(tool_name)
        
        if not tool:
            return f"Errore: il tool '{tool_name}' non esiste nel registro."
        
        try:
            # Chiamiamo il metodo .run() della classe Tool
            print(f"[EXECUTOR] Eseguendo: {tool_name}...")
            result = tool.run(query)
            print(f"[EXECUTOR] Result for {tool_name}: {result}")
            return result
        except Exception as e:
            return f"Errore durante l'esecuzione di {tool_name}: {str(e)}"