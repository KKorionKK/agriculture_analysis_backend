from .base import Repository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_
from api.models import User


class UsersRepository(Repository):
    async def get_user_by_email(self, email: str) -> User | None:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (await session.execute(select(User).where(User.email == email)))
                .scalars()
                .first()
            )
            return result

    async def get_user_by_identifier(self, identifier: str) -> User | None:
        async with self.client() as session:
            session: AsyncSession
            result = (
                (
                    await session.execute(
                        select(User).where(
                            or_(User.email == identifier, User.username == identifier)
                        )
                    )
                )
                .scalars()
                .first()
            )
            return result

    async def create_user_by_email(
        self, email: str, password_hash: str
    ) -> User:
        async with self.client() as session:
            session: AsyncSession
            user = User(email=email, password=password_hash)
            session.add(user)
            await session.flush()
            await session.commit()
            return user
