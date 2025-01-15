from datetime import datetime, timezone
from uuid import uuid4
import random


def get_dt():
    return datetime.now(timezone.utc)


def get_uuid():
    return str(uuid4())


def generate_invite_link():
    return str(uuid4().hex)[: round(len(uuid4().hex) / 4)]


def generate_code():
    code = ""
    for _ in range(6):
        code += str(random.randint(0, 9))
    return code
