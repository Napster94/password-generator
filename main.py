from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import secrets
import string
import httpx
import os
import asyncio

app = FastAPI()

# Allow Flutter or any frontend to access your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API config
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_URL = "https://api-inference.huggingface.co/models/gpt2"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


@app.get("/")
def read_root():
    return {"message": "Zahle AI API is running!"}


@app.get("/generate-password")
def generate_password(length: int = 12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return {"password": password}


async def query_hf(prompt: str, max_length: int = 60):
    """Query Hugging Face Inference API safely."""
    async with httpx.AsyncClient(timeout=60) as client:  # increased timeout
        try:
            response = await client.post(
                HF_URL,
                headers=HEADERS,
                json={"inputs": prompt, "parameters": {"max_new_tokens": max_length}},
            )
        except httpx.RequestError as e:
            print(f"HTTP request failed: {e}")
            return None

        print("HF Status code:", response.status_code)
        print("HF Response text (first 500 chars):", response.text[:500])

        if response.status_code != 200:
            return None

        try:
            data = response.json()
        except ValueError:
            print("Non-JSON response from HF:", response.text)
            return None

        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return str(data)


async def query_hf_with_retry(prompt: str, max_length: int = 60, retries: int = 3):
    """Retry HF query on failure."""
    for attempt in range(retries):
        result = await query_hf(prompt, max_length)
        if result:
            return result
        print(f"Retrying HF query {attempt + 1}/{retries}...")
        await asyncio.sleep(2)
    return None


@app.get("/fun-fact")
async def get_fun_fact():
    prompt = "Give me one short fun historical or cultural fact about Zahlé, Lebanon. Keep it under 2 sentences."
    result = await query_hf_with_retry(prompt, max_length=60)
    if not result:
        return {"fact": "Could not fetch fun fact at the moment. Please try again later."}
    fact = result.replace(prompt, "").strip()
    return {"fact": fact}


@app.get("/places")
async def get_places():
    prompt = "List 5 must-visit places in Zahlé, Lebanon. Return them as a simple numbered list, no extra descriptions."
    result = await query_hf_with_retry(prompt, max_length=120)
    if not result:
        return {"places": ["Could not fetch places at the moment. Please try again later."]}

    text = result.replace(prompt, "").strip()
    places = [line.split(". ", 1)[1] if ". " in line else line for line in text.split("\n") if line]
    return {"places": places}
