from aiohttp import web
from models import User, Token, Advertisement, Session
import json
# from sqlalchemy.ext.asyncio import AsyncSession
from check_auth_validate import hash_password, check_password, validate, check_token
from schema import CreateUser, CreateAdv, PatchUser, PatchAdv, Login, SCHEMA_MODEL
from crud import add_item, create_item, get_item_by_id, select_item
from middleware_errors import Unauthorized
from sqlalchemy import func, select



class BaseView(web.View):
    @property
    def session(self) -> Session:
        return self.request.session

    @property
    def token(self) -> Token:
        return self.request.token

    @property
    def user(self) -> User:
        return self.request.token.user

    @property
    def is_authorized(self) -> bool:
        return hasattr(self.request, "token")

    # async def on_request(self):
    #     with open('token.txt', 'r') as file:
    #         token = file.read().strip()
    #         self.request['token'] = token

    async def validated_json(self, schema: SCHEMA_MODEL):
        json_data = await self.request.json()
        return validate(schema, json_data)


class LoginView(BaseView):
    async def post(self):
        payload = await self.validated_json(Login)
        query = select(User).where(User.name == payload['name']).limit(1)
        user = await select_item(query, self.session)
        if user is None:
            raise Unauthorized("user not found")
        if check_password(payload["password"], user.password):
            token = await create_item(Token, {"user_id": user.id}, self.session)
            with open('token.txt', 'w') as file:
                file.write(str(token.token))
            return web.json_response({"token": str(token.token), "user_id": token.user_id})
        raise Unauthorized("invalid password")


class UserView(BaseView):

    @check_token
    async def get(self):
        return web.json_response({"status": "ok"})


    async def post(self):
        json_data = await self.validated_json(CreateUser)
        json_data['password'] = hash_password(json_data['password'])
        user = await create_item(User, json_data, self.session)
        return web.json_response({'id': user.id})


    async def patch(self):
        user_data = await self.validated_json(PatchUser)
        if 'password' in user_data:
            user_data['password'] = hash_password(user_data['password'])
        user = await update_item(self.token.user, payload, self.session)
        return web.json_response({'id': user.id})


    async def delete(self):
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({'status': 'success'})


