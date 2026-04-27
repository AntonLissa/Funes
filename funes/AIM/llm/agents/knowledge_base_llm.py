

from funes.AIM.llm.agents.base_llm import BaseLLM

class KBLLM(BaseLLM):
    agent_type="kb"

    def __init__(self, model_name, prompts, provider):
        super().__init__(
            model_name=model_name,
            system_prompt=prompts["system_prompt"],
            user_prompt=prompts["user_prompt"],
            provider=provider
        )


    def rag_info_builder(self, rag_data):
        formatted = ""
        counter = 0
        for res in rag_data:
            counter += 1
            metadata = res['metadata']
            formatted += f"{counter}:  Title: {metadata['title']}, Page: {metadata['page_number']}\nText:{res['text']}.\n\n"
        return formatted

    def build_prompt(self, data):

        return self.user_prompt.format(
            useful_info = self.rag_info_builder(data['rag_data']),
            conversation_history=data['conversation_history'],
            user_query = data['user_query'],
            datetime = ''
        )
