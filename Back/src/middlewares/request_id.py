from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response


async def id_requisicao(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    # Mantem o mesmo ID na requisicao e na resposta para rastrear logs.
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response
