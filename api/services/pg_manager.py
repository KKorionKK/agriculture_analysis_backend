from .database import PostgreSQLController
from api.repositories import (
    UsersRepository,
    FieldsRepository,
    AnalyzeRequestsRepository,
    OrganizationsRepository
    # TracksRepository,
    # SharesRepository
)


class PGManager:
    def __init__(self, echo: bool = False) -> None:
        self.client = PostgreSQLController(echo)
        self.users = UsersRepository(self.client, self)
        self.fields = FieldsRepository(self.client, self)
        self.analrequests = AnalyzeRequestsRepository(self.client, self)
        self.organizations = OrganizationsRepository(self.client, self)
        # self.tracks = TracksRepository(self.client, self)
        # self.shares = SharesRepository(self.client, self)
