from __future__ import annotations
from datetime import datetime, time
from typing import Any


def _parse_time(value: str, field: str = "time") -> time:
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise ValueError(f"{field} must be 'HH:MM', got {value!r}")


def _time_to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _minutes_to_time_str(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


class User:
    def __init__(
        self,
        name: str,
        available_time_start: str,
        available_time_end: str,
        user_id: str | None = None,
        preferences: dict | None = None,
        timezone: str | None = None,
    ):
        _parse_time(available_time_start, "available_time_start")
        _parse_time(available_time_end, "available_time_end")
        self.user_id = user_id
        self.name = name
        self.available_time_start = available_time_start
        self.available_time_end = available_time_end
        self.preferences = preferences or {}
        self.timezone = timezone

    def get_available_minutes(self) -> int:
        start = _time_to_minutes(_parse_time(self.available_time_start))
        end = _time_to_minutes(_parse_time(self.available_time_end))
        return end - start

    def update_availability(self, start: str, end: str) -> None:
        _parse_time(start, "start")
        _parse_time(end, "end")
        self.available_time_start = start
        self.available_time_end = end

    def add_preference(self, key: str, value: Any) -> None:
        self.preferences[key] = value

    def remove_preference(self, key: str) -> None:
        self.preferences.pop(key, None)


class Pet:
    def __init__(
        self,
        name: str,
        species: str,
        pet_id: str | None = None,
        breed: str | None = None,
        age_years: int | None = None,
        weight_lbs: float | None = None,
        notes: str | None = None,
        care_constraints: dict | None = None,
    ):
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.breed = breed
        self.age_years = age_years
        self.weight_lbs = weight_lbs
        self.notes = notes
        self.care_constraints = care_constraints or {}

    def update_profile(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Pet has no attribute {key!r}")
            setattr(self, key, value)

    def add_constraint(self, key: str, value: Any) -> None:
        self.care_constraints[key] = value

    def summary(self) -> str:
        parts = [f"{self.name} ({self.species}"]
        if self.breed:
            parts.append(f", {self.breed}")
        if self.age_years is not None:
            parts.append(f", {self.age_years}yr")
        if self.weight_lbs is not None:
            parts.append(f", {self.weight_lbs}lbs")
        parts.append(")")
        return "".join(parts)


class Task:
    def __init__(
        self,
        task_id: str,
        name: str,
        category: str,
        duration_min: int,
        priority: int,
        frequency: str = "daily",
        fixed_start_time: str | None = None,
        earliest_start: str | None = None,
        latest_end: str | None = None,
        can_split: bool = False,
        notes: str | None = None,
        pet_id: str | None = None,
        active: bool = True,
        completed: bool = False,
    ):
        for field, val in [
            ("fixed_start_time", fixed_start_time),
            ("earliest_start", earliest_start),
            ("latest_end", latest_end),
        ]:
            if val is not None:
                _parse_time(val, field)

        self.task_id = task_id
        self.name = name
        self.category = category
        self.duration_min = duration_min
        self.priority = priority
        self.frequency = frequency
        self.fixed_start_time = fixed_start_time
        self.earliest_start = earliest_start
        self.latest_end = latest_end
        self.can_split = can_split
        self.notes = notes
        self.pet_id = pet_id
        self.active = active
        self.completed = completed

    def mark_complete(self) -> None:
        self.completed = True

    def is_fixed_time(self) -> bool:
        return self.fixed_start_time is not None

    def requires_time_window(self) -> bool:
        return self.earliest_start is not None or self.latest_end is not None

    def fits_in_window(self, start_time: str, end_time: str) -> bool:
        window_start = _time_to_minutes(_parse_time(start_time))
        window_end = _time_to_minutes(_parse_time(end_time))
        effective_start = window_start
        effective_end = window_end
        if self.earliest_start:
            effective_start = max(effective_start, _time_to_minutes(_parse_time(self.earliest_start)))
        if self.latest_end:
            effective_end = min(effective_end, _time_to_minutes(_parse_time(self.latest_end)))
        return effective_end - effective_start >= self.duration_min

    def update(self, **kwargs) -> None:
        time_fields = {"fixed_start_time", "earliest_start", "latest_end"}
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Task has no attribute {key!r}")
            if key in time_fields and value is not None:
                _parse_time(value, key)
            setattr(self, key, value)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "category": self.category,
            "duration_min": self.duration_min,
            "priority": self.priority,
            "frequency": self.frequency,
            "fixed_start_time": self.fixed_start_time,
            "earliest_start": self.earliest_start,
            "latest_end": self.latest_end,
            "can_split": self.can_split,
            "notes": self.notes,
            "pet_id": self.pet_id,
            "active": self.active,
            "completed": self.completed,
        }

    @staticmethod
    def from_dict(data: dict) -> Task:
        return Task(
            task_id=data["task_id"],
            name=data["name"],
            category=data["category"],
            duration_min=data["duration_min"],
            priority=data["priority"],
            frequency=data.get("frequency", "daily"),
            fixed_start_time=data.get("fixed_start_time"),
            earliest_start=data.get("earliest_start"),
            latest_end=data.get("latest_end"),
            can_split=data.get("can_split", False),
            notes=data.get("notes"),
            pet_id=data.get("pet_id"),
            active=data.get("active", True),
            completed=data.get("completed", False),
        )


class ScheduledItem:
    def __init__(self, task: Task, start: str, end: str):
        self.task = task
        self.start = start
        self.end = end

    def overlaps(self, other: ScheduledItem) -> bool:
        a_start = _time_to_minutes(_parse_time(self.start))
        a_end = _time_to_minutes(_parse_time(self.end))
        b_start = _time_to_minutes(_parse_time(other.start))
        b_end = _time_to_minutes(_parse_time(other.end))
        return a_start < b_end and b_start < a_end

    def duration(self) -> int:
        return _time_to_minutes(_parse_time(self.end)) - _time_to_minutes(_parse_time(self.start))


class Scheduler:
    def __init__(self, user: User, pet: Pet | None = None):
        self.user = user
        self.pets: list[Pet] = [pet] if pet else []
        self.tasks: dict[str, Task] = {}  # keyed by task_id for O(1) lookup
        self.schedule: list[ScheduledItem] = []
        self.explanations: list[str] = []

    @property
    def active_tasks(self) -> list[Task]:
        return [t for t in self.tasks.values() if t.active]

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        self.tasks[task.task_id] = task

    def edit_task(self, task_id: str, **updates) -> None:
        if task_id not in self.tasks:
            raise KeyError(f"No task with id {task_id!r}")
        self.tasks[task_id].update(**updates)

    def remove_task(self, task_id: str) -> None:
        if task_id not in self.tasks:
            raise KeyError(f"No task with id {task_id!r}")
        self.tasks[task_id].active = False

    def generate_daily_plan(self, date: str | None = None) -> list[ScheduledItem]:
        self.reject_if_impossible()
        sorted_tasks = self.sort_tasks(self.active_tasks)

        avail_start = _time_to_minutes(_parse_time(self.user.available_time_start))
        avail_end = _time_to_minutes(_parse_time(self.user.available_time_end))

        occupied: list[tuple[int, int]] = []
        plan: list[ScheduledItem] = []

        for task in sorted_tasks:
            if task.is_fixed_time():
                start = _time_to_minutes(_parse_time(task.fixed_start_time))
                end = start + task.duration_min
                occupied.append((start, end))
                plan.append(ScheduledItem(task, _minutes_to_time_str(start), _minutes_to_time_str(end)))
            else:
                candidate = avail_start
                if task.earliest_start:
                    candidate = max(candidate, _time_to_minutes(_parse_time(task.earliest_start)))

                # advance past any occupied slots that would conflict
                changed = True
                while changed:
                    changed = False
                    for occ_start, occ_end in occupied:
                        if candidate < occ_end and candidate + task.duration_min > occ_start:
                            candidate = occ_end
                            changed = True

                end = candidate + task.duration_min

                if task.latest_end and end > _time_to_minutes(_parse_time(task.latest_end)):
                    continue
                if end > avail_end:
                    continue

                occupied.append((candidate, end))
                plan.append(ScheduledItem(task, _minutes_to_time_str(candidate), _minutes_to_time_str(end)))

        plan.sort(key=lambda s: _time_to_minutes(_parse_time(s.start)))
        self.schedule = plan
        return plan

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda t: (
                not t.is_fixed_time(),  # fixed-time tasks first
                -t.priority,            # higher priority next
                t.duration_min,         # shorter tasks among equal priority
            ),
        )

    def validate_no_overlap(self, plan: list[ScheduledItem]) -> bool:
        for i, a in enumerate(plan):
            for b in plan[i + 1:]:
                if a.overlaps(b):
                    return False
        return True

    def validate_fits_availability(self, plan: list[ScheduledItem]) -> bool:
        avail_start = _time_to_minutes(_parse_time(self.user.available_time_start))
        avail_end = _time_to_minutes(_parse_time(self.user.available_time_end))
        for item in plan:
            if _time_to_minutes(_parse_time(item.start)) < avail_start:
                return False
            if _time_to_minutes(_parse_time(item.end)) > avail_end:
                return False
        return True

    def validate_all_required_scheduled(self, plan: list[ScheduledItem]) -> bool:
        scheduled_ids = {item.task.task_id for item in plan}
        return all(t.task_id in scheduled_ids for t in self.active_tasks)

    def reject_if_impossible(self) -> None:
        available = self.user.get_available_minutes()
        avail_start = _time_to_minutes(_parse_time(self.user.available_time_start))
        avail_end = _time_to_minutes(_parse_time(self.user.available_time_end))

        total_needed = sum(t.duration_min for t in self.active_tasks)
        if total_needed > available:
            raise ValueError(
                f"Tasks require {total_needed} min but only {available} min available."
            )

        for task in self.active_tasks:
            if task.is_fixed_time():
                start = _time_to_minutes(_parse_time(task.fixed_start_time))
                end = start + task.duration_min
                if start < avail_start or end > avail_end:
                    raise ValueError(
                        f"Task '{task.name}' is fixed at {task.fixed_start_time} "
                        f"but falls outside availability window."
                    )

    def explain_plan(self, plan: list[ScheduledItem]) -> str:
        if not plan:
            return "No tasks were scheduled."
        lines = ["Daily plan:"]
        for item in plan:
            task = item.task
            reasons = []
            if task.is_fixed_time():
                reasons.append("fixed time")
            elif task.priority >= 4:
                reasons.append("high priority")
            if task.requires_time_window():
                reasons.append("time window")
            suffix = f"  ← {', '.join(reasons)}" if reasons else ""
            lines.append(f"  {item.start}–{item.end}  {task.name}{suffix}")
        return "\n".join(lines)
