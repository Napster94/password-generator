from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
import secrets
import string

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Password generator API is running!"}


@app.get("/generate-password")
def generate_password(length: int = 12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return {"password": password}


@app.get("/fun-fact")
async def get_fun_fact():
    try:
        if not openai.api_key:
            return {"error": "Missing OpenAI API key on server."}

        prompt = "Give me one short fun historical or cultural fact about Zahlé, Lebanon. Keep it under 2 sentences."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.8
        )
        fact = response.choices[0].message["content"].strip()
        return {"fact": fact}
    except Exception as e:
        return {"error": str(e)}



@app.get("/places")
async def get_places():
    prompt = (
        "List 5 must-visit places in Zahlé, Lebanon. "
        "Return them as a simple numbered list, no extra text."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.8
    )
    text = response.choices[0].message["content"].strip()
    places = [line.split('. ', 1)[1] if '. ' in line else line for line in text.split('\n') if line]
    return {"places": places}
