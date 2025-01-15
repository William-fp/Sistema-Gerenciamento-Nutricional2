from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Field, create_engine, Session


app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

# home page
@app.get("/")
async def home():
    return {"message" : "API do sistema de Informação nutricional"}
