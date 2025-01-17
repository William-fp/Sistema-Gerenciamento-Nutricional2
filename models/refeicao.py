from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .alimento import Alimento

class RefeicaoAlimento(SQLModel, table=True):
    refeicao_id: int = Field(foreign_key="refeicao.id", primary_key=True)
    alimento_id: int = Field(foreign_key="alimento.id", primary_key=True)

class RefeicaoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    tipo: str  # Exemplo: café da manhã, almoço, etc.
    horario: datetime

class Refeicao(RefeicaoBase, table=True):
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="refeicoes")
    alimentos: List["Alimento"] = Relationship(link_model="RefeicaoAlimento")
