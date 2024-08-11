__all__ = [
    "CallingStatus",
    "RecommendStatus",
    "SacramentAttendance",
    "YouthProtectionTraining",
]

from dataclasses import dataclass


@dataclass
class CallingStatus:
    name: str
    position: str
    organization: str
    sustained: str


@dataclass
class RecommendStatus:
    """
    Individual recommend status
    """

    name: str
    expiration: str
    recommend_type: str


@dataclass
class SacramentAttendance:
    date: str
    count: int


@dataclass
class YouthProtectionTraining:
    name: str
    position: str
    organization: str
    expiration: str
