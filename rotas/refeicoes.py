from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, func
from sqlalchemy.orm import joinedload
from typing import List
from models.alimento import Alimento
from models.refeicao import Refeicao, RefeicaoBase, RefeicaoAlimento
from database import get_session
from datetime import datetime


# Rotas para Refeição
router = APIRouter(
    prefix="/refeicoes",
    tags=["Refeicoes"]
)

@router.post("/", response_model=Refeicao)
def create_refeicao(refeicao: RefeicaoBase, session: Session = Depends(get_session)):
    nova_refeicao = Refeicao.from_orm(refeicao)
    session.add(nova_refeicao)
    session.commit()
    session.refresh(nova_refeicao)
    return nova_refeicao


@router.get("/count", response_model=int)
def count_refeicoes(session: Session = Depends(get_session)):
    return session.exec(select(func.count(Refeicao.id))).scalar()

@router.get("/count-by-user", response_model=dict)
def count_refeicoes_by_user(session: Session = Depends(get_session)):
    return session.exec(select(Refeicao.usuario_id, func.count(Refeicao.id))
                        .group_by(Refeicao.usuario_id)).all()

@router.get("/", response_model=List[Refeicao])
def read_refeicoes(
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    order_by: str = Query("id"),  # Default order by 'id'
    session: Session = Depends(get_session),
):
    statement = select(Refeicao).offset(offset).limit(limit)

    # Filtro por data (data inicial e final)
    if start_date:
        statement = statement.where(Refeicao.horario >= start_date)
    if end_date:
        statement = statement.where(Refeicao.horario <= end_date)

    # Ordenação
    if order_by == "horario":
        statement = statement.order_by(Refeicao.horario)
    else:
        statement = statement.order_by(Refeicao.id)

    # Consultas com joinedload para carregar relacionamentos
    statement = statement.options(joinedload(Refeicao.usuario), joinedload(Refeicao.alimentos))

    return session.exec(statement).all()

@router.get("/{refeicao_id}", response_model=Refeicao)
def read_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeicao not found")
    return refeicao


@router.put("/{refeicao_id}", response_model=Refeicao)
def update_refeicao(refeicao_id: int, refeicao: RefeicaoBase, session: Session = Depends(get_session)):
    db_refeicao = session.get(Refeicao, refeicao_id)
    if not db_refeicao:
        raise HTTPException(status_code=404, detail="Refeicao not found")
    for key, value in refeicao.dict(exclude_unset=True).items():
        setattr(db_refeicao, key, value)
    db_refeicao.horario = datetime.utcnow()
    session.add(db_refeicao)
    session.commit()
    session.refresh(db_refeicao)
    return db_refeicao

@router.delete("/{refeicao_id}")
def delete_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeicao not found")
    session.delete(refeicao)
    session.commit()
    return {"ok": True}

@router.post("/{refeicao_id}/alimentos/{alimento_id}", response_model=Refeicao)
def add_alimento_to_refeicao(refeicao_id: int, alimento_id: int, session: Session = Depends(get_session)):
    refeicao = session.get(Refeicao, refeicao_id)
    alimento = session.get(Alimento, alimento_id)
    if not refeicao or not alimento:
        raise HTTPException(status_code=404, detail="Refeicao or Alimento not found")
    link = RefeicaoAlimento(refeicao_id=refeicao_id, alimento_id=alimento_id)
    session.add(link)
    session.commit()
    return refeicao

@router.delete("/{refeicao_id}/alimentos/{alimento_id}")
def remove_alimento_from_refeicao(refeicao_id: int, alimento_id: int, session: Session = Depends(get_session)):
    link = session.exec(
        select(RefeicaoAlimento).where(
            RefeicaoAlimento.refeicao_id == refeicao_id,
            RefeicaoAlimento.alimento_id == alimento_id,
        )
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Association not found")
    session.delete(link)
    session.commit()
    return {"ok": True}
