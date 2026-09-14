from datetime import datetime

from django.test import SimpleTestCase

from .services.hos import HOSPlanner
from .services.daily_logs import build_daily_logs


class HOSPlannerTests(SimpleTestCase):

    def setUp(self):
        self.start = datetime(
            2026, 9, 14, 8, 0
        )

    def test_30_minute_break_after_8_hours(self):
        planner = HOSPlanner(
            self.start,
            current_cycle_used_hours=0,
        )

        planner.drive(
            total_minutes=9 * 60,
            total_miles=540,
            location="Test route",
        )

        events = planner.get_events()

        breaks = [
            event
            for event in events
            if event["reason"]
            == "30-minute HOS break"
        ]

        self.assertEqual(
            len(breaks),
            1,
        )

        self.assertEqual(
            breaks[0]["duration_minutes"],
            30,
        )


    def test_11_hour_driving_limit(self):
        planner = HOSPlanner(
            self.start,
            current_cycle_used_hours=0,
        )

        planner.drive(
            total_minutes=12 * 60,
            total_miles=720,
            location="Test route",
        )

        events = planner.get_events()

        rests = [
            event
            for event in events
            if event["reason"]
            == "10-hour required rest"
        ]

        self.assertTrue(
            len(rests) >= 1
        )


    def test_cycle_restart_when_70_hours_used(self):
        planner = HOSPlanner(
            self.start,
            current_cycle_used_hours=70,
        )

        planner.drive(
            total_minutes=60,
            total_miles=60,
            location="Test route",
        )

        events = planner.get_events()

        restarts = [
            event
            for event in events
            if "34-hour" in event["reason"]
        ]

        self.assertEqual(
            len(restarts),
            1,
        )

        self.assertEqual(
            restarts[0]["duration_minutes"],
            34 * 60,
        )


    def test_on_duty_counts_toward_cycle(self):
        planner = HOSPlanner(
            self.start,
            current_cycle_used_hours=10,
        )

        planner.add_on_duty_stop(
            minutes=60,
            reason="Pickup",
            location="Chicago",
        )

        self.assertEqual(
            planner.cycle_used,
            11 * 60,
        )


    def test_daily_log_equals_24_hours(self):
        planner = HOSPlanner(
            self.start,
            current_cycle_used_hours=0,
        )

        planner.drive(
            total_minutes=5 * 60,
            total_miles=300,
            location="Test route",
        )

        logs = build_daily_logs(
            planner.get_events()
        )

        self.assertEqual(
            len(logs),
            1,
        )

        total_minutes = sum(
            event["duration_minutes"]
            for event
            in logs[0]["events"]
        )

        self.assertEqual(
            total_minutes,
            24 * 60,
        )


    def test_long_trip_creates_multiple_logs(self):
        planner = HOSPlanner(
            self.start,
            current_cycle_used_hours=0,
        )

        planner.drive(
            total_minutes=30 * 60,
            total_miles=1800,
            location="Long route",
        )

        logs = build_daily_logs(
            planner.get_events()
        )

        self.assertGreater(
            len(logs),
            1,
        )

        for log in logs:
            total_minutes = sum(
                event["duration_minutes"]
                for event
                in log["events"]
            )

            self.assertEqual(
                total_minutes,
                1440,
            )

    def test_driving_miles_split_across_midnight(self):
        events = [
            {
                "status": "D",
                "start": "2026-09-14T22:00:00",
                "end": "2026-09-15T02:00:00",
                "duration_minutes": 240,
                "reason": "Driving",
                "location": "Test route",
                "miles": 240,
            }
        ]

        logs = build_daily_logs(events)

        self.assertEqual(
            len(logs),
            2,
        )

        self.assertAlmostEqual(
            logs[0]["total_miles"],
            120,
            places=2,
        )

        self.assertAlmostEqual(
            logs[1]["total_miles"],
            120,
            places=2,
        )

        self.assertAlmostEqual(
            sum(
                log["total_miles"]
                for log in logs
            ),
            240,
            places=2,
        )

    def test_fuel_stop_before_1000_mile_limit(self):
        planner = HOSPlanner(
            self.start,
            current_cycle_used_hours=0,
        )

        planner.drive(
            total_minutes=20 * 60,
            total_miles=1200,
            location="Long route",
        )

        events = planner.get_events()

        fuel_stops = [
            event
            for event in events
            if event["reason"] == "Fuel stop"
        ]

        self.assertGreaterEqual(
            len(fuel_stops),
            1,
        )

        miles_before_first_fuel = 0

        for event in events:
            if event["reason"] == "Fuel stop":
                break

            if event["status"] == "D":
                miles_before_first_fuel += (
                    event["miles"]
                )

        self.assertLessEqual(
            miles_before_first_fuel,
            1000,
        )