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
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """Represents a pet profile with its own list of tasks."""
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a new task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return a copy of all tasks assigned to this pet."""
        return list(self.tasks)


class Owner:
    """Represents the app user who manages one or more pets."""

    def __init__(self, name: str) -> None:
        """Initialize the owner with a name and empty pet registry."""
        self.name = name
        self.pets: Dict[str, Pet] = {}

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        self.pets[pet.name] = pet

    def get_pet(self, name: str) -> Optional[Pet]:
        """Retrieve a pet by name, returning None if not found."""
        return self.pets.get(name)

    def get_all_tasks(self) -> List[Task]:
        """Aggregate and return all tasks across every pet."""
        all_tasks: List[Task] = []
        for pet in self.pets.values():
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """The algorithmic brain that retrieves, sorts, and manages tasks."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with a reference to the owner."""
        self.owner = owner

    def get_todays_tasks(self, target_date: date) -> List[Task]:
        """Return all tasks scheduled for the given date."""
        return [
            task for task in self.owner.get_all_tasks()
            if task.time.date() == target_date
        ]

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return a new list of tasks sorted in chronological order."""
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(
        self,
        tasks: List[Task],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by pet name, completion status, and/or priority."""
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if priority is not None:
            result = [t for t in result if t.priority == priority]
        return result

    def mark_task_complete(self, task_id: str) -> None:
        """Mark a task complete by ID and create next recurrence if needed."""
        for pet in self.owner.pets.values():
            for task in list(pet.tasks):
                if task.id == task_id:
                    task.mark_complete()
                    # Handle recurrence
                    if task.frequency == "daily":
                        delta = timedelta(days=1)
                    elif task.frequency == "weekly":
                        delta = timedelta(weeks=1)
                    else:
                        return  # "once" — no recurrence needed
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
        """Return pairs of tasks that are scheduled at the same time."""
        conflicts: List[Tuple[Task, Task]] = []
        sorted_tasks = self.sort_by_time(tasks)
        n = len(sorted_tasks)
        for i in range(n):
            for j in range(i + 1, n):
                if sorted_tasks[i].time == sorted_tasks[j].time:
                    conflicts.append((sorted_tasks[i], sorted_tasks[j]))
                else:
                    break  # sorted, so no more matches possible
        return conflicts