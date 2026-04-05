import os

from groq import Groq

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("API key not found. Set OPENAI_API_KEY in environment variables.")

    return Groq(api_key=api_key)

def chat(client, user_prompt, system_prompt=None, model="llama-3.3-70b-versatile"): #llama-3.1-8b-instant #llama-3.3-70b-versatile #openai/gpt-oss-120b
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_prompt})
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0.0,          # Increases randomness
            #frequency_penalty=1.1,    # Discourages repeating words/phrases
            #presence_penalty=1.0,     # Encourages moving to new topics
            top_p=1.0,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro ao chamar a API: {str(e)}"