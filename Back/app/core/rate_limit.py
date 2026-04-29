from __future__ import annotations

import hashlib
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

from fastapi import HTTPException, Request, status

from app.core.config import get_settings


@dataclass
class Balde:
    eventos: deque[float] = field(default_factory=deque)
    bloqueado_ate: float = 0
    violacoes: int = 0


_baldes: dict[str, Balde] = defaultdict(Balde)


def _hash(valor: str) -> str:
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def _ip(request: Request) -> str:
    cliente = request.client.host if request.client else "desconhecido"
    encaminhado = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    real = request.headers.get("x-real-ip", "").strip()
    return encaminhado or real or cliente


def _assinatura(request: Request) -> str:
    agente = request.headers.get("user-agent", "")
    idioma = request.headers.get("accept-language", "")
    origem = request.headers.get("origin", "")
    return _hash(f"{_ip(request)}|{agente}|{idioma}|{origem}")


async def _identidade(request: Request) -> str:
    corpo = await request.body()
    if not corpo:
        return ""

    try:
        dados = json.loads(corpo)
    except json.JSONDecodeError:
        return ""

    email = str(dados.get("email") or "").lower().strip()
    token = str(dados.get("token") or "").strip()
    return email or token[:32]


def _limpar(balde: Balde, agora: float, janela: int) -> None:
    while balde.eventos and balde.eventos[0] <= agora - janela:
        balde.eventos.popleft()


async def limitar(request: Request, escopo: str = "global") -> None:
    config = get_settings()
    agora = time.monotonic()
    limite = config.rate_limite_auth_tentativas
    janela = config.rate_limite_janela_segundos
    bloqueio = config.rate_limite_bloqueio_segundos

    partes = [escopo, request.url.path, _assinatura(request)]
    if config.rate_limite_peso_identidade:
        identidade = await _identidade(request)
        if identidade:
            partes.append(_hash(identidade))

    chave = ":".join(partes)
    balde = _baldes[chave]

    if balde.bloqueado_ate > agora:
        espera = int(balde.bloqueado_ate - agora)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas. Tente novamente em {espera} segundos.",
            headers={"Retry-After": str(max(1, espera))},
        )

    _limpar(balde, agora, janela)
    balde.eventos.append(agora)

    if len(balde.eventos) > limite:
        balde.violacoes += 1
        multiplicador = min(8, 2 ** (balde.violacoes - 1))
        balde.bloqueado_ate = agora + (bloqueio * multiplicador)
        balde.eventos.clear()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Acesso temporariamente bloqueado.",
            headers={"Retry-After": str(bloqueio * multiplicador)},
        )


async def limitar_auth(request: Request) -> None:
    # Protege rotas sensiveis contra repeticao por IP, fingerprint leve e identidade.
    await limitar(request, escopo="auth")
