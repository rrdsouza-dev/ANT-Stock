from pathlib import Path
from typing import cast

import aiofiles


async def read_text(path: Path) -> str:
    async with aiofiles.open(path, encoding="utf-8") as file:
        return cast(str, await file.read())


async def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path, "w", encoding="utf-8") as file:
        await file.write(content)
