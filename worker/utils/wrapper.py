from .database import SyncPostgreSQLController
from worker.models import AnalyzeRequest
from sqlalchemy import update
import datetime


def exception_manager(func):
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except Exception as e:
            request: AnalyzeRequest = kwargs.get("request")
            db = SyncPostgreSQLController()
            with db() as session:
                session.execute(
                    update(AnalyzeRequest)
                    .where(AnalyzeRequest.id == request.id)
                    .values(
                        fail_info={
                            "info": str(e),
                            "dt": str(datetime.datetime.now(datetime.timezone.utc)),
                        }
                    )
                )
                session.commit()

    return wrapper
