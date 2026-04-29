from app.models.comum import EscopoDB, RegistroDB, Usuario
from app.models.escola import EscolaDB, GestaoEscolaDB
from app.models.estoque import (
    CategoriaDB,
    EstoqueDB,
    LocalizacaoDB,
    MovimentacaoDB,
    ProdutoDB,
)
from app.models.logistica import AlunoLogisticaDB, TurmaLogisticaDB

__all__ = (
    "AlunoLogisticaDB",
    "CategoriaDB",
    "EscolaDB",
    "EscopoDB",
    "EstoqueDB",
    "GestaoEscolaDB",
    "LocalizacaoDB",
    "MovimentacaoDB",
    "ProdutoDB",
    "RegistroDB",
    "TurmaLogisticaDB",
    "Usuario",
)
