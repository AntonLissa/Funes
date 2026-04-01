# providers/groq_provider.py
import requests, time
from funes.AIM.llm.provider.base_provider import BaseProvider

class GroqProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.model_small_name = 'llama-3.1-8b-instant'
        self.model_large_name = 'llama-3.3-70b-versatile'
    

    def call(self, model_name, system_prompt, user_prompt, temperature=0):
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            data = {
                "model": model_name,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(self.url, headers=headers, json=data)
                    if response.status_code in [429, 500]:
                        print(f"[GroqProvider] Received {response.status_code}, retrying in 5s...")
                        time.sleep(5)
                        continue
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"].strip()
                except requests.RequestException as e:
                    print(f"[GroqProvider] Attempt {attempt+1}/{max_retries} failed for prompt:\n'{user_prompt}'\nError: {e}")
                    time.sleep(1)

            print(f"[GroqProvider] All {max_retries} attempts failed. Returning None.")
            return None
