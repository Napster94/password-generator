from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import secrets
import string
from openai import OpenAI

app = FastAPI()

# Allow Flutter frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client (new 1.x SDK syntax)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/generate-password")
def generate_password(length: int = 12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return {"password": password}


@app.get("/fun-fact")
def fun_fact():
    prompt = "Give me one short fun historical or cultural fact about Zahlé, Lebanon. Keep it under 2 sentences."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=60,
        )
        fact = response.choices[0].message.content.strip()
        return {"fact": fact}

    except Exception as e:
        print("OpenAI Error in /fun-fact:", e)
        return {"fact": "Could not fetch fun fact at the moment. Please try again later."}


@app.get("/places")
def places():
    prompt = "List 5 must-visit places in Zahlé, Lebanon. Return only names in a numbered list."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=120,
        )
        text = response.choices[0].message.content.strip()
        places = [line.split('. ', 1)[1] if '. ' in line else line for line in text.split('\n') if line]
        return {"places": places}

    except Exception as e:
        print("OpenAI Error in /places:", e)
        return {"places": ["Could not fetch places at the moment. Please try again later."]}
