__all__ = ["get_expiring_recommends_data"]

import arrow
from lcr_session import ChurchUrl, LcrSession

from .types import RecommendStatus, RecommendType


def get_expiring_recommends_data(
    lcr: LcrSession,
    months_past: int = -3,
    months_future: int = 1,
    recommend_type: RecommendType = RecommendType.All,
) -> list[RecommendStatus]:
    """
    Get a list of the expiring/expired temple recommends.

    Args:
        lcr: A previously constructed LcrSession object
        months_past: How many months in the past to include in the report. A 0 indicates
            recommends that are expiring this month. A -2 would indicate two months ago,
            for example.
        months_future: How many months in the future to include in the report. For
            example, a 1 would include the following month.
        recommend_type: Type of the recommends to include. For example, to just get
            youth recommends then set this to `RecommendType.LimitedUse`.

    Raises:
        ValueError: If unknown data is encountered.

    Returns:
        List of recommends matching the filter criteria.
    """
    # Figure out the bounds for expired recommends
    now = arrow.now()
    range_start = now.floor("month").shift(months=months_past)
    range_end = now.ceil("month").shift(months=months_future)

    # Perform the request to get the data
    url = ChurchUrl("lcr", "api/temple-recommend/report?unitNumber={unit}")
    recommend_report = lcr.get_json(url)

    # Iterate over data and filter out unwanted
    expiring = []
    for entry in recommend_report["reportData"]:

        exp_date = arrow.get(entry["recommendReportLine"]["expirationDate"])
        if exp_date < range_start or exp_date > range_end:
            continue

        match entry["recommendReportLine"]["recommendType"]:
            case "LIMITED_USE":
                r_type = RecommendType.LimitedUse
            case "REGULAR":
                r_type = RecommendType.Regular
            case _:
                raise ValueError(
                    f"Unknown recommend type: {entry['recommendReportLine']['recommendType']}"
                )
        if recommend_type != r_type and recommend_type != RecommendType.All:
            continue

        recommend_status = RecommendStatus(
            entry["recommendReportLine"]["memberName"],
            entry["expiredDisplay"],
            exp_date,
            r_type,
        )

        expiring.append(recommend_status)

    return expiring
