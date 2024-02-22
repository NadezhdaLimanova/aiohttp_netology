from middleware_errors import Conflict, NotFound
from models import MODEL, MODEL_TYPE
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from sqlalchemy import Select

async def get_item_by_id(model: MODEL_TYPE, item_id: int, session: AsyncSession) -> MODEL:
    item = await session.get(model, item_id)
    if item is None:
        raise NotFound(f'{model.__name__} not found')
    return item


async def add_item(item: MODEL, session: AsyncSession) -> MODEL:
    try:
        session.add(item)
        await session.commit()
    except IntegrityError as err:
        raise Conflict(f"{item.__class__.__name__} already exists")
    return item


async def create_item(model: MODEL_TYPE, payload: dict, session: AsyncSession) -> MODEL:
    item = model(**payload)
    item = await add_item(item, session)
    return item


async def select_item(query: Select[Any], session: AsyncSession) -> MODEL:
    item = (await session.execute(query)).first()
    if not item:
        return None
    return item[0]


async def update_item(item: MODEL, payload: dict, session: AsyncSession) -> MODEL:
    for key, value in payload.items():
        setattr(item, key, value)
    await add_item(item, session)
    return item

async def delete_item(item: MODEL, session: AsyncSession):
    await session.delete(item)
    await session.commit()



