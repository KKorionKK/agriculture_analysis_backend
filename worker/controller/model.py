from dataclasses import dataclass, field
from common.models.analyze_request import AnalyzeRequest
import datetime
from worker.utils.enumerations import AnalysisType


def get_dt():
    return datetime.datetime.now(tz=datetime.timezone.utc)


@dataclass
class Task:
    task_id: int
    ttype: AnalysisType
    task: AnalyzeRequest
    args: tuple
    kwargs: dict
    dt: datetime.datetime = field(default_factory=get_dt)
