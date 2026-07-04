# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:
<!-- 
```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00, Morning walk (30 min) [priority: high]
#   09:00, Feeding (10 min) [priority: high]
#   ...
``` -->

```
============================================
       PawPal+: Today's Schedule
============================================
  Owner : Alex
  Pets  : Buddy (dog, Labrador, 4yr, 65.0lbs), Mochi (cat, Siamese, 2yr)
  Hours : 08:00 – 18:00
--------------------------------------------
  08:00 – 08:30  Morning Walk
  08:30 – 08:40  Mochi Feeding
  08:40 – 09:00  Grooming
  09:00 – 09:05  Buddy Medication
  15:00 – 15:45  Afternoon Walk
--------------------------------------------
  5 of 5 tasks scheduled

Daily plan:
  08:00–08:30  Morning Walk  ← fixed time
  08:30–08:40  Mochi Feeding  ← high priority, time window
  08:40–09:00  Grooming
  09:00–09:05  Buddy Medication  ← fixed time
  15:00–15:45  Afternoon Walk  ← high priority, time window
============================================
```


## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| **Sort by priority / duration** | `Scheduler.sort_tasks()` | Fixed-time tasks always first, then priority descending, then shorter duration as tiebreaker |
| **Sort by time of day** | `Scheduler.sort_by_time()` | Lambda key on `fixed_start_time or earliest_start or "23:59"`, HH:MM strings are lexicographically ordered so no parsing needed |
| **Filter by pet** | `Scheduler.tasks_for_pet(pet_id)` | Returns active tasks whose `pet_id` matches; use with `Pet.pet_id` |
| **Filter by pet name** | `Scheduler.filter_by_pet_name(name)` | Case-insensitive name lookup; resolves to `pet_id` set before filtering |
| **Filter by completion status** | `Scheduler.tasks_by_status(completed)` | Pass `completed=True` for done tasks, `False` for pending |
| **Conflict detection (raw)** | `Scheduler.detect_fixed_time_conflicts()` | Returns `list[tuple[Task, Task]]` of overlapping fixed-time pairs |
| **Conflict detection (warnings)** | `Scheduler.conflict_warnings()` | Returns human-readable warning strings; checks overlaps, single task too long, and total overbooking never raises |
| **Recurring tasks (same day)** | `Scheduler._expand_recurring_tasks()` | Expands `frequency="2x/day"` tasks into two slots before the greedy placer runs |
| **Recurring tasks (next day/week)** | `Scheduler.mark_task_complete(task_id)` | Marks a task done and auto-creates the next occurrence using `timedelta(days=1)` or `timedelta(weeks=1)` |
| **Greedy slot placement** | `Scheduler.generate_daily_plan()` | Places fixed-time tasks first, then advances a candidate pointer through `bisect`-sorted occupied slots, O(n log n) |
| **Overlap validation** | `Scheduler.validate_no_overlap(plan)` | Adjacent-pair check on sorted plan, O(n) instead of O(n²) all-pairs |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
