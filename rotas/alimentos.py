from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, func
from sqlalchemy.orm import joinedload
from typing import List
from models.alimento import Alimento
from database import get_session
from datetime import datetime

router = APIRouter(
    prefix="/alimentos",
    tags=["Alimentos"]
)

# Rotas para Alimento
@router.post("/", response_model=Alimento)
def create_alimento(alimento: Alimento, session: Session = Depends(get_session)):
    session.add(alimento)
    session.commit()
    session.refresh(alimento)
    return alimento

@router.get("/count", response_model=int)
def count_alimentos(session: Session = Depends(get_session)):
    return session.exec(select(func.count(Alimento.id))).scalar()

@router.get("/count-by-type", response_model=dict)
def count_alimentos_by_type(session: Session = Depends(get_session)):
    return session.exec(select(Alimento.tipo, func.count(Alimento.id))
                        .group_by(Alimento.tipo)).all()

@router.get("/", response_model=List[Alimento])
def read_alimentos(
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    search: str = Query(None),  # Buscar por nome ou descrição
    order_by: str = Query("id"),  # Ordenar por ID ou nome
    session: Session = Depends(get_session),
):
    statement = select(Alimento).offset(offset).limit(limit)

    # Filtro por busca de texto parcial (nome ou descrição)
    if search:
        statement = statement.where(Alimento.nome.ilike(f"%{search}%") |
                                    Alimento.descricao.ilike(f"%{search}%"))

    # Ordenação
    if order_by == "nome":
        statement = statement.order_by(Alimento.nome)
    else:
        statement = statement.order_by(Alimento.id)

    return session.exec(statement).all()

@router.get("/{alimento_id}", response_model=Alimento)
def read_alimento(alimento_id: int, session: Session = Depends(get_session)):
    alimento = session.get(Alimento, alimento_id)
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento not found")
    return alimento



@router.put("/{alimento_id}", response_model=Alimento)
def update_alimento(alimento_id: int, alimento: Alimento, session: Session = Depends(get_session)):
    db_alimento = session.get(Alimento, alimento_id)
    if not db_alimento:
        raise HTTPException(status_code=404, detail="Alimento not found")
    for key, value in alimento.dict(exclude_unset=True).items():
        setattr(db_alimento, key, value)
    session.add(db_alimento)
    session.commit()
    session.refresh(db_alimento)
    return db_alimento

@router.delete("/{alimento_id}")
def delete_alimento(alimento_id: int, session: Session = Depends(get_session)):
    alimento = session.get(Alimento, alimento_id)
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento not found")
    session.delete(alimento)
    session.commit()
    return {"ok": True}

