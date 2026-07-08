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

Output from `python main.py`:

```
Adding tasks (note: intentionally out of order)...
  Task #1 added: bath at 11:00 AM
  Task #2 added: grooming at 02:00 PM
  Task #3 added: walk at 08:00 AM

================================================
  SORTED BY TIME
================================================
  08:00 AM  walk
  11:00 AM  bath
  02:00 PM  grooming

================================================
  RECURRING: Mark Buddy's walk complete (DAILY)
================================================
  Before: status=pending, scheduled=2026-07-08 08:00 AM
  After : status=done
  Next occurrence auto-created -> Task #4 on 2026-07-09 08:00 AM

================================================
  CONFLICT: Add overlapping task for Buddy at 11:20 AM (during bath)
================================================
  Warning  Conflict: 'vet_visit' at 11:20 AM overlaps with 'bath' at 11:00 AM for the same pet.

================================================
  TODAY'S SCHEDULE (sorted by time)
================================================
  [x] 08:00 AM  Buddy -- WALK
       Morning walk around the park  [high priority]
  [ ] 11:00 AM  Buddy -- BATH
       Weekly bath  [medium priority]
  [ ] 11:20 AM  Buddy -- VET_VISIT
       Vet check (overlaps bath)  [high priority]
  [ ] 02:00 PM  Luna -- GROOMING
       Shared grooming appointment  [low priority]
================================================
```

## 🧪 Testing PawPal+

```bash
python -m pytest tests/
```

The test suite covers 17 behaviors across 5 categories:

| Category | What is tested |
|---|---|
| Task status | `mark_complete()` changes status from PENDING to DONE |
| Task count | Adding a task via `Scheduler` updates the pet's task list |
| Sorting | `sort_by_time()` returns tasks in chronological order; single-task edge case |
| Recurring tasks | DAILY → next day; WEEKLY → next week; ONCE → no new task; attributes preserved |
| Conflict detection | Overlapping windows flagged; exact same time flagged; non-overlapping allowed; different pets not flagged |
| Filtering | Filter by status returns only matching tasks; filter by pet_id returns only that pet |
| Edge cases | Pet with no tasks returns empty list; past-day tasks excluded from today's schedule; unknown task ID returns None |

**Sample test output:**

```
============================= test session starts ==============================
platform linux -- Python 3.13.3, pytest-9.1.1, pluggy-1.6.0
collected 17 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  5%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 11%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 17%]
tests/test_pawpal.py::test_sort_by_time_single_task_unchanged PASSED     [ 23%]
tests/test_pawpal.py::test_recurring_daily_schedules_next_day PASSED     [ 29%]
tests/test_pawpal.py::test_recurring_weekly_schedules_next_week PASSED   [ 35%]
tests/test_pawpal.py::test_recurring_once_does_not_create_new_task PASSED [ 41%]
tests/test_pawpal.py::test_recurring_task_preserves_original_attributes PASSED [ 47%]
tests/test_pawpal.py::test_conflict_detected_for_overlapping_tasks PASSED [ 52%]
tests/test_pawpal.py::test_conflict_detected_for_exact_same_start_time PASSED [ 58%]
tests/test_pawpal.py::test_no_conflict_for_non_overlapping_tasks PASSED  [ 64%]
tests/test_pawpal.py::test_no_conflict_for_different_pets PASSED         [ 70%]
tests/test_pawpal.py::test_filter_by_status_returns_only_matching PASSED [ 76%]
tests/test_pawpal.py::test_filter_by_pet_id_returns_only_that_pet PASSED [ 82%]
tests/test_pawpal.py::test_get_tasks_for_pet_with_no_tasks_returns_empty PASSED [ 88%]
tests/test_pawpal.py::test_get_todays_schedule_excludes_other_days PASSED [ 94%]
tests/test_pawpal.py::test_mark_task_complete_unknown_id_returns_none PASSED [100%]

============================== 17 passed in 0.09s ==============================
```

**Confidence level: ★★★★☆** — Core behaviors are well covered. Missing: integration tests that run the full owner → pet → task → schedule flow end-to-end, and tests for the Streamlit layer.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time(tasks)` | Sorts by `scheduled_at` ascending; used inside `get_todays_schedule` |
| Filtering | `Scheduler.filter_tasks(tasks, pet_id, status)` | Filter by pet ID, completion status, or both |
| Conflict handling | `Scheduler.get_conflicts(tasks)` | Detects overlapping time windows for same-pet tasks; `add_task` returns a warning string on conflict |
| Recurring tasks | `Scheduler.mark_task_complete(task_id)` | On completion, auto-schedules next occurrence using `timedelta` (daily +1d, weekly +7d) |

## Features

Tasks sorted chronologically using `Scheduler.sort_by_time()`. The daily schedule always shows tasks in the order they happen, regardless of when they were added.

Conflict warnings via `Scheduler.get_conflicts()`. When a task is added that overlaps an existing task for the same pet (based on start time plus duration), a warning is returned and displayed in the UI. The task is still saved so the owner can decide what to do.

Recurring task automation via `Scheduler.mark_task_complete()`. Marking a DAILY or WEEKLY task done automatically creates the next occurrence using Python's `timedelta`. ONCE tasks are simply closed out.

Filtering via `Scheduler.filter_tasks()`. Tasks can be narrowed by pet ID, completion status, or both. Used in the UI to let owners focus on a single pet's schedule.

Multi-owner support. A pet can have multiple owners. Tasks carry an optional `owner_id`, and tasks with no owner are treated as shared events visible to everyone.

## 📸 Demo Walkthrough

1. Open the app with `streamlit run app.py` and enter your name, then click Set Owner.
2. Add one or more pets using the Add Pet form (name, breed, species, age).
3. Use the Schedule a Task form to add care activities. Pick a pet, activity type, time, duration, priority, and frequency. If you schedule two tasks for the same pet that overlap in time, a conflict warning appears immediately below the form.
4. Click Generate Schedule to see today's tasks sorted chronologically. Each card shows the time, pet, activity, description, priority, duration, and whether it is a personal or shared task.
5. Click Mark done on any task. If the task is DAILY or WEEKLY, a toast notification confirms that the next occurrence has been scheduled automatically.

For a terminal-only demo, run `python main.py`. It demonstrates adding tasks out of order, sorting, filtering, recurring task creation, and conflict detection with printed output.
