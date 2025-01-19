from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from database import get_session
from models.usuario import Usuario
from models.refeicao import Refeicao
from models.alimento import Alimento
from models.refeicao import RefeicaoAlimento

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)

@router.post("/", response_model=Usuario)
def create_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    """
    Cria um usuario
    Args:
        usuario (Usuario): Objeto usuario a ser criado
        session (Session): Sessao do banco de dados

    Returns:
        usuario: Usuario criado
    """ 
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/", response_model=list[Usuario])
def read_usuarios(
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    sort_by: str = Query(default="name"),  
    session: Session = Depends(get_session)
):
    """
    Lista todas os usuarios
    Args:
        offset (int): Deslocamento da query
        limit (int): Limite da query
        sort_by (str): Tipo de ordenamento
        session (Session): Sessao do banco de dados

    Returns:
        list[Usuario]: Retorna todas os usuarios
    """ 
    statement = select(Usuario).offset(offset).limit(limit)
    if sort_by:
        statement = statement.order_by(getattr(Usuario, sort_by))
    return session.exec(statement).all()


@router.get("/{usuario_id}", response_model=Usuario)
def read_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """
    Lista um usuario pelo seu id
    Args:
        usuario_id (int): Id do usuario
        session (Session): A sessao do banco de dados

    Returns:
        usuario: Retorna um usuario
    Raises:
        HTTPException: Caso o usuario nao seja encontrado
    """ 
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    return usuario


@router.get("/procurar/", response_model=list[Usuario])
def search_usuarios(query: str, session: Session = Depends(get_session)):
    """
    Lista usuarios com um nome parecido
    Args:
        query (str): Nome do usuario
        session (Session): A sessao do banco de dados

    Returns:
        list[Usuario]: Retorna uma lista de usuarios
    """ 
    statement = select(Usuario).where(Usuario.name.ilike(f"%{query}%"))
    return session.exec(statement).all()


@router.get("/{usuario_id}/refeicoes/contar")
def count_refeicoes_por_usuario(usuario_id: int, session: Session = Depends(get_session)):
    """
    Conta o numero de refeicoes de um usuario
    Args:
        usuario_id (int): Id do usuario
        session (Session): A sessao do banco de dados

    Returns:
        Objeto: Retorna um objeto com o numero de refeicoes
    """ 
    count = session.exec(select(func.count(Refeicao.id)).where(Refeicao.usuario_id == usuario_id)).one()
    return {"total_refeicoes": count}


@router.get("/status/contar")
def count_usuarios(session: Session = Depends(get_session)):
    """
    Conta o numero de usuarios
    Args:
        session (Session): A sessao do banco de dados

    Returns:
        Objeto: Retorna um objeto com o total de usuario
    """ 
    count = session.exec(select(func.count(Usuario.id))).one()
    return {"total_usuarios": count}


@router.put("/{usuario_id}", response_model=Usuario)
def update_usuario(usuario_id: int, usuario: Usuario, session: Session = Depends(get_session)):
    """
    Atualiza um usuario
    Args:
        usuario_id (int): Id do usuario
        usuario (Usuario): Novo objeto usuario
        session (Session): A sessao do banco de dados

    Returns:
        usuario: Retorna o usuario atualizado
    Raises:
        HTTPException: Caso o usuario nao seja encontrado
    """ 
    db_usuario = session.get(Usuario, usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    for key, value in usuario.dict(exclude_unset=True).items():
        setattr(db_usuario, key, value)
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)
    return db_usuario


@router.delete("/{usuario_id}")
def delete_user(usuario_id: int, session: Session = Depends(get_session)):
    """
    Deleta um usuario
    Args:
        usuario_id (int): Id do usuario
        session (Session): A sessao do banco de dados

    Returns:
        Objeto: Retorna um objeto com uma mensagem de sucesso
    Raises:
        HTTPException: Caso o usuario nao seja encontrado
    """ 
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    session.delete(usuario)
    session.commit()
    return {"Usuario deletado": True}

@router.get("/{usuario_id}/refeicoes_com_alimentos")
def read_refeicoes_com_alimentos(usuario_id: int, session: Session = Depends(get_session)):
    """
    Retorna as refeicoes com alimentos de um usuario

    Args:
        usuario_id (int): Id do usuario
        session (Session): sessao do banco de dados
    Raises:
        HTTPException: Caso o alimento ou uma refeicao nao seja encontrada
        
    Returns:
        resultado: objeto contendo os refeicoes e alimentos
    """ 
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    refeicoes = session.exec(select(Refeicao).where(Refeicao.usuario_id == usuario_id)).all()
    if not refeicoes:
        raise HTTPException(status_code=404, detail="Nenhuma refeição encontrada para este usuário")

    resultado = []
    for refeicao in refeicoes:
        alimentos = session.exec(
            select(Alimento).join(RefeicaoAlimento).where(RefeicaoAlimento.refeicao_id == refeicao.id)
        ).all()
        resultado.append({
            "refeicao": refeicao,
            "alimentos": alimentos
        })

    return resultado

