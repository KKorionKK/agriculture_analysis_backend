from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session
from contextlib import contextmanager
from threading import current_thread
from contextlib import asynccontextmanager
from asyncio import current_task

from api import config

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PostgreSQLController:
    def __init__(self, echo: bool = False) -> None:
        self.engine: AsyncEngine = create_async_engine(
            config.get_connection_string(), echo=echo
        )
        self._session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine, expire_on_commit=False
        )
        self._factory = async_scoped_session(
            self._session_maker, scopefunc=current_task
        )

    async def init_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def __call__(self) -> AsyncSession:  # type: ignore
        try:
            async with self._factory() as s:
                yield s
        finally:
            await self._factory.remove()


class SyncPostgreSQLController:
    def __init__(self, echo: bool = False) -> None:
        self.engine = create_engine(config.get_connection_string(True), echo=echo)
        self._session_maker = sessionmaker(self.engine, expire_on_commit=False)
        self._factory = scoped_session(self._session_maker, scopefunc=current_thread)

    def init_db(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_db(self) -> None:
        Base.metadata.drop_all(self.engine)

    @contextmanager
    def __call__(self) -> Session:
        session = self._factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            self._factory.remove()
