from sqlmodel import SQLModel
from database import create_db_and_tables  # Caso necessário
from models.refeicao import Refeicao, RefeicaoAlimento
from models.usuario import Usuario
from models.alimento import Alimento

# Caso as tabelas ainda não tenham sido criadas
create_db_and_tables()

# Imprime as tabelas registradas
print(SQLModel.metadata.tables)
