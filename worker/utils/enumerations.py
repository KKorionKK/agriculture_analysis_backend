from enum import Enum


class DataStatus(str, Enum):
    declined = "declined"
    waiting = "waiting"
    failed = "failed"
    processing = "processing"
    ready = "ready"

    @staticmethod
    def as_dict():
        data = DataStatus._member_map_  # noqa
        for k, v in data.items():
            data[k] = v.value
        return data


class AnalysisType(str, Enum):
    ndvi = "ndvi"
    neural = "neural"
    both = "both"

    @staticmethod
    def as_dict():
        data = AnalysisType._member_map_  # noqa
        for k, v in data.items():
            data[k] = v.value
        return data
