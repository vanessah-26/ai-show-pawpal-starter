from __future__ import annotations
import bisect
from datetime import date, datetime, time, timedelta
from typing import Any


def _parse_time(value: str, field: str = "time") -> time:
    """Parse a 'HH:MM' string into a time object, raising ValueError on bad input."""
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise ValueError(f"{field} must be 'HH:MM', got {value!r}")


def _time_to_minutes(t: time) -> int:
    """Convert a time object to total minutes since midnight."""
    return t.hour * 60 + t.minute


def _minutes_to_time_str(minutes: int) -> str:
    """Convert total minutes since midnight to a 'HH:MM' string."""
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
        """Return total minutes between availability start and end."""
        start = _time_to_minutes(_parse_time(self.available_time_start))
        end = _time_to_minutes(_parse_time(self.available_time_end))
        return end - start

    def update_availability(self, start: str, end: str) -> None:
        """Validate and update the owner's available time window."""
        _parse_time(start, "start")
        _parse_time(end, "end")
        self.available_time_start = start
        self.available_time_end = end

    def add_preference(self, key: str, value: Any) -> None:
        """Add or overwrite a scheduling preference by key."""
        self.preferences[key] = value

    def remove_preference(self, key: str) -> None:
        """Remove a preference by key, silently ignoring missing keys."""
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
        """Update pet attributes by name, raising ValueError for unknown fields."""
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Pet has no attribute {key!r}")
            setattr(self, key, value)

    def add_constraint(self, key: str, value: Any) -> None:
        """Add or overwrite a care constraint (e.g. max_walk_minutes)."""
        self.care_constraints[key] = value

    def summary(self) -> str:
        """Return a short human-readable description of the pet."""
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
        due_date: str | None = None,
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
        self.due_date = due_date

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def is_fixed_time(self) -> bool:
        """Return True if the task must start at a specific time."""
        return self.fixed_start_time is not None

    def requires_time_window(self) -> bool:
        """Return True if the task has an earliest_start or latest_end constraint."""
        return self.earliest_start is not None or self.latest_end is not None

    def fits_in_window(self, start_time: str, end_time: str) -> bool:
        """Return True if the task's duration fits within the given time window."""
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
        """Update task attributes by name, re-validating any time string fields."""
        time_fields = {"fixed_start_time", "earliest_start", "latest_end"}
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Task has no attribute {key!r}")
            if key in time_fields and value is not None:
                _parse_time(value, key)
            setattr(self, key, value)

    def to_dict(self) -> dict:
        """Serialize the task to a dictionary for storage or session state."""
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
            "due_date": self.due_date,
        }

    @staticmethod
    def from_dict(data: dict) -> Task:
        """Reconstruct a Task from a dictionary produced by to_dict."""
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
            due_date=data.get("due_date"),
        )


class ScheduledItem:
    def __init__(self, task: Task, start: str, end: str):
        self.task = task
        self.start = start
        self.end = end

    def overlaps(self, other: ScheduledItem) -> bool:
        """Return True if this scheduled item's time range overlaps with another's."""
        a_start = _time_to_minutes(_parse_time(self.start))
        a_end = _time_to_minutes(_parse_time(self.end))
        b_start = _time_to_minutes(_parse_time(other.start))
        b_end = _time_to_minutes(_parse_time(other.end))
        return a_start < b_end and b_start < a_end

    def duration(self) -> int:
        """Return the length of this scheduled slot in minutes."""
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
        """Return all tasks that are active and not yet completed."""
        return [t for t in self.tasks.values() if t.active and not t.completed]

    def tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Return all active tasks assigned to a specific pet."""
        return [t for t in self.active_tasks if t.pet_id == pet_id]

    def tasks_by_status(self, completed: bool) -> list[Task]:
        """Return all tasks (active or not) filtered by completion status."""
        return [t for t in self.tasks.values() if t.completed == completed]

    def detect_fixed_time_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of fixed-time tasks whose scheduled windows overlap.

        Compares every pair of fixed-time tasks using interval overlap logic
        (a_start < b_end and b_start < a_end). O(n²) over fixed tasks only,
        which is acceptable since most days have few fixed-time items.
        """
        fixed = [t for t in self.active_tasks if t.is_fixed_time()]
        conflicts = []
        for i, a in enumerate(fixed):
            for b in fixed[i + 1:]:
                a_start = _time_to_minutes(_parse_time(a.fixed_start_time))
                a_end = a_start + a.duration_min
                b_start = _time_to_minutes(_parse_time(b.fixed_start_time))
                b_end = b_start + b.duration_min
                if a_start < b_end and b_start < a_end:
                    conflicts.append((a, b))
        return conflicts

    def conflict_warnings(self) -> list[str]:
        """Return human-readable warnings for scheduling conflicts without raising.

        Checks three conditions: (1) fixed-time tasks that overlap each other,
        (2) a single task whose duration exceeds total availability, and
        (3) total active task time exceeding the availability window.
        Returns an empty list if no issues are found — never raises.
        """
        warnings = []

        # fixed-time tasks that overlap each other
        for a, b in self.detect_fixed_time_conflicts():
            warnings.append(
                f"⚠ Time conflict: '{a.name}' ({a.fixed_start_time}, {a.duration_min} min) "
                f"overlaps '{b.name}' ({b.fixed_start_time}, {b.duration_min} min)"
            )

        # any single task longer than the entire availability window
        available = self.user.get_available_minutes()
        for task in self.active_tasks:
            if task.duration_min > available:
                warnings.append(
                    f"⚠ Task too long: '{task.name}' needs {task.duration_min} min "
                    f"but only {available} min available"
                )

        # total active task time exceeds availability
        total = sum(t.duration_min for t in self.active_tasks)
        if total > available:
            warnings.append(
                f"⚠ Overbooked: tasks total {total} min but only {available} min available"
            )

        return warnings

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the scheduler's pet list."""
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Register a task with the scheduler, keyed by task_id."""
        self.tasks[task.task_id] = task

    def edit_task(self, task_id: str, **updates) -> None:
        """Update fields on an existing task by ID, raising KeyError if not found."""
        if task_id not in self.tasks:
            raise KeyError(f"No task with id {task_id!r}")
        self.tasks[task_id].update(**updates)

    def remove_task(self, task_id: str) -> None:
        """Deactivate a task by ID without deleting it, preserving history."""
        if task_id not in self.tasks:
            raise KeyError(f"No task with id {task_id!r}")
        self.tasks[task_id].active = False

    def mark_task_complete(self, task_id: str, today: str | None = None) -> Task | None:
        """Mark a task done and auto-create the next occurrence for recurring tasks.

        Uses timedelta: daily tasks recur tomorrow, weekly tasks recur in 7 days.
        Returns the new Task if one was created, otherwise None.
        """
        if task_id not in self.tasks:
            raise KeyError(f"No task with id {task_id!r}")

        task = self.tasks[task_id]
        task.mark_complete()

        if task.frequency not in ("daily", "weekly"):
            return None

        base_date = date.fromisoformat(today) if today else date.today()
        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_date = base_date + delta
        next_date_str = next_date.isoformat()

        new_task = Task(
            task_id=f"{task_id}_{next_date_str}",
            name=task.name,
            category=task.category,
            duration_min=task.duration_min,
            priority=task.priority,
            frequency=task.frequency,
            fixed_start_time=task.fixed_start_time,
            earliest_start=task.earliest_start,
            latest_end=task.latest_end,
            can_split=task.can_split,
            notes=task.notes,
            pet_id=task.pet_id,
            active=True,
            completed=False,
            due_date=next_date_str,
        )
        self.add_task(new_task)
        return new_task

    def _expand_recurring_tasks(self, tasks: list[Task]) -> list[Task]:
        """Expand 2x/day tasks into two scheduling instances for the same day.

        For each task with frequency '2x/day', a second copy is inserted
        immediately after the original with '_2' appended to its task_id.
        The second copy inherits all attributes but has no time constraints,
        letting the greedy placer find it a fresh slot later in the day.
        """
        expanded = []
        for task in tasks:
            expanded.append(task)
            if task.frequency == "2x/day":
                second = Task(
                    task_id=f"{task.task_id}_2",
                    name=f"{task.name} (2nd)",
                    category=task.category,
                    duration_min=task.duration_min,
                    priority=task.priority,
                    pet_id=task.pet_id,
                    active=task.active,
                )
                expanded.append(second)
        return expanded

    def generate_daily_plan(self, date: str | None = None) -> list[ScheduledItem]:
        """Build and return a conflict-free daily schedule for all active tasks."""
        self.reject_if_impossible()
        expanded = self._expand_recurring_tasks(self.active_tasks)
        sorted_tasks = self.sort_tasks(expanded)

        avail_start = _time_to_minutes(_parse_time(self.user.available_time_start))
        avail_end = _time_to_minutes(_parse_time(self.user.available_time_end))

        occupied: list[tuple[int, int]] = []
        plan: list[ScheduledItem] = []

        for task in sorted_tasks:
            if task.is_fixed_time():
                start = _time_to_minutes(_parse_time(task.fixed_start_time))
                end = start + task.duration_min
                bisect.insort(occupied, (start, end))
                plan.append(ScheduledItem(task, _minutes_to_time_str(start), _minutes_to_time_str(end)))
            else:
                candidate = avail_start
                if task.earliest_start:
                    candidate = max(candidate, _time_to_minutes(_parse_time(task.earliest_start)))

                # occupied is kept sorted via bisect.insort, so one pass is enough
                for occ_start, occ_end in occupied:
                    if candidate < occ_end and candidate + task.duration_min > occ_start:
                        candidate = occ_end

                end = candidate + task.duration_min

                if task.latest_end and end > _time_to_minutes(_parse_time(task.latest_end)):
                    continue
                if end > avail_end:
                    continue

                bisect.insort(occupied, (candidate, end))
                plan.append(ScheduledItem(task, _minutes_to_time_str(candidate), _minutes_to_time_str(end)))

        plan.sort(key=lambda s: _time_to_minutes(_parse_time(s.start)))
        self.schedule = plan
        return plan

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks: fixed-time first, then by priority descending, then shorter duration."""
        return sorted(
            tasks,
            key=lambda t: (
                not t.is_fixed_time(),  # fixed-time tasks first
                -t.priority,            # higher priority next
                t.duration_min,         # shorter tasks among equal priority
            ),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks chronologically using fixed_start_time, falling back to earliest_start.

        The lambda key `t.fixed_start_time or t.earliest_start or '23:59'` works
        because HH:MM strings are lexicographically ordered — '08:00' < '15:00'.
        Tasks with no time anchor sort last via the '23:59' sentinel.
        """
        return sorted(
            tasks,
            key=lambda t: t.fixed_start_time or t.earliest_start or "23:59",
        )

    def filter_by_pet_name(self, name: str) -> list[Task]:
        """Return active tasks assigned to a pet matching the given name (case-insensitive).

        Resolves the name to a set of pet_ids first, then filters active_tasks.
        Handles multiple pets with the same name and skips pets without a pet_id.
        """
        matching_ids = {
            p.pet_id for p in self.pets
            if p.name.lower() == name.lower() and p.pet_id
        }
        return [t for t in self.active_tasks if t.pet_id in matching_ids]

    def validate_no_overlap(self, plan: list[ScheduledItem]) -> bool:
        """Return True if no two scheduled items in the plan overlap.

        Assumes plan is sorted by start time (guaranteed by generate_daily_plan).
        Adjacent-pair check is O(n) vs the O(n²) all-pairs approach.
        """
        for a, b in zip(plan, plan[1:]):
            if a.overlaps(b):
                return False
        return True

    def validate_fits_availability(self, plan: list[ScheduledItem]) -> bool:
        """Return True if every scheduled item falls within the user's available hours."""
        avail_start = _time_to_minutes(_parse_time(self.user.available_time_start))
        avail_end = _time_to_minutes(_parse_time(self.user.available_time_end))
        for item in plan:
            if _time_to_minutes(_parse_time(item.start)) < avail_start:
                return False
            if _time_to_minutes(_parse_time(item.end)) > avail_end:
                return False
        return True

    def validate_all_required_scheduled(self, plan: list[ScheduledItem]) -> bool:
        """Return True if every active task appears in the plan."""
        scheduled_ids = {item.task.task_id for item in plan}
        return all(t.task_id in scheduled_ids for t in self.active_tasks)

    def reject_if_impossible(self) -> None:
        """Raise ValueError if active tasks cannot fit within the available time window."""
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
        """Return a human-readable summary of the plan with reasons for each slot."""
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
