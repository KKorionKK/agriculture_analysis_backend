from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from .pg_manager import PGManager
from api.common.vigilante import Vigilante
from api.models import User
from api.common.enumerations import Roles

from api.common.exceptions.exceptions import CustomHTTPException, ExceptionCodes

from api import config
from api.schemas.authorization import RegisterData, Token, LoginData


class AuthorizationService:
    context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, pg: PGManager, v: Vigilante):
        self.pg: PGManager = pg
        self.__logger = v.get_logger()

    def __create_access_token(
        self,
        data: dict,
        expires_delta: timedelta,
    ) -> str:
        payload = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        payload.update({"exp": expire})
        encoded_jwt = jwt.encode(payload, config.SECRET, algorithm=config.ALGORITHM)
        return encoded_jwt

    async def get_user_role(self, organization_id: str, user_id: str) -> Roles:
        role = await self.pg.organizations.get_users_roles_in_organization(user_id, organization_id)
        return Roles(role)

    @staticmethod
    def hash_password(password: str) -> str:
        return AuthorizationService.context.hash(password)

    def __get_password_hash(self, password: str) -> str:
        return self.context.hash(password)

    def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.context.verify(plain_password, hashed_password)

    async def register_user(self, data: RegisterData) -> Token:
        user = await self.pg.users.get_user_by_email(data.email)
        access_token_delta = timedelta(minutes=config.ACCESS_SECURITY_TOKEN_EXPIRES)
        refresh_token_delta = timedelta(minutes=config.REFRESH_SECURITY_TOKEN_EXPIRES)
        if user:
            raise CustomHTTPException(ExceptionCodes.EmailInUse)
        else:
            password_hash = self.__get_password_hash(data.password)
            new_user = await self.pg.users.create_user_by_email(
                data.email, password_hash
            )
            access_token = self.__create_access_token(
                {"sub": new_user.email}, access_token_delta
            )
            refresh_token = self.__create_access_token(
                {"sub": new_user.email}, refresh_token_delta
            )
            return Token(access_token=access_token, refresh_token=refresh_token)

    async def login_user(self, data: LoginData) -> Token:
        user = await self.pg.users.get_user_by_email(data.email)
        if not user:
            raise CustomHTTPException(ExceptionCodes.AccountNotFound)
        access_token_delta = timedelta(minutes=config.ACCESS_SECURITY_TOKEN_EXPIRES)
        refresh_token_delta = timedelta(minutes=config.REFRESH_SECURITY_TOKEN_EXPIRES)
        if not self.__verify_password(data.password, user.password):
            raise CustomHTTPException(ExceptionCodes.InvalidCredentials)
        access_token = self.__create_access_token(
            {"sub": user.email}, access_token_delta
        )
        refresh_token = self.__create_access_token(
            {"sub": user.email}, refresh_token_delta
        )
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, config.SECRET, algorithms=[config.ALGORITHM])
            email: str | None = payload.get("sub")
            if email is None:
                raise CustomHTTPException(ExceptionCodes.InvalidCredentials)
        except JWTError:
            raise CustomHTTPException(ExceptionCodes.InvalidCredentials)
        user = await self.pg.users.get_user_by_email(email)
        if user is None:
            raise CustomHTTPException(ExceptionCodes.InvalidCredentials)
        return user
