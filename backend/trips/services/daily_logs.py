from collections import defaultdict
from datetime import datetime, time, timedelta

from .hos import DutyStatus


def split_event_by_day(event: dict) -> list[dict]:
    """
    Split one event if it crosses midnight.

    Driving miles are distributed proportionally
    across each split segment.
    """

    start = datetime.fromisoformat(event["start"])
    end = datetime.fromisoformat(event["end"])

    total_duration_minutes = int(
        (end - start).total_seconds() / 60
    )

    total_miles = float(
        event.get("miles", 0)
    )

    segments = []
    current_start = start

    while current_start.date() < end.date():
        midnight = datetime.combine(
            current_start.date() + timedelta(days=1),
            time.min,
        )

        segment_minutes = int(
            (
                midnight - current_start
            ).total_seconds()
            / 60
        )

        segment_miles = 0.0

        if (
            event["status"]
            == DutyStatus.DRIVING.value
            and total_duration_minutes > 0
        ):
            segment_miles = (
                total_miles
                * segment_minutes
                / total_duration_minutes
            )

        segments.append({
            **event,
            "start": current_start.isoformat(),
            "end": midnight.isoformat(),
            "duration_minutes": segment_minutes,
            "miles": round(
                segment_miles,
                2,
            ),
        })

        current_start = midnight

    if current_start < end:
        segment_minutes = int(
            (
                end - current_start
            ).total_seconds()
            / 60
        )

        segment_miles = 0.0

        if (
            event["status"]
            == DutyStatus.DRIVING.value
            and total_duration_minutes > 0
        ):
            miles_already_used = sum(
                float(
                    segment.get(
                        "miles",
                        0,
                    )
                )
                for segment in segments
            )

            segment_miles = (
                total_miles
                - miles_already_used
            )

        segments.append({
            **event,
            "start": current_start.isoformat(),
            "end": end.isoformat(),
            "duration_minutes": segment_minutes,
            "miles": round(
                segment_miles,
                2,
            ),
        })

    return segments

def build_daily_logs(events: list[dict]) -> list[dict]:
    """
    Convert trip events into one ELD log per calendar day.

    Empty portions of each day are filled as OFF duty so
    each log represents a complete 24-hour period.
    """

    if not events:
        return []

    split_events = []

    for event in events:
        split_events.extend(
            split_event_by_day(event)
        )

    grouped = defaultdict(list)

    for event in split_events:
        start = datetime.fromisoformat(
            event["start"]
        )

        grouped[start.date()].append(event)

    first_date = min(grouped.keys())
    last_date = max(grouped.keys())

    logs = []

    current_date = first_date

    while current_date <= last_date:
        day_start = datetime.combine(
            current_date,
            time.min,
        )

        day_end = day_start + timedelta(days=1)

        day_events = sorted(
            grouped.get(current_date, []),
            key=lambda event: event["start"],
        )

        normalized_events = []

        cursor = day_start

        for event in day_events:
            event_start = datetime.fromisoformat(
                event["start"]
            )

            event_end = datetime.fromisoformat(
                event["end"]
            )

            # Fill time before the first event or between
            # events as OFF DUTY.
            if event_start > cursor:
                normalized_events.append(
                    _make_off_duty_event(
                        cursor,
                        event_start,
                    )
                )

            normalized_events.append(event)

            cursor = max(
                cursor,
                event_end,
            )

        # Fill remainder of the day.
        if cursor < day_end:
            normalized_events.append(
                _make_off_duty_event(
                    cursor,
                    day_end,
                )
            )

        totals = calculate_status_totals(
            normalized_events
        )

        total_miles = sum(
            float(event.get("miles", 0))
            for event in normalized_events
            if event["status"] == DutyStatus.DRIVING.value
        )

        logs.append({
            "date": current_date.isoformat(),
            "events": normalized_events,
            "totals": totals,
            "total_miles": round(total_miles, 2),
        })

        current_date += timedelta(days=1)

    return logs

def _make_off_duty_event(
    start: datetime,
    end: datetime,
) -> dict:

    return {
        "status": DutyStatus.OFF_DUTY.value,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "duration_minutes": int(
            (end - start).total_seconds() / 60
        ),
        "reason": "Off duty",
        "location": None,
        "miles": 0,
    }

def calculate_status_totals(
    events: list[dict],
) -> dict:

    totals_minutes = {
        DutyStatus.OFF_DUTY.value: 0,
        DutyStatus.SLEEPER.value: 0,
        DutyStatus.DRIVING.value: 0,
        DutyStatus.ON_DUTY.value: 0,
    }

    for event in events:
        status = event["status"]

        totals_minutes[status] += (
            event["duration_minutes"]
        )

    return {
        status: round(
            minutes / 60,
            2,
        )
        for status, minutes
        in totals_minutes.items()
    }

