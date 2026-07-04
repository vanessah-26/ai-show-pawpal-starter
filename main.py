from pawpal_system import User, Pet, Task, Scheduler

# ── Owner ────────────────────────────────────────────────────────────────────

owner = User(
    name="Alex",
    available_time_start="08:00",
    available_time_end="18:00",
)

# ── Pets ─────────────────────────────────────────────────────────────────────

buddy = Pet(
    name="Buddy",
    species="dog",
    breed="Labrador",
    age_years=4,
    weight_lbs=65.0,
    care_constraints={"max_walk_minutes": 45},
)

mochi = Pet(
    name="Mochi",
    species="cat",
    breed="Siamese",
    age_years=2,
    notes="Anxious around loud noises",
)

# ── Scheduler ─────────────────────────────────────────────────────────────────

scheduler = Scheduler(user=owner, pet=buddy)
scheduler.add_pet(mochi)

# ── Tasks ─────────────────────────────────────────────────────────────────────

scheduler.add_task(Task(
    task_id="t1",
    name="Morning Walk",
    category="walk",
    duration_min=30,
    priority=5,
    pet_id=buddy.pet_id,
    fixed_start_time="08:00",
))

scheduler.add_task(Task(
    task_id="t2",
    name="Mochi Feeding",
    category="feeding",
    duration_min=10,
    priority=5,
    pet_id=mochi.pet_id,
    earliest_start="08:30",
    latest_end="09:30",
))

scheduler.add_task(Task(
    task_id="t3",
    name="Buddy Medication",
    category="meds",
    duration_min=5,
    priority=5,
    pet_id=buddy.pet_id,
    fixed_start_time="09:00",
))

scheduler.add_task(Task(
    task_id="t4",
    name="Afternoon Walk",
    category="walk",
    duration_min=45,
    priority=4,
    pet_id=buddy.pet_id,
    earliest_start="15:00",
    latest_end="17:00",
))

scheduler.add_task(Task(
    task_id="t5",
    name="Grooming",
    category="grooming",
    duration_min=20,
    priority=2,
    pet_id=buddy.pet_id,
))

# ── Generate & Print ──────────────────────────────────────────────────────────

plan = scheduler.generate_daily_plan()

print("=" * 44)
print("       PawPal+  —  Today's Schedule")
print("=" * 44)
print(f"  Owner : {owner.name}")
print(f"  Pets  : {buddy.summary()}, {mochi.summary()}")
print(f"  Hours : {owner.available_time_start} – {owner.available_time_end}")
print("-" * 44)

for item in plan:
    pet_label = f"[{item.task.pet_id}] " if item.task.pet_id else ""
    print(f"  {item.start} – {item.end}  {pet_label}{item.task.name}")

print("-" * 44)
print(f"  {len(plan)} of {len(scheduler.active_tasks)} tasks scheduled")
print()
print(scheduler.explain_plan(plan))
print("=" * 44)
