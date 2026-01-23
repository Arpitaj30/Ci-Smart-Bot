import os
import requests

USE_GROQ = os.getenv("USE_GROQ", "false") == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_llm(prompt: str) -> str:
    if USE_GROQ:
        return ask_groq(prompt)
    else:
        return ask_local(prompt)

def ask_groq(prompt):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
    )
    return response.json()["choices"][0]["message"]["content"]

def ask_local(prompt):
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch

    model_name = "codellama/CodeLlama-7b-Instruct-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=300)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)