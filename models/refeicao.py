from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING
from datetime import date


if TYPE_CHECKING:
    from .usuario import Usuario
    from .alimento import Alimento

class RefeicaoAlimento(SQLModel, table=True):
    refeicao_id: int = Field(foreign_key="refeicao.id", primary_key=True)
    alimento_id: int = Field(foreign_key="alimento.id", primary_key=True)

class RefeicaoBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    tipo: str  # Exemplo: cafe da manha, almoço, etc
    data: date


class Refeicao(RefeicaoBase, table=True):
    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: "Usuario" = Relationship(back_populates="refeicoes")
    alimentos: List["Alimento"] = Relationship(link_model=RefeicaoAlimento)


class RefeicaoCreate(RefeicaoBase):
    usuario_id: int
    alimentos_ids: List[int]


class RefeicaoUpdate(RefeicaoBase):
    alimentos_ids: List[int]
