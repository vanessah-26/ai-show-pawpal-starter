from __future__ import annotations
from typing import Any


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
        self.user_id = user_id
        self.name = name
        self.available_time_start = available_time_start
        self.available_time_end = available_time_end
        self.preferences = preferences or {}
        self.timezone = timezone

    def get_available_minutes(self) -> int:
        pass

    def update_availability(self, start: str, end: str) -> None:
        pass

    def add_preference(self, key: str, value: Any) -> None:
        pass

    def remove_preference(self, key: str) -> None:
        pass


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
        pass

    def add_constraint(self, key: str, value: Any) -> None:
        pass

    def summary(self) -> str:
        pass


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
    ):
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

    def is_fixed_time(self) -> bool:
        pass

    def requires_time_window(self) -> bool:
        pass

    def fits_in_window(self, start_time: str, end_time: str) -> bool:
        pass

    def update(self, **kwargs) -> None:
        pass

    def to_dict(self) -> dict:
        pass

    @staticmethod
    def from_dict(data: dict) -> Task:
        pass


class ScheduledItem:
    def __init__(self, task: Task, start: str, end: str):
        self.task = task
        self.start = start
        self.end = end

    def overlaps(self, other: ScheduledItem) -> bool:
        pass

    def duration(self) -> int:
        pass


class Scheduler:
    def __init__(self, user: User, pet: Pet | None = None):
        self.user = user
        self.pet = pet
        self.tasks: list[Task] = []
        self.schedule: list[dict] = []
        self.explanations: list[str] = []

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, task_id: str, **updates) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def generate_daily_plan(self, date: str | None = None) -> list[dict]:
        pass

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def validate_no_overlap(self, plan: list[dict]) -> bool:
        pass

    def validate_fits_availability(self, plan: list[dict]) -> bool:
        pass

    def validate_all_required_scheduled(self, plan: list[dict]) -> bool:
        pass

    def reject_if_impossible(self) -> None:
        pass

    def explain_plan(self, plan: list[dict]) -> str:
        pass
