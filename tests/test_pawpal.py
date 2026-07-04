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
