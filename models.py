import datetime
from sqlalchemy import UUID, create_engine, DateTime, String, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
import uuid
from aiohttp import web
from typing import List, Type
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)

from db import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    registration_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    tokens: Mapped[List["Token"]] = relationship(
        "Token", back_populates="user", cascade="all, delete-orphan", lazy="joined"
    )
    advertisements: Mapped[List["Advertisement"]] = relationship(
        "Advertisement", back_populates="user", cascade="all, delete-orphan", lazy="joined"
    )

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "advertisements": [advertisements.id for advertisements in self.advertisements],
            "registration_time": self.registration_time.isoformat(),
        }


class Advertisement(Base):
    __tablename__ = "app_for_advertisements"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    registration_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped[User] = relationship(User, back_populates="advertisements")

    @property
    def dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "description": self.description,
            "registration_time": self.registration_time.isoformat(),
            "user_id": self.user_id,
        }


class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(
        UUID, server_default=func.gen_random_uuid(), unique=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(User, back_populates="tokens", lazy="joined")

    @property
    def dict(self):
        return {"id": self.id, "token": self.token, "user_id": self.user_id}



MODEL_TYPE = Type[User | Token | Advertisement]
MODEL = User | Token | Advertisement



async def init_orm(app: web.Application):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield