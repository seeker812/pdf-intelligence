import asyncio
import functools

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def response_wrapper(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        if not isinstance(result, tuple) or len(result) != 2:
            raise ValueError(
                f"{func.__name__} must return a tuple of (data, message), got {type(result).__name__}"
            )

        data, message = result

        return JSONResponse(
            content=jsonable_encoder(
                {
                    "success": True,
                    "message": message,
                    "data": data,
                }
            )
        )

    return wrapper
