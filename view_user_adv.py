from aiohttp import web
from models import User, Token, Advertisement
import json
from sqlalchemy.ext.asyncio import AsyncSession
from check_auth_validate import hash_password, check_password, validate, check_token, check_owner
from schema import CreateUser, CreateAdv, PatchUser, PatchAdv, Login, SCHEMA_MODEL
from crud import add_item, create_item, get_item_by_id, select_item, update_item, delete_item
from middleware_errors import Unauthorized
from sqlalchemy import func, select



class BaseView(web.View):
    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def validated_json(self, schema: SCHEMA_MODEL):
        json_data = await self.request.json()
        return validate(schema, json_data)


class UserView(BaseView):

    @property
    def user_id(self) -> int | None:
        user_id = int(self.request.match_info["user_id"])
        return user_id

    @check_token
    async def get(self):
        user = await get_item_by_id(User, self.user_id, self.session)
        return web.json_response(user.dict)


    async def post(self):
        json_data = await self.validated_json(CreateUser)
        json_data['password'] = hash_password(json_data['password'])
        user = await create_item(User, json_data, self.session)
        return web.json_response({'id': user.id, "name": user.name})

    @check_token
    async def patch(self):
        payload = await self.validated_json(PatchUser)
        if 'password' in payload:
            payload['password'] = hash_password(payload['password'])
        user = await get_item_by_id(User, self.user_id, self.session)
        user = await update_item(user, payload, self.session)
        return web.json_response({'id': user.id, "name": user.name})

    @check_token
    async def delete(self):
        user = await get_item_by_id(User, self.user_id, self.session)
        await delete_item(user, self.session)
        return web.json_response({'status': 'success'})


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


class AdvView(BaseView):
    @property
    def adv_id(self) -> int | None:
        adv_id = self.request.match_info.get("adv_id")
        return int(adv_id) if adv_id else None

    @property
    async def user_id(self) -> int:
        token = self.request.headers.get("Authorization")
        user_id_query = select(Token.user_id).where(Token.token == token)
        user_id = await select_item(user_id_query, self.session)
        return user_id

    @check_token
    async def get(self):
        user_id = await self.user_id
        user = await get_item_by_id(User, user_id, self.session)
        if self.adv_id is None:
            return web.json_response([adv.dict for adv in user.advertisements])
        adv = await get_item_by_id(Advertisement, self.adv_id, self.session)
        check_owner(adv, user_id)
        return web.json_response(adv.dict)

    @check_token
    async def post(self):
        json_data = await self.validated_json(CreateAdv)
        user_id = await self.user_id
        adv = await create_item(Advertisement, dict(user_id=user_id, **json_data), self.session)
        return web.json_response({'id': adv.id, "name": adv.author})

    @check_token
    async def patch(self):
        payload = await self.validated_json(PatchAdv)
        user_id = await self.user_id
        adv = await get_item_by_id(Advertisement, self.adv_id, self.session)
        check_owner(adv, user_id)
        adv = await update_item(adv, payload, self.session)
        return web.json_response({'id': adv.id, "author": adv.author})

    @check_token
    async def delete(self):
        user_id = await self.user_id
        user = await get_item_by_id(User, user_id, self.session)
        adv = await get_item_by_id(Advertisement, self.adv_id, self.session)
        check_owner(adv, user_id)
        await delete_item(adv, self.session)
        return web.json_response({'status': 'success'})