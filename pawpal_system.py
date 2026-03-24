from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple


@dataclass
class Task:
    """Represents a single care activity scheduled for a pet."""

    description: str
    pet_name: str
    time: datetime
    duration_minutes: int
    priority: str
    frequency: str = "once"
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_complete(self) -> None:
        """Set this task's completed status to True."""
        self.completed = True


@dataclass
class Pet:
    """Represents a pet profile containing basic info and a task list."""

    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a new Task to this pet's internal task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return a shallow copy of this pet's task list to prevent mutation."""
        return list(self.tasks)


class Owner:
    """Represents the app user who owns and manages one or more pets."""

    def __init__(self, name: str) -> None:
        """Initialize the owner with a display name and an empty pet registry."""
        self.name = name
        self.pets: Dict[str, Pet] = {}

    def add_pet(self, pet: Pet) -> None:
        """Register a Pet under this owner, keyed by the pet's name."""
        self.pets[pet.name] = pet

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the Pet matching the given name, or None if not found."""
        return self.pets.get(name)

    def get_all_tasks(self) -> List[Task]:
        """Collect and return a flat list of all tasks across every pet."""
        all_tasks: List[Task] = []
        for pet in self.pets.values():
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """Algorithmic engine that retrieves, organizes, and manages pet tasks."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with a reference to the Owner instance."""
        self.owner = owner

    def get_todays_tasks(self, target_date: date) -> List[Task]:
        """Return all tasks whose scheduled date matches the given target date."""
        return [
            task for task in self.owner.get_all_tasks()
            if task.time.date() == target_date
        ]

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return a new list of tasks sorted in ascending chronological order."""
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(
        self,
        tasks: List[Task],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks filtered by any combination of pet name, completion status, or priority."""
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if priority is not None:
            result = [t for t in result if t.priority == priority]
        return result

    def mark_task_complete(self, task_id: str) -> None:
        """Mark the task matching the given ID as complete and schedule its next recurrence if needed."""
        for pet in self.owner.pets.values():
            for task in list(pet.tasks):
                if task.id == task_id:
                    task.mark_complete()
                    if task.frequency == "daily":
                        delta = timedelta(days=1)
                    elif task.frequency == "weekly":
                        delta = timedelta(weeks=1)
                    else:
                        return
                    new_task = Task(
                        description=task.description,
                        pet_name=task.pet_name,
                        time=task.time + delta,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                        frequency=task.frequency,
                    )
                    pet.add_task(new_task)
                    return

    def detect_conflicts(self, tasks: List[Task]) -> List[Tuple[Task, Task]]:
        """Return all pairs of tasks that share the same scheduled time."""
        conflicts: List[Tuple[Task, Task]] = []
        sorted_tasks = self.sort_by_time(tasks)
        n = len(sorted_tasks)
        for i in range(n):
            for j in range(i + 1, n):
                if sorted_tasks[i].time == sorted_tasks[j].time:
                    conflicts.append((sorted_tasks[i], sorted_tasks[j]))
                else:
                    break
        return conflicts