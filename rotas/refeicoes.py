from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select, func
from models.refeicao import Refeicao
from database import get_session
from datetime import date
from models.alimento import Alimento
from models.usuario import Usuario
from models.refeicao import RefeicaoAlimento

router = APIRouter(
    prefix="/refeicoes",
    tags=["Refeicoes"],
)

@router.post("/", response_model=Refeicao)
def create_refeicao(
    refeicao: Refeicao,
    alimentos: list[int],
    session: Session = Depends(get_session)
):
    
    if not session.get(Usuario, refeicao.usuario_id):
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    
    for alimento_id in alimentos:
        if not session.get(Alimento, alimento_id):
            raise HTTPException(
                status_code=400, detail=f"Alimento com ID {alimento_id} não encontrado"
            )

    
    session.add(refeicao)
    session.commit()
    session.refresh(refeicao)

    
    for alimento_id in alimentos:
        relacionamento = RefeicaoAlimento(refeicao_id=refeicao.id, alimento_id=alimento_id)
        session.add(relacionamento)

    session.commit()
    return refeicao




@router.get("/refeicoes/{refeicao_id}/alimentos/count")
def count_alimentos_por_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    count = session.exec(select(func.count(RefeicaoAlimento.alimento_id)).where(RefeicaoAlimento.refeicao_id == refeicao_id)).one()
    return {"total_alimentos": count}


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


@router.put("/{refeicao_id}", response_model=Refeicao)
def update_refeicao(
    refeicao_id: int,
    refeicao: Refeicao,
    alimentos: list[int],  
    session: Session = Depends(get_session)
):
    db_refeicao = session.get(Refeicao, refeicao_id)
    if not db_refeicao:
        raise HTTPException(status_code=404, detail="Refeição não encontrada")

   
    if not session.get(Usuario, refeicao.usuario_id):
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    
    for key, value in refeicao.dict(exclude={"alimentos"}, exclude_unset=True).items():
        setattr(db_refeicao, key, value)

   
    session.query(RefeicaoAlimento).filter_by(refeicao_id=refeicao_id).delete()

   
    for alimento_id in alimentos:
        if not session.get(Alimento, alimento_id):
            raise HTTPException(status_code=400, detail=f"Alimento com ID {alimento_id} não encontrado")
        novo_relacionamento = RefeicaoAlimento(refeicao_id=refeicao_id, alimento_id=alimento_id)
        session.add(novo_relacionamento)

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

