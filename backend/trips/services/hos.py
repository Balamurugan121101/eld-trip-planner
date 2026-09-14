from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class DutyStatus(str, Enum):
    OFF_DUTY = "OFF"
    SLEEPER = "SB"
    DRIVING = "D"
    ON_DUTY = "ON"

MAX_DRIVING = 11 * 60
MAX_WINDOW = 14 * 60
BREAK_TRIGGER = 8 * 60
BREAK_DURATION = 30
DAILY_REST = 10 * 60
CYCLE_LIMIT = 70 * 60
CYCLE_RESTART = 34 * 60
PICKUP_DURATION = 60
DROPOFF_DURATION = 60
FUEL_DURATION = 30
FUEL_INTERVAL = 1000


@dataclass
class DutyEvent:
    status: DutyStatus
    start: datetime
    end: datetime
    reason: str
    location: str | None = None
    miles: float = 0

    @property
    def duration_minutes(self):
        return round(
            (
                self.end - self.start
            ).total_seconds() / 60
        )

    def to_dict(self):
        return {
            "status": self.status.value,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_minutes":
                self.duration_minutes,
            "reason": self.reason,
            "location": self.location,
            "miles": round(self.miles, 2),
        }

class HOSPlanner:

    def __init__(
        self,
        start_time: datetime,
        current_cycle_used_hours: float,
    ):
        self.current_time = start_time

        self.cycle_used = round(
            current_cycle_used_hours * 60
        )

        self.shift_start: datetime | None = None

        self.shift_driving = 0

        self.driving_since_break = 0
        self.miles_since_fuel = 0.0

        self.events: list[DutyEvent] = []

    def add_event(
        self,
        status: DutyStatus,
        minutes: int,
        reason: str,
        location: str | None = None,
        miles: float = 0,
    ):
        if minutes <= 0:
            return

        start = self.current_time

        end = start + timedelta(
            minutes=minutes
        )

        self.events.append(
            DutyEvent(
                status=status,
                start=start,
                end=end,
                reason=reason,
                location=location,
                miles=miles,
            )
        )

        self.current_time = end

        if status in (
            DutyStatus.DRIVING,
            DutyStatus.ON_DUTY,
        ):
            self.cycle_used += minutes

        if status == DutyStatus.DRIVING:
            self.shift_driving += minutes
            self.driving_since_break += minutes
            self.miles_since_fuel += miles

    def start_shift_if_needed(self):
        if self.shift_start is None:
            self.shift_start = self.current_time

    def remaining_window_minutes(self):
        if self.shift_start is None:
            return MAX_WINDOW

        elapsed = round(
            (
                self.current_time
                - self.shift_start
            ).total_seconds() / 60
        )

        return max(
            0,
            MAX_WINDOW - elapsed,
        )
    
    def remaining_driving_minutes(self):
        return max(
            0,
            MAX_DRIVING
            - self.shift_driving,
        )

    def remaining_cycle_minutes(self):
        return max(
            0,
            CYCLE_LIMIT
            - self.cycle_used,
        )

    def take_break(
        self,
        location=None,
    ):
        self.add_event(
            DutyStatus.OFF_DUTY,
            BREAK_DURATION,
            "30-minute HOS break",
            location,
        )

        self.driving_since_break = 0

    def take_daily_rest(
        self,
        location=None,
    ):
        self.add_event(
            DutyStatus.SLEEPER,
            DAILY_REST,
            "10-hour required rest",
            location,
        )

        self.shift_start = None
        self.shift_driving = 0
        self.driving_since_break = 0

    def take_cycle_restart(
        self,
        location=None,
    ):
        self.add_event(
            DutyStatus.OFF_DUTY,
            CYCLE_RESTART,
            "34-hour cycle restart",
            location,
        )

        self.cycle_used = 0
        self.shift_start = None
        self.shift_driving = 0
        self.driving_since_break = 0

    def add_on_duty_stop(
        self,
        minutes: int,
        reason: str,
        location: str,
    ):
        self.start_shift_if_needed()

        self.add_event(
            DutyStatus.ON_DUTY,
            minutes,
            reason,
            location,
        )

        if minutes >= BREAK_DURATION:
            self.driving_since_break = 0

    def get_events(self):
        return [
            event.to_dict()
            for event in self.events
        ]
    
    def can_drive_now(self) -> bool:
        return (
            self.remaining_driving_minutes() > 0
            and self.remaining_window_minutes() > 0
            and self.remaining_cycle_minutes() > 0
        )

    def drive(
        self,
        total_minutes: int,
        total_miles: float,
        location: str | None = None,
    ):
        remaining_minutes = int(total_minutes)
        remaining_miles = float(total_miles)

        if remaining_minutes <= 0:
            return

        # Average route speed for this leg.
        miles_per_minute = (
            remaining_miles / remaining_minutes
            if remaining_minutes > 0
            else 0
        )

        while remaining_minutes > 0:
            self.start_shift_if_needed()

            # 70-hour cycle exhausted
            if self.remaining_cycle_minutes() <= 0:
                self.take_cycle_restart(location)
                continue

            # 11-hour driving limit or 14-hour window exhausted
            if (
                self.remaining_driving_minutes() <= 0
                or self.remaining_window_minutes() <= 0
            ):
                self.take_daily_rest(location)
                continue

            # 8 cumulative driving hours reached
            if self.driving_since_break >= BREAK_TRIGGER:
                self.take_break(location)
                continue

            remaining_until_break = (
                BREAK_TRIGGER
                - self.driving_since_break
            )

            # Determine how much farther we may travel
            # before a fuel stop is required.
            miles_until_fuel = max(
                0,
                FUEL_INTERVAL - self.miles_since_fuel,
            )

            # If another full minute of driving would cross
            # the 1,000-mile fuel interval, fuel now.
            if (
                miles_per_minute > 0
                and 0 < miles_until_fuel < miles_per_minute
            ):
                self.take_fuel_stop(location)
                continue

            if miles_until_fuel <= 0:
                self.take_fuel_stop(location)
                continue

            if miles_per_minute > 0:
                minutes_until_fuel = max(
                    1,
                    int(
                        miles_until_fuel
                        / miles_per_minute
                    ),
                )
            else:
                minutes_until_fuel = remaining_minutes

            allowed_minutes = min(
                remaining_minutes,
                self.remaining_driving_minutes(),
                self.remaining_window_minutes(),
                self.remaining_cycle_minutes(),
                remaining_until_break,
                minutes_until_fuel,
            )

            if allowed_minutes <= 0:
                if self.miles_since_fuel >= FUEL_INTERVAL:
                    self.take_fuel_stop(location)
                    continue

                if self.driving_since_break >= BREAK_TRIGGER:
                    self.take_break(location)
                    continue

                if (
                    self.remaining_driving_minutes() <= 0
                    or self.remaining_window_minutes() <= 0
                ):
                    self.take_daily_rest(location)
                    continue

                if self.remaining_cycle_minutes() <= 0:
                    self.take_cycle_restart(location)
                    continue

                raise RuntimeError(
                    "Unable to determine legal driving interval."
                )

            miles_for_block = min(
                remaining_miles,
                miles_per_minute * allowed_minutes,
            )

            self.add_event(
                DutyStatus.DRIVING,
                allowed_minutes,
                "Driving",
                location,
                miles_for_block,
            )

            remaining_minutes -= allowed_minutes
            remaining_miles -= miles_for_block

            # Fuel once threshold is reached, but don't add
            # a pointless fuel stop after the trip leg ends.
            if (
                remaining_minutes > 0
                and self.miles_since_fuel >= FUEL_INTERVAL - 0.01
            ):
                self.take_fuel_stop(location)

    def ensure_cycle_for_driving(
        self,
        location: str | None = None,
    ):
        if self.remaining_cycle_minutes() <= 0:
            self.take_cycle_restart(location)

    def take_fuel_stop(
        self,
        location: str | None = None,
    ):
        self.add_event(
            DutyStatus.ON_DUTY,
            FUEL_DURATION,
            "Fuel stop",
            location,
        )

        self.miles_since_fuel = 0.0

        # 30 consecutive non-driving minutes also
        # satisfies the break requirement.
        self.driving_since_break = 0