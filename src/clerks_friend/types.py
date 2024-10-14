__all__ = [
    "CallingStatus",
    "MovedOut",
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
class MovedOut:
    name: str
    birth_date: str
    move_date: str
    prior_unit: str
    next_unit_name: str
    next_unit_number: int
    address_Unknown: bool
    deceased: bool


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
