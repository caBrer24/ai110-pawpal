from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Owner:
    id: int
    name: str
    pets: list["Pet"] = field(default_factory=list)

    def add_pet(self, pet: "Pet") -> None:
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

    def get_tasks(self) -> list["Task"]:
        pass

    def get_owners(self) -> list["Owner"]:
        pass


@dataclass
class Task:
    id: int
    pet_id: int
    task_kind: str  # "personal" or "event"
    type: str
    priority: str
    duration: int
    status: str
    scheduled_at: datetime
    owner_id: Optional[int] = None  # null when task_kind is "event"

    def mark_done(self) -> None:
        pass

    def is_pending(self) -> bool:
        pass

    def is_shared(self) -> bool:
        pass
