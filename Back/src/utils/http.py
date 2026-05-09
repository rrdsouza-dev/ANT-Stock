from collections.abc import AsyncGenerator

import httpx


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        yield client
