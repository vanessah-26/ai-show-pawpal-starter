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

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest tests/test_pawpal.py 


# Test covered:
# User
# - test_user_available_minutes: get_available_minutes() returns correct total minutes between start and end
# - test_user_update_availability: update_availability() stores the new window and recalculates minutes
# - test_user_bad_time_format_raises: invalid format like "8am" raises ValueError
# - test_user_add_and_remove_preference: add_preference stores a key and remove_preference deletes it
# - test_user_remove_missing_preference_does_not_raise: removing a non-existent preference key is safe
#
# Pet
# - test_pet_summary_full: summary() with all fields produces the full formatted string
# - test_pet_summary_minimal: summary() with only name and species omits optional fields
# - test_pet_add_constraint: add_constraint stores a value in care_constraints
# - test_pet_update_profile: update_profile sets valid attributes by keyword
# - test_pet_update_profile_unknown_key_raises: unknown keyword raises ValueError
#
# Task
# - test_task_mark_complete: mark_complete() flips completed to True
# - test_task_is_fixed_time: returns True when fixed_start_time is set, False otherwise
# - test_task_requires_time_window: returns True when earliest_start or latest_end is set
# - test_task_fits_in_window: task fits when window >= duration, fails when window is too short
# - test_task_fits_in_window_respects_constraints: earliest_start/latest_end narrow the effective window
# - test_task_bad_time_raises: invalid time format in constructor raises ValueError
# - test_task_update_valid: update() changes non-time fields correctly
# - test_task_update_unknown_key_raises: unknown field name raises ValueError
# - test_task_to_dict_and_from_dict: round-trip serialization preserves all fields
# - test_task_update_time_field_valid: update() accepts a valid new time string for fixed_start_time
# - test_task_update_time_field_invalid_raises: update() with a bad time format raises ValueError
#
# ScheduledItem
# - test_scheduled_item_duration: duration() returns end minus start in minutes
# - test_scheduled_item_overlaps_true: partial time overlap is detected
# - test_scheduled_item_overlaps_false_adjacent: items where end == start do not overlap
# - test_scheduled_item_overlaps_false_separate: non-touching items do not overlap
#
# Scheduler — core
# - test_adding_task_increases_count: add_task grows the tasks dict
# - test_remove_task_sets_inactive: remove_task sets active=False without deleting
# - test_remove_task_unknown_id_raises: unknown ID raises KeyError
# - test_edit_task_updates_field: edit_task patches a field by task ID
# - test_edit_task_unknown_id_raises: unknown ID raises KeyError
# - test_add_pet_increases_count: add_pet grows the pets list
# - test_reject_if_impossible_raises: raises when total task minutes exceed availability
# - test_reject_if_impossible_fixed_outside_window_raises: raises when a fixed task falls outside the user's window
# - test_tasks_for_pet_returns_matching: returns only tasks whose pet_id matches
# - test_tasks_for_pet_empty_when_none_match: returns empty list when no tasks match the pet ID
# - test_tasks_by_status_incomplete: correctly splits tasks into completed vs. incomplete buckets
#
# Scheduler — sorting
# - test_sort_tasks_fixed_first_then_priority: fixed-time tasks come first, then by priority descending
# - test_sort_by_time_chronological_order: sort_by_time orders tasks by fixed_start_time ascending
# - test_sort_by_time_falls_back_to_earliest_start: uses earliest_start when no fixed_start_time
# - test_sort_by_time_no_anchor_sorts_last: tasks with no time anchor sort last via "23:59" sentinel
#
# Scheduler — recurrence
# - test_mark_complete_sets_completed_flag: original task is marked completed=True
# - test_mark_complete_daily_creates_tomorrow: daily task creates a new task due the next day
# - test_mark_complete_weekly_creates_seven_days_later: weekly task creates a new task due in 7 days
# - test_mark_complete_one_off_returns_none: non-recurring frequency returns None, no new task created
# - test_mark_complete_unknown_id_raises: unknown task ID raises KeyError
#
# Scheduler — 2x/day expansion
# - test_expand_recurring_2x_day_produces_two_entries: a 2x/day task expands to two list entries
# - test_expand_recurring_2x_day_copy_has_no_time_constraints: the second copy has no fixed_start_time, earliest_start, or latest_end
# - test_expand_recurring_non_2x_day_unchanged: non-2x/day tasks are returned as-is
#
# Scheduler — daily plan generation
# - test_generate_daily_plan_order_and_count: plan has correct count, fixed task anchors first slot, no overlaps
# - test_generate_plan_respects_earliest_start: floating task is not placed before its earliest_start
# - test_generate_plan_skips_task_exceeding_latest_end: task is silently dropped when it can't finish before latest_end
# - test_generate_plan_skips_task_exceeding_avail_end: task is silently dropped when it would run past availability end
#
# Scheduler — conflict detection
# - test_detect_no_conflict_when_tasks_are_separate: non-overlapping fixed tasks return no conflicts
# - test_detect_conflict_same_start_time: two tasks at the same fixed time are flagged
# - test_detect_conflict_partial_overlap: partial overlap between fixed tasks is flagged
# - test_detect_no_conflict_adjacent_tasks: adjacent tasks (end == start) are not flagged
# - test_conflict_warnings_includes_fixed_overlap_message: warning string mentions the conflicting task names
# - test_conflict_warnings_overbooked: warning appears when total task minutes exceed availability
# - test_conflict_warnings_empty_when_clean: no warnings for a schedule that fits cleanly
#
# Scheduler — validation
# - test_validate_no_overlap_clean: adjacent plan items pass the no-overlap check
# - test_validate_no_overlap_conflict: overlapping plan items fail the no-overlap check
# - test_validate_fits_availability: items inside the window pass; items ending late fail
# - test_validate_fits_availability_start_too_early: item starting before availability opens fails
# - test_validate_all_required_scheduled_all_present: returns True when every active task is in the plan
# - test_validate_all_required_scheduled_missing_task: returns False when an active task is absent from the plan
#
# Scheduler — filter & explain
# - test_filter_by_pet_name_case_insensitive: matches pet name regardless of case
# - test_filter_by_pet_name_no_match_returns_empty: returns empty list when no pet matches the name
# - test_filter_by_pet_name_multiple_pets_same_name: returns tasks for all pets sharing the same name
# - test_explain_plan_empty: returns "No tasks were scheduled." for an empty plan
# - test_explain_plan_fixed_time_label: fixed-time tasks get a "fixed time" annotation
# - test_explain_plan_high_priority_label: floating tasks with priority >= 4 get a "high priority" annotation
# - test_explain_plan_time_window_label: tasks with earliest_start or latest_end get a "time window" annotation
# - test_explain_plan_no_label_for_low_priority_floating: low-priority floating tasks get no annotation


# Run with coverage:
# pytest --cov
python -m pytest --cov=pawpal_system --cov-report=term-missing tests/test_pawpal.py
```

Sample test output:

```
collected 73 items                                                                                                                      

tests/test_pawpal.py::test_user_available_minutes PASSED                                                                          [  1%]
tests/test_pawpal.py::test_user_update_availability PASSED                                                                        [  2%]
tests/test_pawpal.py::test_user_bad_time_format_raises PASSED                                                                     [  4%]
tests/test_pawpal.py::test_user_add_and_remove_preference PASSED                                                                  [  5%]
tests/test_pawpal.py::test_user_remove_missing_preference_does_not_raise PASSED                                                   [  6%]
tests/test_pawpal.py::test_pet_summary_full PASSED                                                                                [  8%]
tests/test_pawpal.py::test_pet_summary_minimal PASSED                                                                             [  9%]
tests/test_pawpal.py::test_pet_add_constraint PASSED                                                                              [ 10%]
tests/test_pawpal.py::test_pet_update_profile PASSED                                                                              [ 12%]
tests/test_pawpal.py::test_pet_update_profile_unknown_key_raises PASSED                                                           [ 13%]
tests/test_pawpal.py::test_task_mark_complete PASSED                                                                              [ 15%]
tests/test_pawpal.py::test_task_is_fixed_time PASSED                                                                              [ 16%]
tests/test_pawpal.py::test_task_requires_time_window PASSED                                                                       [ 17%]
tests/test_pawpal.py::test_task_fits_in_window PASSED                                                                             [ 19%]
tests/test_pawpal.py::test_task_fits_in_window_respects_constraints PASSED                                                        [ 20%]
tests/test_pawpal.py::test_task_bad_time_raises PASSED                                                                            [ 21%]
tests/test_pawpal.py::test_task_update_valid PASSED                                                                               [ 23%]
tests/test_pawpal.py::test_task_update_unknown_key_raises PASSED                                                                  [ 24%]
tests/test_pawpal.py::test_task_to_dict_and_from_dict PASSED                                                                      [ 26%]
tests/test_pawpal.py::test_scheduled_item_duration PASSED                                                                         [ 27%]
tests/test_pawpal.py::test_scheduled_item_overlaps_true PASSED                                                                    [ 28%]
tests/test_pawpal.py::test_scheduled_item_overlaps_false_adjacent PASSED                                                          [ 30%]
tests/test_pawpal.py::test_scheduled_item_overlaps_false_separate PASSED                                                          [ 31%]
tests/test_pawpal.py::test_adding_task_increases_count PASSED                                                                     [ 32%]
tests/test_pawpal.py::test_remove_task_sets_inactive PASSED                                                                       [ 34%]
tests/test_pawpal.py::test_remove_task_unknown_id_raises PASSED                                                                   [ 35%]
tests/test_pawpal.py::test_edit_task_updates_field PASSED                                                                         [ 36%]
tests/test_pawpal.py::test_edit_task_unknown_id_raises PASSED                                                                     [ 38%]
tests/test_pawpal.py::test_sort_tasks_fixed_first_then_priority PASSED                                                            [ 39%]
tests/test_pawpal.py::test_reject_if_impossible_raises PASSED                                                                     [ 41%]
tests/test_pawpal.py::test_reject_if_impossible_fixed_outside_window_raises PASSED                                                [ 42%]
tests/test_pawpal.py::test_validate_no_overlap_clean PASSED                                                                       [ 43%]
tests/test_pawpal.py::test_validate_no_overlap_conflict PASSED                                                                    [ 45%]
tests/test_pawpal.py::test_validate_fits_availability PASSED                                                                      [ 46%]
tests/test_pawpal.py::test_generate_daily_plan_order_and_count PASSED                                                             [ 47%]
tests/test_pawpal.py::test_add_pet_increases_count PASSED                                                                         [ 49%]
tests/test_pawpal.py::test_sort_by_time_chronological_order PASSED                                                                [ 50%]
tests/test_pawpal.py::test_sort_by_time_falls_back_to_earliest_start PASSED                                                       [ 52%]
tests/test_pawpal.py::test_sort_by_time_no_anchor_sorts_last PASSED                                                               [ 53%]
tests/test_pawpal.py::test_mark_complete_sets_completed_flag PASSED                                                               [ 54%]
tests/test_pawpal.py::test_mark_complete_daily_creates_tomorrow PASSED                                                            [ 56%]
tests/test_pawpal.py::test_mark_complete_weekly_creates_seven_days_later PASSED                                                   [ 57%]
tests/test_pawpal.py::test_mark_complete_one_off_returns_none PASSED                                                              [ 58%]
tests/test_pawpal.py::test_mark_complete_unknown_id_raises PASSED                                                                 [ 60%]
tests/test_pawpal.py::test_detect_no_conflict_when_tasks_are_separate PASSED                                                      [ 61%]
tests/test_pawpal.py::test_detect_conflict_same_start_time PASSED                                                                 [ 63%]
tests/test_pawpal.py::test_detect_conflict_partial_overlap PASSED                                                                 [ 64%]
tests/test_pawpal.py::test_detect_no_conflict_adjacent_tasks PASSED                                                               [ 65%]
tests/test_pawpal.py::test_conflict_warnings_includes_fixed_overlap_message PASSED                                                [ 67%]
tests/test_pawpal.py::test_conflict_warnings_overbooked PASSED                                                                    [ 68%]
tests/test_pawpal.py::test_conflict_warnings_empty_when_clean PASSED                                                              [ 69%]
tests/test_pawpal.py::test_task_update_time_field_valid PASSED                                                                    [ 71%]
tests/test_pawpal.py::test_task_update_time_field_invalid_raises PASSED                                                           [ 72%]
tests/test_pawpal.py::test_tasks_for_pet_returns_matching PASSED                                                                  [ 73%]
tests/test_pawpal.py::test_tasks_for_pet_empty_when_none_match PASSED                                                             [ 75%]
tests/test_pawpal.py::test_tasks_by_status_incomplete PASSED                                                                      [ 76%]
tests/test_pawpal.py::test_expand_recurring_2x_day_produces_two_entries PASSED                                                    [ 78%]
tests/test_pawpal.py::test_expand_recurring_2x_day_copy_has_no_time_constraints PASSED                                            [ 79%]
tests/test_pawpal.py::test_expand_recurring_non_2x_day_unchanged PASSED                                                           [ 80%]
tests/test_pawpal.py::test_generate_plan_respects_earliest_start PASSED                                                           [ 82%]
tests/test_pawpal.py::test_generate_plan_skips_task_exceeding_latest_end PASSED                                                   [ 83%]
tests/test_pawpal.py::test_generate_plan_skips_task_exceeding_avail_end PASSED                                                    [ 84%]
tests/test_pawpal.py::test_filter_by_pet_name_case_insensitive PASSED                                                             [ 86%]
tests/test_pawpal.py::test_filter_by_pet_name_no_match_returns_empty PASSED                                                       [ 87%]
tests/test_pawpal.py::test_filter_by_pet_name_multiple_pets_same_name PASSED                                                      [ 89%]
tests/test_pawpal.py::test_validate_fits_availability_start_too_early PASSED                                                      [ 90%]
tests/test_pawpal.py::test_validate_all_required_scheduled_all_present PASSED                                                     [ 91%]
tests/test_pawpal.py::test_validate_all_required_scheduled_missing_task PASSED                                                    [ 93%]
tests/test_pawpal.py::test_explain_plan_empty PASSED                                                                              [ 94%]
tests/test_pawpal.py::test_explain_plan_fixed_time_label PASSED                                                                   [ 95%]
tests/test_pawpal.py::test_explain_plan_high_priority_label PASSED                                                                [ 97%]
tests/test_pawpal.py::test_explain_plan_time_window_label PASSED                                                                  [ 98%]
tests/test_pawpal.py::test_explain_plan_no_label_for_low_priority_floating PASSED                                                 [100%]

========================================================== 73 passed in 0.05s ===========================================================
============================================================ tests coverage =============================================================
___________________________________________ coverage: platform darwin, python 3.11.4-final-0 ____________________________________________

Name               Stmts   Miss  Cover   Missing
------------------------------------------------
pawpal_system.py     280      1    99%   441
------------------------------------------------
TOTAL                280      1    99%
========================================================== 73 passed in 0.12s ===========================================================

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

### UI features
The Streamlit app has four sections:

- **Owner Setup** — enter name and availability window (`08:00`–`18:00`). Initializes the scheduler.
- **Add a Pet** — add pets with name, species, optional breed. Each gets a `pet_id` used to link tasks.
- **Add a Task** — set name, category, duration, priority (1–5), optional fixed start time, and pet. Task table updates immediately sorted by scheduling priority; conflict warnings appear live below.
- **Generate Schedule** — disabled when conflicts exist. Produces a conflict-free plan with priority badges (🔴 high / 🟡 medium / 🔵 low), ✓ Done buttons, and a collapsible explanation panel.

### Example flow

1. Save owner **Jordan**, available `08:00`–`18:00`
2. Add pet **Buddy** (dog)
3. Add task: *Morning Walk*, 30 min, priority 5, fixed at `08:00`
4. Add task: *Feeding*, 10 min, priority 4, assigned to Buddy
5. Add task: *Grooming*, 20 min, priority 2
6. Click **Generate Schedule** → plan appears in chronological order
7. Click **✓ Done** on Morning Walk → it grays out; next daily occurrence is queued

### Key scheduler behaviors shown

- **Conflict warnings** appear the moment two fixed-time tasks overlap and block the Generate button until resolved
- **Priority sorting** ensures high-priority tasks claim slots before low-priority ones
- **Skipped-task notice** reports how many tasks couldn't fit their time window constraints
- **explain_plan** annotates each slot with the reason it was placed there (fixed time / high priority / time window)

### Sample CLI output (`python main.py`)

```
====================================================
  Conflict Warnings
====================================================
  ⚠ Time conflict: 'Morning Walk' (08:00, 30 min) overlaps 'Buddy Medication' (08:00, 5 min)
  ⚠ Time conflict: 'Morning Walk' (08:00, 30 min) overlaps 'Grooming' (08:10, 20 min)

====================================================
  Removing conflicting tasks and rescheduling
====================================================
  Warnings after fix: 0 (cleared)

====================================================
  PawPal+  —  Today's Schedule (conflict-free)
====================================================
  08:00 – 08:30  [buddy] Morning Walk
  08:30 – 08:40  [mochi] Mochi Feeding
  09:00 – 09:05  [buddy] Buddy Medication
  3 tasks scheduled
====================================================
```
