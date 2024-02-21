import bcrypt
from middleware_errors import BadRequest, Unauthorized
from aiohttp.web import View
from sqlalchemy import func, select
from schema import SCHEMA_MODEL
from models import MODEL, Token
from crud import select_item
from pydantic import ValidationError

def validate(model: SCHEMA_MODEL, json_data: dict):
    try:
        return model.model_validate(json_data).model_dump(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise BadRequest( error)

def hash_password(password: str):
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password

def check_password(password:str, hashed_password:str):
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password,hashed_password)


def check_token(handler):
    async def wrapper(view: View):
        token = view.request.headers.get("Authorization")
        if token is None or token.strip() == '':
            raise Unauthorized("token not found")
        token_query = select(Token).where(Token.token == token)
        token_result = await select_item(token_query, view.session)
        if token_result is None:
            raise Unauthorized("invalid token")
        view.request.token = token
        return await handler(view)
    return wrapper




