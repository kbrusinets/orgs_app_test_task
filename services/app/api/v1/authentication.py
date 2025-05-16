from typing import Annotated

from fastapi import Depends, HTTPException, status

from services.backend import Backend, get_backend
from services.backend.modules.auth.schemas import User


async def check_api_key(
        backend: Annotated[Backend, Depends(get_backend)],
        api_key: str | None = None,
) -> User | None:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Api key not provided.'
        )
    try:
        user = await backend.auth_module.get_current_user(api_key=api_key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        ) from e
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Wrong api key.'
        )
    return user