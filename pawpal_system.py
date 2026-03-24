from __future__ import annotations
import uuid
import json
import os
from dataclasses import dataclass, field, replace
from datetime import datetime, date, timedelta, time
from itertools import combinations
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────
# Task
# ─────────────────────────────────────────────

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

    def to_dict(self) -> dict:
        """Serialize this Task to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "pet_name": self.pet_name,
            "time": self.time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Deserialize a Task from a dictionary loaded from JSON."""
        task = cls(
            description=data["description"],
            pet_name=data["pet_name"],
            time=datetime.fromisoformat(data["time"]),
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            frequency=data["frequency"],
            completed=data["completed"],
        )
        task.id = data["id"]
        return task


# ─────────────────────────────────────────────
# Pet
# ─────────────────────────────────────────────

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

    def to_dict(self) -> dict:
        """Serialize this Pet (and all its tasks) to a JSON-compatible dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Deserialize a Pet and its tasks from a dictionary loaded from JSON."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            breed=data.get("breed"),
            age=data.get("age"),
        )
        for t in data.get("tasks", []):
            pet.add_task(Task.from_dict(t))
        return pet


# ─────────────────────────────────────────────
# Owner
# ─────────────────────────────────────────────

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

    # ── Challenge 2: JSON Persistence ──────────────────────────────────

    def save_to_json(self, filepath: str = "data.json") -> None:
        """
        Serialize the entire Owner (all pets and tasks) to a JSON file.
        Creates or overwrites the file at the given filepath.
        Agent Mode implementation: Owner.save_to_json() → data.json
        """
        data = {
            "owner_name": self.name,
            "pets": [pet.to_dict() for pet in self.pets.values()],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> Owner:
        """
        Deserialize an Owner with all pets and tasks from a JSON file.
        Returns a fresh Owner named 'My Household' if no file is found.
        Agent Mode implementation: Owner.load_from_json() ← data.json
        """
        if not os.path.exists(filepath):
            return cls(name="My Household")
        with open(filepath, "r") as f:
            data = json.load(f)
        owner = cls(name=data["owner_name"])
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner


# ─────────────────────────────────────────────
# Scheduler
# ─────────────────────────────────────────────

class Scheduler:
    """Algorithmic engine that retrieves, organizes, and manages pet tasks."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with a reference to the Owner instance."""
        self.owner = owner

    def get_todays_tasks(self, target_date: date = None) -> List[Task]:
        """Return all tasks whose scheduled date matches the given target date (defaults to today)."""
        target = target_date or date.today()
        return [
            task for task in self.owner.get_all_tasks()
            if task.time.date() == target
        ]

    def sort_by_time(self, tasks: List[Task], priority_first: bool = False) -> List[Task]:
        """Return tasks sorted by time, or by priority then time if priority_first is True."""
        priority_weights = {"High": 1, "Medium": 2, "Low": 3}
        if priority_first:
            return sorted(
                tasks,
                key=lambda t: (priority_weights.get(t.priority, 4), t.time)
            )
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
        """
        Mark the task matching the given ID as complete.
        Uses dataclasses.replace() to clone recurring tasks — more Pythonic
        than deepcopy for flat dataclasses (Claude 3.5 Sonnet recommendation,
        Challenge 5 model comparison winner).
        """
        for pet in self.owner.pets.values():
            for task in list(pet.tasks):
                if task.id == task_id:
                    if task.completed:
                        return                          # guard: no double-recurrence
                    task.mark_complete()
                    if task.frequency == "daily":
                        delta = timedelta(days=1)
                    elif task.frequency == "weekly":
                        delta = timedelta(weeks=1)
                    else:
                        return                          # "once" — no recurrence
                    # dataclasses.replace() produces an immutable clone;
                    # the original completed task is preserved in history
                    new_task = replace(
                        task,
                        time=task.time + delta,
                        completed=False,
                        id=str(uuid.uuid4()),
                    )
                    pet.add_task(new_task)
                    return

    def detect_conflicts(self, tasks: List[Task]) -> List[Tuple[Task, Task]]:
        """Return pairs of tasks that overlap based on start time and duration."""
        conflicts: List[Tuple[Task, Task]] = []
        sorted_tasks = self.sort_by_time(tasks)
        for a, b in combinations(sorted_tasks, 2):
            a_end = a.time + timedelta(minutes=a.duration_minutes)
            b_end = b.time + timedelta(minutes=b.duration_minutes)
            if a.time < b_end and b.time < a_end:
                conflicts.append((a, b))
        return conflicts

    def get_recurring_tasks(self) -> List[Task]:
        """Return all incomplete tasks with a daily or weekly frequency."""
        return [
            task for task in self.owner.get_all_tasks()
            if not task.completed and task.frequency in {"daily", "weekly"}
        ]

    # ── Challenge 1: Next Available Slot Algorithm ─────────────────────

    def find_next_available_slot(
        self,
        duration_minutes: int,
        preferred_date: date = None,
        start_hour: int = 8,
        end_hour: int = 20,
    ) -> Optional[datetime]:
        """
        Find the earliest open time slot of a given duration with no conflicts.

        Algorithm:
        - Scans from start_hour to end_hour in 30-minute increments
        - For each candidate window, checks interval overlap against all
          existing tasks scheduled that day
        - Returns the first conflict-free window, or None if none found

        Time complexity: O(n * k) where n = existing tasks, k = scan slots
        Typical daily schedule: n < 20, k < 24 — effectively O(1)
        """
        target    = preferred_date or date.today()
        tasks     = self.get_todays_tasks(target)
        candidate = datetime.combine(target, time(start_hour, 0))
        window_end = datetime.combine(target, time(end_hour, 0))

        while candidate + timedelta(minutes=duration_minutes) <= window_end:
            candidate_end = candidate + timedelta(minutes=duration_minutes)
            conflict = any(
                task.time < candidate_end and
                (task.time + timedelta(minutes=task.duration_minutes)) > candidate
                for task in tasks
            )
            if not conflict:
                return candidate
            candidate += timedelta(minutes=30)

        return None  # no open slot found in the scanning window