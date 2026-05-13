from pathlib import Path
from typing import cast

import aiofiles


async def ler_texto(caminho: Path) -> str:
    async with aiofiles.open(caminho, encoding="utf-8") as arquivo:
        return cast(str, await arquivo.read())


async def salvar_texto(caminho: Path, conteudo: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(caminho, "w", encoding="utf-8") as arquivo:
        await arquivo.write(conteudo)
