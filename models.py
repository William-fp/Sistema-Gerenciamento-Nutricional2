from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    #refeicoes: id da refeicao

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def inserir_usuario(nome: str):
    with Session(engine) as session:
        usuario = Usuario(name=nome)
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        print(f"Usuário inserido: {usuario}")

# Testando a inserção
inserir_usuario("João da Silva")
