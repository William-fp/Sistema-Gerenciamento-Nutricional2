from sqlmodel import Session
from database import create_db_and_tables, get_session
from models.usuario import Usuario
from models.refeicao import Refeicao, RefeicaoAlimento
from models.alimento import Alimento
from datetime import date

def create_and_populate():
    # Crie o banco de dados e as tabelas
    create_db_and_tables()
    populate_data()

def populate_data():
    with get_session() as session:
        # Usuários
        usuarios = [
            Usuario(name="Carlos", idade=30, peso=80.5),
            Usuario(name="Ana", idade=25, peso=65.0),
            Usuario(name="João", idade=22, peso=70.3),
            Usuario(name="Mariana", idade=28, peso=55.0),
            Usuario(name="Pedro", idade=35, peso=85.0),
            Usuario(name="Juliana", idade=32, peso=68.2),
            Usuario(name="Lucas", idade=27, peso=72.0),
            Usuario(name="Fernanda", idade=24, peso=58.5),
            Usuario(name="Ricardo", idade=29, peso=76.3),
            Usuario(name="Beatriz", idade=26, peso=62.4)
        ]
        session.add_all(usuarios)
        session.commit()

        # Alimentos
        alimentos = [
            Alimento(nome="Maçã", calorias=52, proteinas=0.3, carboidratos=14, gorduras=0.2, sodio=1, acucar=10),
            Alimento(nome="Banana", calorias=96, proteinas=1.3, carboidratos=27, gorduras=0.3, sodio=1, acucar=14),
            Alimento(nome="Arroz", calorias=130, proteinas=2.7, carboidratos=28, gorduras=0.3, sodio=1, acucar=0),
            Alimento(nome="Feijão", calorias=127, proteinas=8.7, carboidratos=23, gorduras=0.5, sodio=5, acucar=0),
            Alimento(nome="Frango", calorias=239, proteinas=27, carboidratos=0, gorduras=14, sodio=70, acucar=0),
            Alimento(nome="Ovo", calorias=155, proteinas=13, carboidratos=1.1, gorduras=11, sodio=124, acucar=0),
            Alimento(nome="Leite", calorias=42, proteinas=3.4, carboidratos=5, gorduras=1, sodio=44, acucar=5),
            Alimento(nome="Pão", calorias=265, proteinas=9, carboidratos=49, gorduras=3.2, sodio=491, acucar=5),
            Alimento(nome="Queijo", calorias=402, proteinas=25, carboidratos=1.3, gorduras=33, sodio=621, acucar=0),
            Alimento(nome="Tomate", calorias=18, proteinas=0.9, carboidratos=3.9, gorduras=0.2, sodio=5, acucar=2.6)
        ]
        session.add_all(alimentos)
        session.commit()

        # Refeições
        refeicoes = [
            Refeicao(tipo="Café da manhã", usuario_id=1, data=date(2023, 1, 1)),
            Refeicao(tipo="Almoço", usuario_id=2, data=date(2023, 1, 2)),
            Refeicao(tipo="Jantar", usuario_id=3, data=date(2023, 1, 3)),
            Refeicao(tipo="Café da manhã", usuario_id=4, data=date(2023, 1, 4)),
            Refeicao(tipo="Almoço", usuario_id=5, data=date(2023, 1, 5)),
            Refeicao(tipo="Jantar", usuario_id=6, data=date(2023, 1, 6)),
            Refeicao(tipo="Café da manhã", usuario_id=7, data=date(2023, 1, 7)),
            Refeicao(tipo="Almoço", usuario_id=8, data=date(2023, 1, 8)),
            Refeicao(tipo="Jantar", usuario_id=9, data=date(2023, 1, 9)),
            Refeicao(tipo="Café da manhã", usuario_id=10, data=date(2023, 1, 10))
        ]
        session.add_all(refeicoes)
        session.commit()

        # Relacionamentos RefeicaoAlimento
        refeicao_alimentos = [
            RefeicaoAlimento(refeicao_id=1, alimento_id=1),
            RefeicaoAlimento(refeicao_id=1, alimento_id=2),
            RefeicaoAlimento(refeicao_id=2, alimento_id=3),
            RefeicaoAlimento(refeicao_id=2, alimento_id=4),
            RefeicaoAlimento(refeicao_id=3, alimento_id=5),
            RefeicaoAlimento(refeicao_id=3, alimento_id=6),
            RefeicaoAlimento(refeicao_id=4, alimento_id=1),
            RefeicaoAlimento(refeicao_id=4, alimento_id=7),
            RefeicaoAlimento(refeicao_id=5, alimento_id=3),
            RefeicaoAlimento(refeicao_id=5, alimento_id=8),
            RefeicaoAlimento(refeicao_id=6, alimento_id=9),
            RefeicaoAlimento(refeicao_id=6, alimento_id=10),
            RefeicaoAlimento(refeicao_id=7, alimento_id=1),
            RefeicaoAlimento(refeicao_id=7, alimento_id=4),
            RefeicaoAlimento(refeicao_id=8, alimento_id=2),
            RefeicaoAlimento(refeicao_id=8, alimento_id=9),
            RefeicaoAlimento(refeicao_id=9, alimento_id=5),
            RefeicaoAlimento(refeicao_id=9, alimento_id=6),
            RefeicaoAlimento(refeicao_id=10, alimento_id=7),
            RefeicaoAlimento(refeicao_id=10, alimento_id=8)
        ]
        session.add_all(refeicao_alimentos)
        session.commit()

# Verificação para executar se o arquivo for rodado diretamente
if __name__ == "__main__":
    create_and_populate()
