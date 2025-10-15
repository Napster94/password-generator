from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/generate-password")
async def generate_password():
    prompt = (
        "Generate a strong, unique password that is secure yet easy to remember. "
        "Include a mix of letters, numbers, and symbols, but avoid dictionary words."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=15,
        temperature=0.8
    )

    password = response.choices[0].message["content"].strip()
    return {"password": password}
