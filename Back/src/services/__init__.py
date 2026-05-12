# Exporta servicos de regras de negocio.
from src.services.auth import AuthService
from src.services.stock import InventoryServices

__all__ = ["AuthService", "InventoryServices"]
