from fastapi import FastAPI
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
