class ContextBuilder:

    def build(self, retrieved_items):

        solutions = []
        documents = []

        for item in retrieved_items:

            metadata = item.get("metadata", {})
            item_type = metadata.get("type")

            if item_type == "solution":
                solutions.append(item["text"])

            elif item_type == "document":
                documents.append(item["text"])

        context = ""

        if solutions:
            context += "Known solutions:\n"
            context += "\n".join(solutions)
            context += "\n\n"

        if documents:
            context += "Relevant documents:\n"
            context += "\n".join(documents)

        return context
