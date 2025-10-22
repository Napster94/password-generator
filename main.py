from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import secrets
import string
import httpx
import os

app = FastAPI()

# Allow Flutter and any frontend to access your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_URL = "https://api-inference.huggingface.co/models/gpt2"  # lightweight free model
headers = {"Authorization": f"Bearer {HF_API_KEY}"}


@app.get("/")
def read_root():
    return {"message": "Zahle AI API is running!"}


@app.get("/generate-password")
def generate_password(length: int = 12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return {"password": password}


async def query_hf(prompt: str, max_length: int = 60):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            HF_URL,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_new_tokens": max_length}}
        )
        data = response.json()
        # Some models return a list of dicts
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return str(data)


@app.get("/fun-fact")
async def get_fun_fact():
    prompt = "Give me one short fun historical or cultural fact about Zahlé, Lebanon. Keep it under 2 sentences."
    result = await query_hf(prompt)
    fact = result.replace(prompt, "").strip()  # clean prompt repetition
    return {"fact": fact}


@app.get("/places")
async def get_places():
    prompt = "List 5 must-visit places in Zahlé, Lebanon. Return them as a simple numbered list, no extra descriptions."
    result = await query_hf(prompt, max_length=120)
    text = result.replace(prompt, "").strip()
    places = [line.split(". ", 1)[1] if ". " in line else line for line in text.split("\n") if line]
    return {"places": places}
