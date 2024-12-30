__all__ = [
    "get_expiring_recommends",
    "get_not_set_apart",
    "get_protecting_children_and_youth_training",
    "get_sacrament_meeting_attendance",
    "get_members_moved_out",
]

import arrow
from lcr_session import ChurchUrl, LcrSession

from .types import (
    CallingStatus,
    MovedIn,
    MovedOut,
    RecommendStatus,
    SacramentAttendance,
    YouthProtectionTraining,
)


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

        if entry["recommendReportLine"]["expirationDate"] is None:
            continue

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


def get_not_set_apart(lcr: LcrSession) -> list[CallingStatus]:
    """
    Get a list of people who have not been set apart.

    Args:
        lcr: A previously constructed LcrSession object

    Returns:
        List of people not set apart.
    """
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


def get_protecting_children_and_youth_training(
    lcr: LcrSession, months_future: int = 0
) -> list[YouthProtectionTraining]:
    """
    Get a list of people whose Protecting Children and Youth training is expiring.

    Args:
        lcr: A previously constructed LcrSession object
        months_future: Number of months in the future to check for expiration. A value
            of 0 indicates the current month only.

    Returns:
        List of expired and expiring training.
    """
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


def get_sacrament_meeting_attendance(
    lcr: LcrSession, year: int = 0
) -> list[SacramentAttendance]:
    """
    Get weekly sacrament meeting attendance for the specified year.

    Args:
        lcr: A previously constructed LcrSession object
        year: Attendance year to fetch. 0 for current year.

    Returns:
        List of weekly attendance numbers.
    """
    url = ChurchUrl("lcr", "api/sacrament-attendance/unit/{unit}/years/{year}")

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


def get_members_moved_out(lcr: LcrSession, months: int = 1) -> list[MovedOut]:
    """
    Get the list of members moved out.

    Args:
        lcr: A previously constructed LcrSession object
        months: Number of months worth of data to fetch

    Returns:
        List of members moved out
    """
    url = ChurchUrl("lcr", "api/umlu/report/members-moved-out/unit/{unit}/{months}")

    data = lcr.get_json(url, months=months)
    moved = []
    for entry in data:
        name = entry["name"]
        birth_date = entry["birthDate"]
        move_date = entry["moveDate"]
        prior_unit = entry["priorUnit"]
        next_unit_name = entry["nextUnitName"]
        next_unit_number = entry["nextUnitNumber"]
        address_unknown = entry["addressUnknown"]
        deceased = entry["deceased"]
        moved.append(
            MovedOut(
                name,
                birth_date,
                move_date,
                prior_unit,
                next_unit_name,
                next_unit_number,
                address_unknown,
                deceased,
            )
        )
    return moved


def get_members_moved_in(lcr: LcrSession, months: int = 1) -> list[MovedIn]:
    """
    Get the list of members moved in.

    Args:
        lcr: A previously constructed LcrSession object
        months: Number of months worth of data to fetch

    Returns:
        List of members moved in
    """
    url = ChurchUrl("lcr", "api/report/members-moved-in/unit/{unit}/{months}")

    data = lcr.get_json(url, months=months)
    moved = []
    for entry in data:
        name = entry["name"]
        age = entry["age"]
        birth_date = entry["birthdate"]
        move_date = entry["moveDate"]
        prior_unit_name = entry["priorUnitName"]
        prior_unit_number = entry["priorUnitNumber"]
        address = entry["textAddress"]
        moved.append(
            MovedIn(
                name=name,
                age=age,
                birth_date=birth_date,
                move_date=move_date,
                prior_unit_name=prior_unit_name,
                prior_unit_number=prior_unit_number,
                address=address,
            )
        )
    return moved
