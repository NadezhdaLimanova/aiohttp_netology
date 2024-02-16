from aiohttp import web
from aiohttp.typedefs import Handler
from aiohttp.web_exceptions import HTTPInternalServerError, HTTPMethodNotAllowed, HTTPNotFound
from models import Session, engine
import json
from aiohttp.web import HTTPException


class Error(HTTPException):
    def __init__(self, description: dict | list | str):
        self.description = description

        super().__init__(
            text=json.dumps({"status": "error", "description": description}),
            content_type="application/json",
        )


class NotFound(Error):
    status_code = 404


class BadRequest(Error):
    status_code = 400


class Conflict(Error):
    status_code = 409


class Unauthorized(Error):
    status_code = 401


class Forbidden(Error):
    status_code = 403


class MethodNotAllowed(Error):
    status_code = 405


class UnexpectedError(Error):
    status_code = 500



@web.middleware
async def errors_middleware(request: web.Request, handler: Handler):
    try:
        response = await handler(request)
    except HTTPNotFound:
        raise NotFound(description="url not found")
    except HTTPMethodNotAllowed:
        raise NotFound(description="method not allowed")
    except HTTPInternalServerError:
        raise NotFound(description="unexpected error")
    return response


@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response