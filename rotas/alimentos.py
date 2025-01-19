from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from models.alimento import Alimento
from database import get_session

router = APIRouter(
    prefix="/alimentos",
    tags=["Alimentos"],
)


@router.post("/", response_model=Alimento)

def create_alimento(alimento: Alimento, session: Session = Depends(get_session)):
    """
    Cria um alimento
    Args:
        alimento (Alimento): Objeto alimento
        session (Session):

    Returns:
        Alimento: Retorna o alimento criado
    """ 
    session.add(alimento)
    session.commit()
    session.refresh(alimento)
    return alimento

@router.get("/", response_model=list[Alimento])
def read_alimentos(
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    sort_by: str = Query(default="nome"),  
    session: Session = Depends(get_session)
):
    """
    Retorna todos alimentos

    Args:
        offset (int): Deslocamento da query
        limit (int): Limite da consulta
        sort_by (str): Tipo de ordenamento
        session (Session): Sessao do banco de dados

    Returns:
        List[Alimento]: Retorna todos os alimentos
    """ 
    statement = select(Alimento).offset(offset).limit(limit)
    if sort_by:
        statement = statement.order_by(getattr(Alimento, sort_by))
    return session.exec(statement).all()

@router.get("/{alimento_id}", response_model=Alimento)
def read_alimento(alimento_id: int, session: Session = Depends(get_session)):
    """
    Retorna um alimento pelo id

    Args:
        alimento_id (int): Id do alimento
        session (Session): sessao do banco de dados
    Raises:
        HTTPException: Caso o alimento nao seja encontrado
        
    Returns:
        Alimento: Retorna o alimento
    """ 
    alimento = session.get(Alimento, alimento_id)
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    return alimento


@router.put("/{alimento_id}", response_model=Alimento)
def update_alimento(alimento_id: int, alimento: Alimento, session: Session = Depends(get_session)):
    """
    Atualiza um alimento

    Args:
        alimento_id (int): Id do alimento
        alimento (Alimento): Novo objeto alimento 
        session (Session): sessao do banco de dados
    Raises:
        HTTPException: Caso o alimento nao seja encontrado
        
    Returns:
        Alimento: Retorna o alimento atualizado
    """ 
    db_alimento = session.get(Alimento, alimento_id)
    if not db_alimento:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    for key, value in alimento.dict(exclude_unset=True).items():
        setattr(db_alimento, key, value)
    session.add(db_alimento)
    session.commit()
    session.refresh(db_alimento)
    return db_alimento

@router.delete("/{alimento_id}")
def delete_alimento(alimento_id: int, session: Session = Depends(get_session)):
    """
    Apaga um alimento pelo id

    Args:
        alimento_id (int): Id do alimento
        session (Session): sessao do banco de dados
    Raises:
        HTTPException: Caso o alimento nao seja encontrado
        
    Returns:
        Objeto: Retorna uma mensagem de confirmacao
    """ 
    alimento = session.get(Alimento, alimento_id)
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento não encontrado")
    session.delete(alimento)
    session.commit()
    return {"alimento apagado": True}


@router.get("/procurar/", response_model=list[Alimento])
def search_alimentos(query: str, session: Session = Depends(get_session)):
    """
    Retorna um alimento pelo nome dele

    Args:
        query (str): Nome do alimento
        session (Session): sessao do banco de dados
    Returns:
        List[Alimento]: Retorna todos os alimentos com um nome parecido
    """ 
    statement = select(Alimento).where(Alimento.nome.ilike(f"%{query}%"))
    return session.exec(statement).all()