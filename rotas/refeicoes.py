from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlmodel import Session, select, func
from models.refeicao import Refeicao, RefeicaoAlimento, RefeicaoCreate, RefeicaoUpdate
from database import get_session
from datetime import date
from models.alimento import Alimento
from models.usuario import Usuario
from typing import List


router = APIRouter(
    prefix="/refeicoes",
    tags=["Refeicoes"],
)


@router.post("/", response_model=Refeicao, status_code=status.HTTP_201_CREATED)
def create_refeicao(*, session: Session = Depends(get_session), refeicao: RefeicaoCreate):
    # Verifica se o usuário existe
    user = session.get(Usuario, refeicao.usuario_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Cria a nova refeição
    nova_refeicao = Refeicao(
        tipo=refeicao.tipo,
        data=refeicao.data,
        usuario_id=refeicao.usuario_id
    )
    session.add(nova_refeicao)
    session.commit()
    session.refresh(nova_refeicao)

    # Associa os alimentos à refeição
    for alimento_id in refeicao.alimentos_ids:
        alimento = session.get(Alimento, alimento_id)
        if not alimento:
            raise HTTPException(status_code=404, detail=f"Alimento com ID {alimento_id} não encontrado")

        refeicao_alimento = RefeicaoAlimento(
            refeicao_id=nova_refeicao.id,
            alimento_id=alimento.id
        )
        session.add(refeicao_alimento)

    session.commit()
    session.refresh(nova_refeicao)

    return nova_refeicao


@router.get("/", response_model=list[Refeicao])
def read_refeicoes(
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    sort_by: str = Query(default="data"),  
    session: Session = Depends(get_session)
):
    statement = select(Refeicao).offset(offset).limit(limit)
    if sort_by:
        statement = statement.order_by(getattr(Refeicao, sort_by))
    return session.exec(statement).all()


@router.get("/{refeicao_id}", response_model=Refeicao)
def read_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeicao não encontrada")
    return refeicao


@router.get("/by_date/", response_model=list[Refeicao])
def read_refeicoes_por_data(data: date, session: Session = Depends(get_session)):
    statement = select(Refeicao).where(Refeicao.data == data)
    return session.exec(statement).all()


@router.get("/refeicoes/{refeicao_id}/alimentos/count")
def count_alimentos_por_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    count = session.exec(select(func.count(RefeicaoAlimento.alimento_id)).where(RefeicaoAlimento.refeicao_id == refeicao_id)).one()
    return {"total_alimentos": count}



@router.put("/{refeicao_id}", response_model=Refeicao)
def update_refeicao(*, session: Session = Depends(get_session), refeicao_id: int, refeicao: RefeicaoUpdate):
    # Verifica se a refeição existe
    db_refeicao = session.get(Refeicao, refeicao_id)
    if not db_refeicao:
        raise HTTPException(status_code=404, detail="Refeição não encontrada")

    # Atualiza os campos da refeição, exceto usuario_id
    db_refeicao.tipo = refeicao.tipo
    db_refeicao.data = refeicao.data

    # Limpa as associações atuais de alimentos
    session.query(RefeicaoAlimento).filter_by(refeicao_id=refeicao_id).delete()

    # Associa os novos alimentos à refeição
    for alimento_id in refeicao.alimentos_ids:
        alimento = session.get(Alimento, alimento_id)
        if not alimento:
            raise HTTPException(status_code=404, detail=f"Alimento com ID {alimento_id} não encontrado")

        refeicao_alimento = RefeicaoAlimento(
            refeicao_id=db_refeicao.id,
            alimento_id=alimento.id
        )
        session.add(refeicao_alimento)

    session.commit()
    session.refresh(db_refeicao)

    return db_refeicao



@router.delete("/{refeicao_id}")
def delete_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeicao não encontrada")
    session.delete(refeicao)
    session.commit()
    return {"ok": True}

@router.get("/{refeicao_id}/alimentos", response_model=list[Alimento])
def read_alimentos_por_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    statement = select(Refeicao).where(Refeicao.id == refeicao_id)
    refeicao = session.exec(statement).one_or_none()
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeição não encontrada")
    
    alimentos = session.exec(select(Alimento).join(RefeicaoAlimento).where(RefeicaoAlimento.refeicao_id == refeicao_id)).all()
    return alimentos

