import pytest
from pawpal_system import User, Pet, Task, Scheduler, ScheduledItem


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_user(start="08:00", end="18:00"):
    return User(name="Alex", available_time_start=start, available_time_end=end)


def make_pet(pet_id="buddy"):
    return Pet(name="Buddy", species="dog", pet_id=pet_id)


def make_task(task_id="t1", duration=30, priority=3, pet_id=None,
              fixed_start=None, earliest=None, latest=None):
    return Task(
        task_id=task_id,
        name="Morning Walk",
        category="walk",
        duration_min=duration,
        priority=priority,
        pet_id=pet_id,
        fixed_start_time=fixed_start,
        earliest_start=earliest,
        latest_end=latest,
    )


def make_scheduler(*tasks):
    s = Scheduler(user=make_user())
    for t in tasks:
        s.add_task(t)
    return s


# ── User ──────────────────────────────────────────────────────────────────────

def test_user_available_minutes():
    user = make_user("08:00", "18:00")
    assert user.get_available_minutes() == 600


def test_user_update_availability():
    user = make_user()
    user.update_availability("09:00", "17:00")
    assert user.available_time_start == "09:00"
    assert user.available_time_end == "17:00"
    assert user.get_available_minutes() == 480


def test_user_bad_time_format_raises():
    with pytest.raises(ValueError):
        make_user(start="8am")


def test_user_add_and_remove_preference():
    user = make_user()
    user.add_preference("no_evenings", True)
    assert user.preferences["no_evenings"] is True
    user.remove_preference("no_evenings")
    assert "no_evenings" not in user.preferences


def test_user_remove_missing_preference_does_not_raise():
    user = make_user()
    user.remove_preference("nonexistent")  # should not raise


# ── Pet ───────────────────────────────────────────────────────────────────────

def test_pet_summary_full():
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age_years=4, weight_lbs=65.0)
    assert pet.summary() == "Buddy (dog, Labrador, 4yr, 65.0lbs)"


def test_pet_summary_minimal():
    pet = Pet(name="Mochi", species="cat")
    assert pet.summary() == "Mochi (cat)"


def test_pet_add_constraint():
    pet = make_pet()
    pet.add_constraint("max_walk_minutes", 30)
    assert pet.care_constraints["max_walk_minutes"] == 30


def test_pet_update_profile():
    pet = make_pet()
    pet.update_profile(age_years=5, breed="Golden Retriever")
    assert pet.age_years == 5
    assert pet.breed == "Golden Retriever"


def test_pet_update_profile_unknown_key_raises():
    pet = make_pet()
    with pytest.raises(ValueError):
        pet.update_profile(unknown_field="oops")


# ── Task ──────────────────────────────────────────────────────────────────────

def test_task_mark_complete():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_is_fixed_time():
    assert make_task(fixed_start="09:00").is_fixed_time() is True
    assert make_task().is_fixed_time() is False


def test_task_requires_time_window():
    assert make_task(earliest="09:00").requires_time_window() is True
    assert make_task(latest="10:00").requires_time_window() is True
    assert make_task().requires_time_window() is False


def test_task_fits_in_window():
    task = make_task(duration=30)
    assert task.fits_in_window("08:00", "09:00") is True
    assert task.fits_in_window("08:00", "08:20") is False  # only 20 min, need 30


def test_task_fits_in_window_respects_constraints():
    task = make_task(duration=30, earliest="09:00", latest="09:45")
    assert task.fits_in_window("08:00", "18:00") is True   # 45 min window
    assert task.fits_in_window("08:00", "09:20") is False  # only 20 min after earliest


def test_task_bad_time_raises():
    with pytest.raises(ValueError):
        make_task(fixed_start="9am")


def test_task_update_valid():
    task = make_task(duration=30)
    task.update(duration_min=45, priority=5)
    assert task.duration_min == 45
    assert task.priority == 5


def test_task_update_unknown_key_raises():
    task = make_task()
    with pytest.raises(ValueError):
        task.update(nonexistent="oops")


def test_task_to_dict_and_from_dict():
    task = make_task(task_id="t1", duration=20, priority=4)
    restored = Task.from_dict(task.to_dict())
    assert restored.task_id == task.task_id
    assert restored.duration_min == task.duration_min
    assert restored.priority == task.priority
    assert restored.completed == task.completed


# ── ScheduledItem ─────────────────────────────────────────────────────────────

def test_scheduled_item_duration():
    item = ScheduledItem(task=make_task(), start="08:00", end="08:30")
    assert item.duration() == 30


def test_scheduled_item_overlaps_true():
    task = make_task()
    a = ScheduledItem(task, "08:00", "08:30")
    b = ScheduledItem(task, "08:15", "08:45")
    assert a.overlaps(b) is True


def test_scheduled_item_overlaps_false_adjacent():
    task = make_task()
    a = ScheduledItem(task, "08:00", "08:30")
    b = ScheduledItem(task, "08:30", "09:00")
    assert a.overlaps(b) is False


def test_scheduled_item_overlaps_false_separate():
    task = make_task()
    a = ScheduledItem(task, "08:00", "08:30")
    b = ScheduledItem(task, "09:00", "09:30")
    assert a.overlaps(b) is False


# ── Scheduler ─────────────────────────────────────────────────────────────────

def test_adding_task_increases_count():
    pet = make_pet()
    scheduler = Scheduler(user=make_user(), pet=pet)
    pet_task_count = lambda: sum(1 for t in scheduler.tasks.values() if t.pet_id == pet.pet_id)

    assert pet_task_count() == 0
    scheduler.add_task(make_task(task_id="t1", pet_id=pet.pet_id))
    assert pet_task_count() == 1
    scheduler.add_task(make_task(task_id="t2", pet_id=pet.pet_id))
    assert pet_task_count() == 2


def test_remove_task_sets_inactive():
    scheduler = make_scheduler(make_task("t1"))
    scheduler.remove_task("t1")
    assert scheduler.tasks["t1"].active is False
    assert scheduler.active_tasks == []


def test_remove_task_unknown_id_raises():
    scheduler = make_scheduler()
    with pytest.raises(KeyError):
        scheduler.remove_task("ghost")


def test_edit_task_updates_field():
    scheduler = make_scheduler(make_task("t1", duration=30))
    scheduler.edit_task("t1", duration_min=60)
    assert scheduler.tasks["t1"].duration_min == 60


def test_edit_task_unknown_id_raises():
    scheduler = make_scheduler()
    with pytest.raises(KeyError):
        scheduler.edit_task("ghost", duration_min=10)


def test_sort_tasks_fixed_first_then_priority():
    fixed = make_task("t1", priority=2, fixed_start="09:00")
    high  = make_task("t2", priority=5)
    low   = make_task("t3", priority=1)
    scheduler = make_scheduler(low, high, fixed)
    result = scheduler.sort_tasks([low, high, fixed])
    assert result[0].task_id == "t1"  # fixed first
    assert result[1].task_id == "t2"  # then high priority
    assert result[2].task_id == "t3"


def test_reject_if_impossible_raises():
    scheduler = Scheduler(user=make_user("08:00", "08:10"))
    scheduler.add_task(make_task("t1", duration=60))
    with pytest.raises(ValueError):
        scheduler.reject_if_impossible()


def test_reject_if_impossible_fixed_outside_window_raises():
    scheduler = make_scheduler(make_task("t1", fixed_start="06:00", duration=30))
    with pytest.raises(ValueError):
        scheduler.reject_if_impossible()


def test_validate_no_overlap_clean():
    task = make_task()
    plan = [
        ScheduledItem(task, "08:00", "08:30"),
        ScheduledItem(task, "08:30", "09:00"),
    ]
    scheduler = make_scheduler()
    assert scheduler.validate_no_overlap(plan) is True


def test_validate_no_overlap_conflict():
    task = make_task()
    plan = [
        ScheduledItem(task, "08:00", "08:30"),
        ScheduledItem(task, "08:15", "08:45"),
    ]
    scheduler = make_scheduler()
    assert scheduler.validate_no_overlap(plan) is False


def test_validate_fits_availability():
    task = make_task()
    scheduler = make_scheduler()
    in_window  = [ScheduledItem(task, "08:00", "08:30")]
    out_window = [ScheduledItem(task, "19:00", "19:30")]
    assert scheduler.validate_fits_availability(in_window) is True
    assert scheduler.validate_fits_availability(out_window) is False


def test_generate_daily_plan_order_and_count():
    t1 = make_task("t1", duration=30, priority=5, fixed_start="08:00")
    t2 = make_task("t2", duration=20, priority=3)
    t3 = make_task("t3", duration=15, priority=1)
    scheduler = make_scheduler(t1, t2, t3)
    plan = scheduler.generate_daily_plan()
    assert len(plan) == 3
    assert plan[0].start == "08:00"          # fixed task anchors first slot
    assert scheduler.validate_no_overlap(plan) is True
    assert scheduler.validate_fits_availability(plan) is True


def test_add_pet_increases_count():
    scheduler = Scheduler(user=make_user())
    assert len(scheduler.pets) == 0
    scheduler.add_pet(make_pet("p1"))
    assert len(scheduler.pets) == 1
    scheduler.add_pet(make_pet("p2"))
    assert len(scheduler.pets) == 2


# ── Sorting Correctness (chronological) ──────────────────────────────────────
# sort_by_time orders tasks by fixed_start_time, falling back to earliest_start,
# then a "23:59" sentinel for tasks with no time anchor at all.

def test_sort_by_time_chronological_order():
    # Three tasks with distinct fixed start times — expect earliest first.
    early  = make_task("t1", fixed_start="08:00")
    midday = make_task("t2", fixed_start="12:00")
    late   = make_task("t3", fixed_start="17:00")
    scheduler = make_scheduler(early, midday, late)

    result = scheduler.sort_by_time([late, early, midday])  # intentionally shuffled

    assert [t.task_id for t in result] == ["t1", "t2", "t3"]


def test_sort_by_time_falls_back_to_earliest_start():
    # A task with only earliest_start should sort by that value,
    # not be treated as having no anchor.
    fixed   = make_task("t1", fixed_start="09:00")
    windowed = make_task("t2", earliest="07:00")  # no fixed_start, but has earliest
    scheduler = make_scheduler(fixed, windowed)

    result = scheduler.sort_by_time([fixed, windowed])

    # windowed has earliest_start "07:00" < fixed "09:00", so windowed comes first
    assert result[0].task_id == "t2"
    assert result[1].task_id == "t1"


def test_sort_by_time_no_anchor_sorts_last():
    # A task with neither fixed_start_time nor earliest_start gets the "23:59"
    # sentinel, so it always sorts after any task with a real time.
    anchored  = make_task("t1", fixed_start="10:00")
    unanchored = make_task("t2")  # no time constraints at all
    scheduler = make_scheduler(anchored, unanchored)

    result = scheduler.sort_by_time([unanchored, anchored])

    assert result[0].task_id == "t1"
    assert result[1].task_id == "t2"


# ── Recurrence Logic ─────────────────────────────────────────────────────────
# mark_task_complete flags the original done and auto-creates the next
# occurrence for daily/weekly tasks, but returns None for one-off tasks.

def make_recurring_task(task_id="t1", frequency="daily", duration=30):
    return Task(
        task_id=task_id,
        name="Walk",
        category="walk",
        duration_min=duration,
        priority=3,
        frequency=frequency,
    )


def test_mark_complete_sets_completed_flag():
    scheduler = make_scheduler(make_recurring_task("t1"))
    scheduler.mark_task_complete("t1", today="2025-06-01")

    assert scheduler.tasks["t1"].completed is True


def test_mark_complete_daily_creates_tomorrow():
    # Completing a daily task on 2025-06-01 should create a new task
    # with due_date "2025-06-02" and task_id "t1_2025-06-02".
    scheduler = make_scheduler(make_recurring_task("t1", frequency="daily"))
    new_task = scheduler.mark_task_complete("t1", today="2025-06-01")

    assert new_task is not None
    assert new_task.task_id == "t1_2025-06-02"
    assert new_task.due_date == "2025-06-02"
    assert new_task.completed is False
    assert new_task.active is True
    assert "t1_2025-06-02" in scheduler.tasks


def test_mark_complete_weekly_creates_seven_days_later():
    # Weekly task completed on 2025-06-01 → next due 2025-06-08.
    scheduler = make_scheduler(make_recurring_task("t1", frequency="weekly"))
    new_task = scheduler.mark_task_complete("t1", today="2025-06-01")

    assert new_task is not None
    assert new_task.due_date == "2025-06-08"
    assert new_task.task_id == "t1_2025-06-08"


def test_mark_complete_one_off_returns_none():
    # A task with frequency="once" (not daily or weekly) should return None —
    # no follow-up task is created.
    task = Task(
        task_id="t1", name="Vet visit", category="medical",
        duration_min=60, priority=5, frequency="once",
    )
    scheduler = make_scheduler(task)
    result = scheduler.mark_task_complete("t1", today="2025-06-01")

    assert result is None
    assert "t1_2025-06-02" not in scheduler.tasks


def test_mark_complete_unknown_id_raises():
    scheduler = make_scheduler()
    with pytest.raises(KeyError):
        scheduler.mark_task_complete("ghost", today="2025-06-01")


# ── Conflict Detection ────────────────────────────────────────────────────────
# detect_fixed_time_conflicts returns (Task, Task) pairs that overlap.
# conflict_warnings returns human-readable strings for all conflict types.

def test_detect_no_conflict_when_tasks_are_separate():
    t1 = make_task("t1", fixed_start="08:00", duration=30)  # 08:00–08:30
    t2 = make_task("t2", fixed_start="09:00", duration=30)  # 09:00–09:30
    scheduler = make_scheduler(t1, t2)

    assert scheduler.detect_fixed_time_conflicts() == []


def test_detect_conflict_same_start_time():
    # Two tasks fixed to the exact same start time must be flagged.
    t1 = make_task("t1", fixed_start="09:00", duration=30)
    t2 = make_task("t2", fixed_start="09:00", duration=30)
    scheduler = make_scheduler(t1, t2)

    conflicts = scheduler.detect_fixed_time_conflicts()

    assert len(conflicts) == 1
    ids = {conflicts[0][0].task_id, conflicts[0][1].task_id}
    assert ids == {"t1", "t2"}


def test_detect_conflict_partial_overlap():
    # t1 runs 09:00–09:30, t2 runs 09:15–09:45 → they overlap by 15 min.
    t1 = make_task("t1", fixed_start="09:00", duration=30)
    t2 = make_task("t2", fixed_start="09:15", duration=30)
    scheduler = make_scheduler(t1, t2)

    conflicts = scheduler.detect_fixed_time_conflicts()

    assert len(conflicts) == 1


def test_detect_no_conflict_adjacent_tasks():
    # Adjacent tasks (one ends exactly when the next begins) must NOT conflict.
    t1 = make_task("t1", fixed_start="08:00", duration=30)  # ends 08:30
    t2 = make_task("t2", fixed_start="08:30", duration=30)  # starts 08:30
    scheduler = make_scheduler(t1, t2)

    assert scheduler.detect_fixed_time_conflicts() == []


def test_conflict_warnings_includes_fixed_overlap_message():
    # conflict_warnings should mention both task names in its output string.
    t1 = make_task("t1", fixed_start="09:00", duration=30)
    t2 = make_task("t2", fixed_start="09:00", duration=30)
    scheduler = make_scheduler(t1, t2)

    warnings = scheduler.conflict_warnings()

    assert any("t1".lower() in w.lower() or "morning walk" in w.lower() for w in warnings)
    assert len(warnings) >= 1


def test_conflict_warnings_overbooked():
    # When total task time exceeds availability, a warning must appear.
    scheduler = Scheduler(user=make_user("08:00", "08:20"))  # only 20 min
    scheduler.add_task(make_task("t1", duration=30))         # needs 30 min

    warnings = scheduler.conflict_warnings()

    assert any("overbooked" in w.lower() or "too long" in w.lower() for w in warnings)


def test_conflict_warnings_empty_when_clean():
    # A single short task well within the window should produce no warnings.
    scheduler = make_scheduler(make_task("t1", duration=30))  # 08:00–18:00, needs 30

    assert scheduler.conflict_warnings() == []
