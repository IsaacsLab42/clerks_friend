__all__ = [
    "get_expiring_recommends",
    "get_not_set_apart",
    "get_sacrament_meeting_attendance",
    "get_protecting_children_and_youth_training",
]

import arrow
from lcr_session import ChurchUrl, LcrSession

from .types import (
    CallingStatus,
    RecommendStatus,
    SacramentAttendance,
    YouthProtectionTraining,
)


def get_not_set_apart(lcr: LcrSession) -> list[CallingStatus]:
    url = ChurchUrl(
        "lcr", "api/report/members-with-callings?lang=eng&unitNumber={unit}"
    )
    members_with_callings = lcr.get_json(url)

    not_set_apart = []
    for member in members_with_callings:
        # Only ward level callings
        if member["outOfUnit"] or member["stake"]:
            continue
        if member["setApart"]:
            continue
        sustained = arrow.get(member["sustainedDate"]).format("YYYY-MM-DD")
        not_set_apart.append(
            CallingStatus(
                member["name"], member["position"], member["organization"], sustained
            )
        )
    return not_set_apart


def get_expiring_recommends(
    lcr: LcrSession,
    months_past: int = -3,
    months_future: int = 1,
    recommend_type: str | None = None,
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
        recommend_type: Type of the recommends to include. This should either be
            "REGULAR", "LIMITED_USE", or `None`. If `None` then all recommend types will
            be included.

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
    url = ChurchUrl("lcr", "api/temple-recommend/report?lang=eng&unitNumber={unit}")
    recommend_report = lcr.get_json(url)

    # Iterate over data and filter out unwanted
    expiring = []
    for entry in recommend_report["reportData"]:

        exp_date = arrow.get(entry["recommendReportLine"]["expirationDate"])
        if exp_date < range_start or exp_date > range_end:
            continue

        if (
            recommend_type is not None
            and entry["recommendReportLine"]["recommendType"] != recommend_type
        ):
            continue

        recommend_status = RecommendStatus(
            entry["recommendReportLine"]["memberName"],
            entry["expiredDisplay"],
            entry["recommendReportLine"]["recommendType"],
        )

        expiring.append(recommend_status)

    return expiring


def get_sacrament_meeting_attendance(
    lcr: LcrSession, year: int = 0
) -> list[SacramentAttendance]:
    url = ChurchUrl("lcr", "api/sacrament-attendance/unit/{unit}/years/{year}?lang=eng")

    if year == 0:
        now = arrow.now()
        year = now.year

    attendance_data = lcr.get_json(url, year=year)

    attendance = []
    for entry in attendance_data:
        month = entry["month"]
        for week in entry["weeks"]:
            if week["future"]:
                continue
            day = week["day"]
            the_date = f"{year}-{month:02d}-{day:02d}"
            count = week.get("value", 0)
            attendance.append(SacramentAttendance(the_date, count))

    return attendance


def get_protecting_children_and_youth_training(
    lcr: LcrSession, months_future: int = 0
) -> list[YouthProtectionTraining]:
    url = ChurchUrl("lcr", "api/report/child-protection?lang=eng")
    training_report = lcr.get_json(url)

    now = arrow.now()
    range_end = now.ceil("month").shift(months=months_future)

    org_types = {}
    for org in training_report["orgTypes"]:
        org_types[org["orgTypeId"]] = org["orgName"]

    training_status = []
    for entry in training_report["protectionDtoList"]:
        if entry["expirationDate"] is not None:
            expiration = arrow.get(entry["expirationDate"], "D MMM YYYY")
            if expiration > range_end:
                continue
            expiration_str = expiration.format("YYYY-MM-DD")
        else:
            expiration_str = "Past Due"
        org = org_types[entry["orgTypeId"]]
        training_status.append(
            YouthProtectionTraining(
                entry["name"], entry["positionName"], org, expiration_str
            )
        )

    return training_status
