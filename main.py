from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import secrets
import string
from transformers import pipeline

app = FastAPI()

# Allow any frontend to access your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize local text-generation pipeline
generator = pipeline("text-generation", model="sshleifer/tiny-gpt2")

@app.get("/")
def read_root():
    return {"message": "Zahle AI API is running locally!"}


@app.get("/generate-password")
def generate_password(length: int = 12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return {"password": password}


def generate_text(prompt: str, max_length: int = 60) -> str:
    """Generate text using local model."""
    result = generator(prompt, max_length=max_length, do_sample=True, temperature=0.7)[0]["generated_text"]
    # Remove the prompt from the generated text
    text = result.replace(prompt, "").strip()
    return text


@app.get("/fun-fact")
def get_fun_fact():
    prompt = "Give me one short fun historical or cultural fact about Zahlé, Lebanon. Keep it under 2 sentences."
    fact = generate_text(prompt, max_length=60)
    return {"fact": fact}


@app.get("/places")
def get_places():
    prompt = "List 5 must-visit places in Zahlé, Lebanon. Return them as a simple numbered list, no extra descriptions."
    text = generate_text(prompt, max_length=120)
    # Convert generated text to a list
    places = [line.split(". ", 1)[1] if ". " in line else line for line in text.split("\n") if line]
    return {"places": places}
