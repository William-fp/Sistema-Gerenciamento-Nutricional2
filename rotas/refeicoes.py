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
    """
    Cria uma refeicao
    Args:
        session (Session): Sessao do banco de dados
        refeicao (RefeicaoCreate): Objeto refeicao a ser criado

    Returns:
        nova_refeicao: Retorna a nova refeicao
    Raises:
        HTTPException: Caso um alimento da refeicao nao seja encontrado
    """ 
    user = session.get(Usuario, refeicao.usuario_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    nova_refeicao = Refeicao(
        tipo=refeicao.tipo,
        data=refeicao.data,
        usuario_id=refeicao.usuario_id
    )
    session.add(nova_refeicao)
    session.commit()
    session.refresh(nova_refeicao)

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
    """
    Lista todas as refeicoes
    Args:
        offset (int): Deslocamento da query
        limit (int): Limite da query
        sort_by (str): Tipo de ordenamento
        session (Session): Sessao do banco de dados

    Returns:
        list[Alimento]: Retorna todas as refeicoes
    """ 
    statement = select(Refeicao).offset(offset).limit(limit)
    if sort_by:
        statement = statement.order_by(getattr(Refeicao, sort_by))
    return session.exec(statement).all()


@router.get("/{refeicao_id}", response_model=Refeicao)
def read_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    """
    Lista uma refeicao pelo id dela
    Args:
        refeicao_id (int): Id da refeicao
        session (Session): A sessao do banco de dados

    Returns:
        list[Alimento]: Retorna o total de alimentos
    Raises:
        HTTPException: Caso a refeicao nao seja encontrada
    """ 
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeicao não encontrada")
    return refeicao


@router.get("/by_date/", response_model=list[Refeicao])
def read_refeicoes_por_data(data: date, session: Session = Depends(get_session)):
    """
    Retorna uma lista de refeicao ordernada pela data
    Args:
        data (date): Data da refeicao
        session (Session): A sessao do banco de dados

    Returns:
        list[Refeicao]: Retorna uma lista de refeicoes
    """ 
    statement = select(Refeicao).where(Refeicao.data == data)
    return session.exec(statement).all()


@router.get("/refeicoes/{refeicao_id}/alimentos/count")
def count_alimentos_por_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    """
    Conta a quantidade de alimentos de uma refeicao
    Args:
        refeicao_id (int): Id da refeicao
        session (Session): A sessao do banco de dados

    Returns:
        objeto: Retorna o total de alimentos
    """ 
    count = session.exec(select(func.count(RefeicaoAlimento.alimento_id)).where(RefeicaoAlimento.refeicao_id == refeicao_id)).one()
    return {"total_alimentos": count}

@router.put("/{refeicao_id}", response_model=Refeicao)
def update_refeicao(*, session: Session = Depends(get_session), refeicao_id: int, refeicao: RefeicaoUpdate):
    """
    Atualiza os dados de uma refeicao pelo id

    Args:
        refeicao_id (int): id da refeicao
        refeicao (RefeicaoUpdate): A nova refeicao com a lista de alimentos
        session (Session): Sessao do banco de dados

    Returns:
        db_refeicao: Retorna a refeicao atualizada

    Raises:
        HTTPException: 
            - Se a refeicao nao for encontrada
            - Se algum dos alimentos nao forem encontrados
    """
    db_refeicao = session.get(Refeicao, refeicao_id)
    if not db_refeicao:
        raise HTTPException(status_code=404, detail="Refeição não encontrada")

    db_refeicao.tipo = refeicao.tipo
    db_refeicao.data = refeicao.data

    session.query(RefeicaoAlimento).filter_by(refeicao_id=refeicao_id).delete()

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
    """
    Apaga uma refeicao pelo id dela
    Args:
        refeicao_id (int): Id da refeicao
        session (Session): A sessao do banco de dados

    Returns:
        objeto: Retorna uma mensagem de sucesso
    Raises:
        HTTPException: Caso a refeicao nao seja encontrada
    """ 
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeicao não encontrada")
    session.delete(refeicao)
    session.commit()
    return {"refeicao apagada": True}

@router.get("/{refeicao_id}/alimentos", response_model=list[Alimento])
def read_alimentos_por_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    """
    Retornar os alimentos de uma refeicao por id
    Args:
        refeicao_id (int): Id da refeicao
        session (Session): A sessao do banco de dados

    Returns:
        alimentos: Retorna uma lista de alimentos

    Raises:
        HTTPException: Caso a refeicao nao seja encontrada
    """ 
    statement = select(Refeicao).where(Refeicao.id == refeicao_id)
    refeicao = session.exec(statement).one_or_none()
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeição não encontrada")
    
    alimentos = session.exec(select(Alimento).join(RefeicaoAlimento).where(RefeicaoAlimento.refeicao_id == refeicao_id)).all()
    return alimentos

@router.get("/refeicoes/{refeicao_id}/usuario", response_model=Usuario)
def read_usuario_por_refeicao(refeicao_id: int, session: Session = Depends(get_session)):
    """
    Retornar o usuarios associado a uma refeicao
    Args:
        refeicao_id (int): Id da refeicao
        session (Session): A sessao do banco de dados

    Returns:
        usuario: Retorna um usuario

    Raises:
        HTTPException: Caso a refeicao nao seja encontrada
    """ 
    refeicao = session.get(Refeicao, refeicao_id)
    if not refeicao:
        raise HTTPException(status_code=404, detail="Refeição não encontrada")

    return refeicao.usuario
