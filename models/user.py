from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .refeicao import Refeicao

class UserBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    idade: int
    peso: float
    

class User(UserBase, table=True):
    refeicoes: List["Refeicao"] = Relationship(back_populates="user")
