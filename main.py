from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session

app = FastAPI()

# home page
@app.get("/")
async def home():
    return {"message" : "API do sistema de Informação nutricional"}
