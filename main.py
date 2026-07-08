from datetime import datetime
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    ActivityType, TaskKind, TaskPriority, TaskStatus, TaskFrequency,
)

scheduler = Scheduler()

# Owner and pets
carlos = Owner(id=1, name="Carlos")
scheduler.add_owner(carlos)

buddy = Pet(id=1, name="Buddy", breed="Golden Retriever", age=3, species="dog")
luna  = Pet(id=2, name="Luna",  breed="Siamese",          age=5, species="cat")
scheduler.add_pet(buddy, owner_id=1)
scheduler.add_pet(luna,  owner_id=1)

today = datetime.now()

def t(hour, minute=0):
    return today.replace(hour=hour, minute=minute, second=0, microsecond=0)


# ── Add tasks intentionally OUT OF ORDER to demo sorting ──────────────────────
tasks = [
    Task(id=1, pet_id=1, owner_id=1,
         task_kind=TaskKind.PERSONAL, activity=ActivityType.BATH,
         priority=TaskPriority.MEDIUM, duration_minutes=45,
         status=TaskStatus.PENDING, scheduled_at=t(11),
         description="Weekly bath", frequency=TaskFrequency.WEEKLY),

    Task(id=2, pet_id=2, owner_id=None,
         task_kind=TaskKind.EVENT, activity=ActivityType.GROOMING,
         priority=TaskPriority.LOW, duration_minutes=60,
         status=TaskStatus.PENDING, scheduled_at=t(14),
         description="Shared grooming appointment", frequency=TaskFrequency.WEEKLY),

    Task(id=3, pet_id=1, owner_id=1,
         task_kind=TaskKind.PERSONAL, activity=ActivityType.WALK,
         priority=TaskPriority.HIGH, duration_minutes=30,
         status=TaskStatus.PENDING, scheduled_at=t(8),
         description="Morning walk around the park", frequency=TaskFrequency.DAILY),
]

print("Adding tasks (note: intentionally out of order)...")
for task in tasks:
    warning = scheduler.add_task(task)
    if warning:
        print(f"  {warning}")
    else:
        print(f"  Task #{task.id} added: {task.activity.value} at {task.scheduled_at.strftime('%I:%M %p')}")


# ── Sorting ────────────────────────────────────────────────────────────────────
def separator(title):
    print(f"\n{'=' * 48}\n  {title}\n{'=' * 48}")

all_tasks = list(scheduler.tasks.values())

separator("UNSORTED (insertion order)")
for t_ in all_tasks:
    print(f"  {t_.scheduled_at.strftime('%I:%M %p')}  {t_.activity.value}")

separator("SORTED BY TIME")
for t_ in scheduler.sort_by_time(all_tasks):
    print(f"  {t_.scheduled_at.strftime('%I:%M %p')}  {t_.activity.value}")


# ── Filtering ─────────────────────────────────────────────────────────────────
separator("FILTER: Buddy's tasks only (pet_id=1)")
for t_ in scheduler.filter_tasks(all_tasks, pet_id=1):
    print(f"  [{t_.status.value}] {t_.activity.value}")

separator("FILTER: Pending tasks only")
for t_ in scheduler.filter_tasks(all_tasks, status=TaskStatus.PENDING):
    print(f"  {t_.activity.value} — {t_.status.value}")


# ── Recurring tasks ────────────────────────────────────────────────────────────
separator("RECURRING: Mark Buddy's walk complete (DAILY)")
walk = scheduler.tasks[3]
print(f"  Before: status={walk.status.value}, scheduled={walk.scheduled_at.strftime('%Y-%m-%d %I:%M %p')}")
next_task = scheduler.mark_task_complete(walk.id)
print(f"  After : status={walk.status.value}")
if next_task:
    print(f"  Next occurrence auto-created → Task #{next_task.id} on {next_task.scheduled_at.strftime('%Y-%m-%d %I:%M %p')}")


# ── Conflict detection ─────────────────────────────────────────────────────────
separator("CONFLICT: Add overlapping task for Buddy at 11:20 AM (during bath)")
conflicting_task = Task(
    id=5, pet_id=1, owner_id=1,
    task_kind=TaskKind.PERSONAL, activity=ActivityType.VET_VISIT,
    priority=TaskPriority.HIGH, duration_minutes=30,
    status=TaskStatus.PENDING, scheduled_at=t(11, 20),
    description="Vet check (overlaps bath)", frequency=TaskFrequency.ONCE,
)
warning = scheduler.add_task(conflicting_task)
if warning:
    print(f"  {warning}")


# ── Today's schedule ───────────────────────────────────────────────────────────
separator("TODAY'S SCHEDULE (sorted by time)")
schedule = scheduler.get_todays_schedule(owner_id=1)
for t_ in schedule:
    pet        = scheduler.pets[t_.pet_id]
    status_icon = "✅" if t_.status == TaskStatus.DONE else "⏳"
    print(f"  {status_icon} {t_.scheduled_at.strftime('%I:%M %p')}  {pet.name} — {t_.activity.value.upper()}")
    print(f"       {t_.description}  [{t_.priority.value} priority]")

print(f"\n{'=' * 48}")
