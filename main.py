from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_and_tables
from rotas import home, usuarios, refeicoes, alimentos


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    yield
    

app = FastAPI(lifespan=lifespan)


app.include_router(home.router)
app.include_router(usuarios.router)
app.include_router(refeicoes.router)
app.include_router(alimentos.router)
