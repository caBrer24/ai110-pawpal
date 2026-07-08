from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class TaskKind(Enum):
    PERSONAL = "personal"
    EVENT = "event"


class ActivityType(Enum):
    WALK = "walk"
    BATH = "bath"
    GROOMING = "grooming"
    VET_VISIT = "vet_visit"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(Enum):
    PENDING = "pending"
    DONE = "done"


class TaskFrequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Owner:
    id: int
    name: str
    pet_ids: list[int] = field(default_factory=list)
    task_ids: list[int] = field(default_factory=list)

    def add_pet(self, pet_id: int) -> None:
        """Associate a pet with this owner by ID."""
        if pet_id not in self.pet_ids:
            self.pet_ids.append(pet_id)

    def create_task(self, task: "Task") -> "Task":
        """Register a task under this owner and return it."""
        if task.id not in self.task_ids:
            self.task_ids.append(task.id)
        return task


@dataclass
class Pet:
    id: int
    name: str
    breed: str
    age: int
    species: str
    owner_ids: list[int] = field(default_factory=list)
    task_ids: list[int] = field(default_factory=list)

    def get_tasks(self) -> list[int]:
        """Return the IDs of all tasks assigned to this pet."""
        return self.task_ids

    def get_owners(self) -> list[int]:
        """Return the IDs of all owners associated with this pet."""
        return self.owner_ids


@dataclass
class Task:
    id: int
    pet_id: int
    task_kind: TaskKind
    activity: ActivityType
    priority: TaskPriority
    duration_minutes: int
    status: TaskStatus
    scheduled_at: datetime
    description: str
    frequency: TaskFrequency
    owner_id: Optional[int] = None  # null when task_kind is EVENT

    def mark_complete(self) -> None:
        """Set the task status to DONE."""
        self.status = TaskStatus.DONE

    def is_pending(self) -> bool:
        """Return True if the task has not been completed."""
        return self.status == TaskStatus.PENDING

    def is_shared(self) -> bool:
        """Return True if the task is a shared event with no assigned owner."""
        return self.owner_id is None


@dataclass
class Scheduler:
    owners: dict = field(default_factory=dict)
    pets: dict = field(default_factory=dict)
    tasks: dict = field(default_factory=dict)

    def add_owner(self, owner: Owner) -> None:
        """Register an owner in the data store."""
        self.owners[owner.id] = owner

    def add_pet(self, pet: Pet, owner_id: int) -> None:
        """Register a pet and link it bidirectionally to an owner."""
        self.pets[pet.id] = pet
        if owner_id in self.owners:
            self.owners[owner_id].add_pet(pet.id)
            if owner_id not in pet.owner_ids:
                pet.owner_ids.append(owner_id)

    def add_task(self, task: Task) -> str | None:
        """Register a task; returns a conflict warning string if an overlap is detected."""
        self.tasks[task.id] = task
        if task.pet_id in self.pets:
            pet = self.pets[task.pet_id]
            if task.id not in pet.task_ids:
                pet.task_ids.append(task.id)
        if task.owner_id and task.owner_id in self.owners:
            self.owners[task.owner_id].create_task(task)

        pet_tasks = self.get_tasks_for_pet(task.pet_id)
        for t1, t2 in self.get_conflicts(pet_tasks):
            if task.id in (t1.id, t2.id):
                other = t2 if t1.id == task.id else t1
                return (
                    f"⚠️  Conflict: '{task.activity.value}' at "
                    f"{task.scheduled_at.strftime('%I:%M %p')} overlaps with "
                    f"'{other.activity.value}' at "
                    f"{other.scheduled_at.strftime('%I:%M %p')} for the same pet."
                )
        return None

    def get_tasks_for_pet(self, pet_id: int) -> list[Task]:
        """Return all Task objects assigned to a specific pet."""
        pet = self.pets.get(pet_id)
        if not pet:
            return []
        return [self.tasks[tid] for tid in pet.task_ids if tid in self.tasks]

    def get_todays_schedule(self, owner_id: int) -> list[Task]:
        """Return today's tasks for an owner's pets, sorted by scheduled time."""
        owner = self.owners.get(owner_id)
        if not owner:
            return []
        today = datetime.now().date()
        tasks = []
        for pet_id in owner.pet_ids:
            pet_tasks = self.get_tasks_for_pet(pet_id)
            tasks.extend([t for t in pet_tasks if t.scheduled_at.date() == today])
        return self.sort_by_time(tasks)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by scheduled_at in ascending chronological order."""
        return sorted(tasks, key=lambda t: t.scheduled_at)

    def filter_tasks(
        self,
        tasks: list[Task],
        pet_id: int | None = None,
        status: TaskStatus | None = None,
    ) -> list[Task]:
        """Filter a task list by pet ID, completion status, or both."""
        result = tasks
        if pet_id is not None:
            result = [t for t in result if t.pet_id == pet_id]
        if status is not None:
            result = [t for t in result if t.status == status]
        return result

    def get_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Return pairs of same-pet tasks whose time windows overlap."""
        conflicts = []
        for i, t1 in enumerate(tasks):
            for t2 in tasks[i + 1:]:
                if t1.pet_id != t2.pet_id:
                    continue
                t1_end = t1.scheduled_at + timedelta(minutes=t1.duration_minutes)
                t2_end = t2.scheduled_at + timedelta(minutes=t2.duration_minutes)
                if t1.scheduled_at < t2_end and t2.scheduled_at < t1_end:
                    conflicts.append((t1, t2))
        return conflicts

    def mark_task_complete(self, task_id: int) -> Task | None:
        """Mark a task done and auto-schedule the next occurrence if it recurs."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        task.mark_complete()
        if task.frequency == TaskFrequency.ONCE:
            return None
        delta = (
            timedelta(days=1) if task.frequency == TaskFrequency.DAILY
            else timedelta(weeks=1)
        )
        new_id = max(self.tasks.keys(), default=0) + 1
        next_task = Task(
            id=new_id,
            pet_id=task.pet_id,
            task_kind=task.task_kind,
            activity=task.activity,
            priority=task.priority,
            duration_minutes=task.duration_minutes,
            status=TaskStatus.PENDING,
            scheduled_at=task.scheduled_at + delta,
            description=task.description,
            frequency=task.frequency,
            owner_id=task.owner_id,
        )
        self.add_task(next_task)
        return next_task
