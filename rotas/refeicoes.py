from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from models.refeicao import Refeicao
from database import get_session

router = APIRouter(
    prefix="/refeicoes",  # Prefixo para todas as rotas
    tags=["Refeicoes"],   # Tag para documentação automática
)

# Refeicoes
@router.post("/", response_model=Refeicao)
def create_refeicao(refeicao: Refeicao, session: Session = Depends(get_session)):
    session.add(refeicao)
    session.commit()
    session.refresh(refeicao)
    return refeicao

@router.get("/", response_model=list[Refeicao])
def read_refeicoes(offset: int = 0, limit: int = Query(default=10, le=100), 
               session: Session = Depends(get_session)):
    return session.exec(select(Refeicao).offset(offset).limit(limit)).all()

@router.get("/{refeicao_id}", response_model=Refeicao)
def read_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeicao nao encontrada")
    return refeicao

@router.put("/{refeicao_id}", response_model=Refeicao)
def update_refeicao(refeicao_id: int, refeicao: Refeicao, session: Session = Depends(get_session)):
    db_refeicao = session.get(Refeicao, refeicao_id)
    if not db_refeicao:
        raise HTTPException(status_code=404, detail="Refeicao nao encontrada")
    for key, value in refeicao.dict(exclude_unset=True).items():
        setattr(db_refeicao, key, value)
    session.add(db_refeicao)
    session.commit()
    session.refresh(db_refeicao)
    return db_refeicao

@router.delete("/{refeicao_id}")
def delete_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeicao nao encontrada")
    session.delete(refeicao)
    session.commit()
    return {"ok": True}
