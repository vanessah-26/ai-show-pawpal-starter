from pawpal_system import User, Pet, Task, Scheduler

# ── Owner & Pets ──────────────────────────────────────────────────────────────

owner = User(name="Alex", available_time_start="08:00", available_time_end="18:00")
buddy = Pet(name="Buddy", species="dog", pet_id="buddy", breed="Labrador", age_years=4)
mochi = Pet(name="Mochi", species="cat", pet_id="mochi", breed="Siamese", age_years=2)

scheduler = Scheduler(user=owner, pet=buddy)
scheduler.add_pet(mochi)

# ── Normal tasks ──────────────────────────────────────────────────────────────

scheduler.add_task(Task(
    task_id="t1",
    name="Morning Walk",
    category="walk",
    duration_min=30,
    priority=5,
    pet_id="buddy",
    fixed_start_time="08:00",
))

scheduler.add_task(Task(
    task_id="t2",
    name="Mochi Feeding",
    category="feeding",
    duration_min=10,
    priority=5,
    pet_id="mochi",
    earliest_start="08:30",
    latest_end="09:30",
))

# ── Conflicting tasks (same fixed time) ───────────────────────────────────────
# Buddy Medication starts at 08:00 — same as Morning Walk (30 min), so they overlap.
# Grooming also starts at 08:10, which falls inside Morning Walk's window.

scheduler.add_task(Task(
    task_id="t3",
    name="Buddy Medication",
    category="meds",
    duration_min=5,
    priority=5,
    pet_id="buddy",
    fixed_start_time="08:00",   # conflicts with Morning Walk (08:00–08:30)
))

scheduler.add_task(Task(
    task_id="t4",
    name="Grooming",
    category="grooming",
    duration_min=20,
    priority=2,
    pet_id="buddy",
    fixed_start_time="08:10",   # also conflicts with Morning Walk (08:00–08:30)
))

# ── Conflict Detection ────────────────────────────────────────────────────────

print("=" * 52)
print("  Conflict Warnings")
print("=" * 52)

warnings = scheduler.conflict_warnings()

if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# ── Show what a clean schedule looks like without the conflicting tasks ────────

print()
print("=" * 52)
print("  Removing conflicting tasks and rescheduling")
print("=" * 52)

scheduler.remove_task("t3")   # deactivate Buddy Medication
scheduler.remove_task("t4")   # deactivate Grooming

warnings_after = scheduler.conflict_warnings()
print(f"  Warnings after fix: {len(warnings_after)} (cleared)")

scheduler.add_task(Task(
    task_id="t3b",
    name="Buddy Medication",
    category="meds",
    duration_min=5,
    priority=5,
    pet_id="buddy",
    fixed_start_time="09:00",   # moved to a clear slot
))

plan = scheduler.generate_daily_plan()

print()
print("=" * 52)
print("  PawPal+  —  Today's Schedule (conflict-free)")
print("=" * 52)
for item in plan:
    print(f"  {item.start} – {item.end}  [{item.task.pet_id}] {item.task.name}")
print(f"  {len(plan)} tasks scheduled")
print("=" * 52)
