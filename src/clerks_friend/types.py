__all__ = ["RecommendType", "RecommendStatus"]

from dataclasses import dataclass
from enum import Enum

import arrow


class RecommendType(Enum):
    """
    Temple recommend type. When used as a filter all three options are valid. When used
    in the RecommendStatus then only Regular or LimitedUse are valid.
    """

    Regular = 1
    LimitedUse = 2
    All = 3


@dataclass
class RecommendStatus:
    """
    Individual recommend status
    """

    name: str
    expiration_display: str
    expiration_date: arrow.Arrow
    recommend_type: RecommendType
