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
class MovedIn:
    name: str
    age: int
    birth_date: str
    move_date: str
    prior_unit_name: str
    prior_unit_number: int
    address: str


@dataclass
class MovedOut:
    name: str
    birth_date: str
    move_date: str
    prior_unit: str
    next_unit_name: str
    next_unit_number: int
    address_unknown: bool
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


@dataclass
class Member:
    name: str
    gender: str
    age: int
    birth_date: str
    phone_number: str
    email: str


@dataclass
class Family:
    name: str
    address: str
    phone_number: str
    email: str
