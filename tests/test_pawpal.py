from datetime import datetime, timedelta
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    ActivityType, TaskKind, TaskPriority, TaskStatus, TaskFrequency,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(task_id=1, pet_id=1, owner_id=1, hour=9, minute=0,
              duration_minutes=30, frequency=TaskFrequency.DAILY,
              activity=ActivityType.WALK):
    return Task(
        id=task_id,
        pet_id=pet_id,
        owner_id=owner_id,
        task_kind=TaskKind.PERSONAL,
        activity=activity,
        priority=TaskPriority.MEDIUM,
        duration_minutes=duration_minutes,
        status=TaskStatus.PENDING,
        scheduled_at=datetime.now().replace(
            hour=hour, minute=minute, second=0, microsecond=0
        ),
        description="Test task",
        frequency=frequency,
    )


def make_scheduler():
    scheduler = Scheduler()
    owner = Owner(id=1, name="Test Owner")
    pet = Pet(id=1, name="Buddy", breed="Lab", age=2, species="dog")
    scheduler.add_owner(owner)
    scheduler.add_pet(pet, owner_id=1)
    return scheduler, owner, pet


# ---------------------------------------------------------------------------
# Original tests (kept)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()
    assert task.status == TaskStatus.PENDING
    task.mark_complete()
    assert task.status == TaskStatus.DONE


def test_adding_task_increases_pet_task_count():
    scheduler, owner, pet = make_scheduler()
    assert len(pet.task_ids) == 0
    scheduler.add_task(make_task(task_id=1, pet_id=1))
    assert len(pet.task_ids) == 1


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    scheduler = Scheduler()
    tasks = [
        make_task(task_id=1, hour=14),
        make_task(task_id=2, hour=8),
        make_task(task_id=3, hour=11),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    hours = [t.scheduled_at.hour for t in sorted_tasks]
    assert hours == sorted(hours)


def test_sort_by_time_single_task_unchanged():
    scheduler = Scheduler()
    task = make_task(hour=10)
    assert scheduler.sort_by_time([task]) == [task]


# ---------------------------------------------------------------------------
# Recurring tasks
# ---------------------------------------------------------------------------

def test_recurring_daily_schedules_next_day():
    scheduler, owner, pet = make_scheduler()
    task = make_task(task_id=1, frequency=TaskFrequency.DAILY)
    scheduler.add_task(task)
    original_date = task.scheduled_at.date()
    next_task = scheduler.mark_task_complete(task.id)
    assert next_task is not None
    assert next_task.scheduled_at.date() == original_date + timedelta(days=1)
    assert next_task.status == TaskStatus.PENDING


def test_recurring_weekly_schedules_next_week():
    scheduler, owner, pet = make_scheduler()
    task = make_task(task_id=1, frequency=TaskFrequency.WEEKLY)
    scheduler.add_task(task)
    original_date = task.scheduled_at.date()
    next_task = scheduler.mark_task_complete(task.id)
    assert next_task is not None
    assert next_task.scheduled_at.date() == original_date + timedelta(weeks=1)


def test_recurring_once_does_not_create_new_task():
    scheduler, owner, pet = make_scheduler()
    task = make_task(task_id=1, frequency=TaskFrequency.ONCE)
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task.id)
    assert next_task is None


def test_recurring_task_preserves_original_attributes():
    scheduler, owner, pet = make_scheduler()
    task = make_task(task_id=1, frequency=TaskFrequency.DAILY,
                     activity=ActivityType.BATH, duration_minutes=45)
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task.id)
    assert next_task.activity == ActivityType.BATH
    assert next_task.duration_minutes == 45
    assert next_task.frequency == TaskFrequency.DAILY


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_conflict_detected_for_overlapping_tasks():
    scheduler, owner, pet = make_scheduler()
    # Bath: 9:00–9:45 AM (45 min)
    # Walk: 9:20–9:50 AM (30 min) — overlaps
    scheduler.add_task(make_task(task_id=1, hour=9, minute=0,
                                 duration_minutes=45, activity=ActivityType.BATH))
    warning = scheduler.add_task(make_task(task_id=2, hour=9, minute=20,
                                           duration_minutes=30, activity=ActivityType.WALK))
    assert warning is not None
    assert "Conflict" in warning or "⚠️" in warning


def test_conflict_detected_for_exact_same_start_time():
    scheduler, owner, pet = make_scheduler()
    scheduler.add_task(make_task(task_id=1, hour=10, activity=ActivityType.WALK))
    warning = scheduler.add_task(make_task(task_id=2, hour=10, activity=ActivityType.BATH))
    assert warning is not None


def test_no_conflict_for_non_overlapping_tasks():
    scheduler, owner, pet = make_scheduler()
    # Walk: 9:00–9:30 AM — Bath: 10:00–10:45 AM; no overlap
    scheduler.add_task(make_task(task_id=1, hour=9, duration_minutes=30))
    warning = scheduler.add_task(make_task(task_id=2, hour=10, duration_minutes=45))
    assert warning is None


def test_no_conflict_for_different_pets():
    scheduler = Scheduler()
    owner = Owner(id=1, name="Test Owner")
    pet1 = Pet(id=1, name="Buddy", breed="Lab",     age=2, species="dog")
    pet2 = Pet(id=2, name="Luna",  breed="Siamese",  age=3, species="cat")
    scheduler.add_owner(owner)
    scheduler.add_pet(pet1, owner_id=1)
    scheduler.add_pet(pet2, owner_id=1)
    scheduler.add_task(make_task(task_id=1, pet_id=1, hour=10))
    warning = scheduler.add_task(make_task(task_id=2, pet_id=2, hour=10))
    assert warning is None


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def test_filter_by_status_returns_only_matching():
    scheduler, owner, pet = make_scheduler()
    scheduler.add_task(make_task(task_id=1, hour=9,  frequency=TaskFrequency.ONCE))
    scheduler.add_task(make_task(task_id=2, hour=10, frequency=TaskFrequency.ONCE))
    scheduler.mark_task_complete(1)
    all_tasks = list(scheduler.tasks.values())
    pending = scheduler.filter_tasks(all_tasks, status=TaskStatus.PENDING)
    done    = scheduler.filter_tasks(all_tasks, status=TaskStatus.DONE)
    assert all(t.status == TaskStatus.PENDING for t in pending)
    assert all(t.status == TaskStatus.DONE    for t in done)


def test_filter_by_pet_id_returns_only_that_pet():
    scheduler = Scheduler()
    owner = Owner(id=1, name="Test Owner")
    pet1  = Pet(id=1, name="Buddy", breed="Lab",    age=2, species="dog")
    pet2  = Pet(id=2, name="Luna",  breed="Siamese", age=3, species="cat")
    scheduler.add_owner(owner)
    scheduler.add_pet(pet1, owner_id=1)
    scheduler.add_pet(pet2, owner_id=1)
    scheduler.add_task(make_task(task_id=1, pet_id=1))
    scheduler.add_task(make_task(task_id=2, pet_id=2))
    all_tasks    = list(scheduler.tasks.values())
    buddy_tasks  = scheduler.filter_tasks(all_tasks, pet_id=1)
    assert len(buddy_tasks) == 1
    assert buddy_tasks[0].pet_id == 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_get_tasks_for_pet_with_no_tasks_returns_empty():
    scheduler, owner, pet = make_scheduler()
    assert scheduler.get_tasks_for_pet(pet.id) == []


def test_get_todays_schedule_excludes_other_days():
    scheduler, owner, pet = make_scheduler()
    yesterday = datetime.now() - timedelta(days=1)
    old_task = Task(
        id=1, pet_id=1, owner_id=1,
        task_kind=TaskKind.PERSONAL, activity=ActivityType.WALK,
        priority=TaskPriority.LOW, duration_minutes=30,
        status=TaskStatus.PENDING, scheduled_at=yesterday,
        description="Yesterday's walk", frequency=TaskFrequency.ONCE,
    )
    scheduler.add_task(old_task)
    assert scheduler.get_todays_schedule(owner_id=1) == []


def test_mark_task_complete_unknown_id_returns_none():
    scheduler, owner, pet = make_scheduler()
    result = scheduler.mark_task_complete(task_id=999)
    assert result is None
