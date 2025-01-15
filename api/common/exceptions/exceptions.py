errors = {
    1: "Unexpected error",
    2: "Validation error",
    3: "Token not found",
    4: "Body is empty, contains unacceptable characters or violates constraints.",
    10: "Could not validate credentials",
    11: "Email in use",
    12: "Account not found",
    13: "Need any data for analysis",
    14: "Not enough permissions"
}


class CustomHTTPException(Exception):
    errors = errors

    def __init__(self, code: int, data: dict | str | None = None):
        self.code = code
        self.data = data

    def as_dict(self):
        return {
            "status": "ERR",
            "data": self.data,
            "code": self.code,
            "message": self.errors.get(self.code),
        }


class ExceptionCodes:
    UnexpectedError = 1
    ValidationError = 2
    TokenNotFound = 3
    EncoderError = 4

    InvalidCredentials = 10
    EmailInUse = 11
    AccountNotFound = 12
    NeedData = 13
    NotEnoughPermissions = 14
