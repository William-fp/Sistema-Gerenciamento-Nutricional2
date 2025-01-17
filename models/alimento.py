from sqlmodel import SQLModel, Field

class Alimento(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    calorias: float
    proteinas: float
    carboidratos: float
    gorduras: float
    sodio: float
    acucar: float
