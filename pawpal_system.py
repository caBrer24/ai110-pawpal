from dataclasses import dataclass, field
from datetime import datetime
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


@dataclass
class Owner:
    id: int
    name: str
    pet_ids: list[int] = field(default_factory=list)
    task_ids: list[int] = field(default_factory=list)

    def add_pet(self, pet_id: int) -> None:
        pass

    def create_task(self, task: "Task") -> "Task":
        pass


@dataclass
class Pet:
    id: int
    name: str
    breed: str
    age: int
    species: str
    owner_ids: list[int] = field(default_factory=list)
    task_ids: list[int] = field(default_factory=list)

    def get_tasks(self) -> list["Task"]:
        pass

    def get_owners(self) -> list["Owner"]:
        pass


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
    owner_id: Optional[int] = None  # null when task_kind is EVENT

    def mark_done(self) -> None:
        pass

    def is_pending(self) -> bool:
        pass

    def is_shared(self) -> bool:
        pass
