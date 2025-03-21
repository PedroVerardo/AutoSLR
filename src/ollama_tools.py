import requests
import json
import logging

OLLAMA_URL = "http://localhost:11434"

def ask_llm(prompt, context: list[str] = [], model="deepseek-r1:1.5b"):
    try:

        if isinstance(prompt, list):
            prompt = "\n".join(str(item) for item in prompt)

        if isinstance(context, list):
            context = "\n".join(str(item) for item in context)

        data = {
            "model": model,
            "prompt": f"Context:\n{context}\nEnd of context\nAnswer the question with only Context information, anything besides that write MYTHINKING:\n{prompt}"
        }

        response = requests.post(
            f'{OLLAMA_URL}/api/generate',
            json=data,
            timeout=10,
            stream=False
        )
        response.raise_for_status()
        
        full_response = ""
        for line in response.text.splitlines():
            if line.strip():
                try:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        full_response += json_response['response']
                except json.JSONDecodeError:
                    continue
        
        return full_response

    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama server"
    except requests.exceptions.RequestException as e:
        return f"Error: Request failed: {str(e)}"
    
if __name__ == "__main__":
    ask_llm("What is the capital of France?")