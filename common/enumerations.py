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


class DataUploadedStatus(str, Enum):
    complete = "complete"
    partial = "partial"
    missing = "missing"

    @staticmethod
    def as_dict():
        data = DataUploadedStatus._member_map_  # noqa
        for k, v in data.items():
            data[k] = v.value
        return data


class HealthStatus(str, Enum):
    optimal = "Оптимальный"
    need_attention = "Требует внимания"
    critical = "Критический"

    @staticmethod
    def as_dict():
        data = HealthStatus._member_map_  # noqa
        for k, v in data.items():
            data[k] = v.value
        return data


class Roles(str, Enum):
    owner = "owner"
    admin = "admin"
    write = "write"
    read_only = "read_only"

    @staticmethod
    def as_dict():
        data = Roles._member_map_  # noqa
        for k, v in data.items():
            data[k] = v.value
        return data


class ChartType(str, Enum):
    ndvi = "ndvi"
    disease = "disease"
    health = "health"

    @staticmethod
    def as_list():
        data = ChartType._member_map_  # noqa
        return [item.name for item in data.values()]


class Filter(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class NotificationType(str, Enum):
    social = "social"
    analysis = "analysis"
    system = "system"


class NotificationSubjectType(str, Enum):
    analrequest = "analrequest"
    field = "field"
    invite = "invite"
    organization = "organization"
