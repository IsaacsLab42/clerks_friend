__all__ = ["get_expiring_recommends_report"]

from lcr_session import LcrSession
from prettytable import MARKDOWN, PrettyTable

from .data import get_expiring_recommends_data
from .types import RecommendType


def get_expiring_recommends_report(
    lcr: LcrSession,
    months_past: int = -3,
    months_future: int = 1,
    recommend_type: RecommendType = RecommendType.All,
) -> str:
    data = get_expiring_recommends_data(lcr, months_past, months_future, recommend_type)

    table = PrettyTable()
    table.field_names = ["Name", "Expiration"]
    table.set_style(MARKDOWN)
    table.align = "l"

    for entry in data:
        table.add_row([entry.name, entry.expiration_display])

    return table.get_string()
