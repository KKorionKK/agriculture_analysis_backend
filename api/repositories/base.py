from api.services.database import PostgreSQLController


class Repository:
    def __init__(self, client: PostgreSQLController, manager: "PGManager") -> None:  # type: ignore # noqa: F821
        self.client = client
        self.manager = manager
