from datetime import datetime, date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ── Helpers ────────────────────────────────────────────────────────────────

def make_task(
    description="Test Task",
    pet_name="Buddy",
    hour=9,
    minute=0,
    duration=30,
    priority="Medium",
    frequency="once",
) -> Task:
    """Return a Task scheduled for today at the given hour."""
    return Task(
        description=description,
        pet_name=pet_name,
        time=datetime.now().replace(
            hour=hour, minute=minute, second=0, microsecond=0
        ),
        duration_minutes=duration,
        priority=priority,
        frequency=frequency,
    )


def make_scheduler(pet_name="Buddy") -> tuple:
    """Return a (scheduler, pet, owner) tuple."""
    owner = Owner(name="Test Owner")
    pet = Pet(name=pet_name, species="Dog")
    owner.add_pet(pet)
    return Scheduler(owner), pet, owner


# ── Happy Path Tests ───────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """mark_complete() should set completed to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """add_task() should increase the pet's task count by 1."""
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1
    pet.add_task(make_task(description="Second Task"))
    assert len(pet.get_tasks()) == 2


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return tasks in ascending time order."""
    scheduler, pet, _ = make_scheduler()
    t1 = make_task(description="Late",  hour=18)
    t2 = make_task(description="Early", hour=7)
    t3 = make_task(description="Mid",   hour=12)
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    sorted_tasks = scheduler.sort_by_time(pet.get_tasks())
    times = [t.time.hour for t in sorted_tasks]
    assert times == sorted(times)


def test_daily_task_creates_next_day_recurrence():
    """Completing a daily task should create a new task for tomorrow."""
    scheduler, pet, _ = make_scheduler()
    task = make_task(frequency="daily")
    pet.add_task(task)

    scheduler.mark_task_complete(task.id)

    tasks = pet.get_tasks()
    assert any(t.completed for t in tasks)
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    assert any(t.time.date() == tomorrow for t in tasks)


def test_weekly_task_creates_next_week_recurrence():
    """Completing a weekly task should create a new task for next week."""
    scheduler, pet, _ = make_scheduler()
    task = make_task(frequency="weekly")
    pet.add_task(task)

    scheduler.mark_task_complete(task.id)

    tasks = pet.get_tasks()
    next_week = (datetime.now() + timedelta(weeks=1)).date()
    assert any(t.time.date() == next_week for t in tasks)


def test_conflict_detection_flags_overlapping_tasks():
    """detect_conflicts() should flag tasks that overlap in time."""
    scheduler, pet, _ = make_scheduler()
    t1 = make_task(description="Task A", hour=10, minute=0,  duration=60)
    t2 = make_task(description="Task B", hour=10, minute=30, duration=60)
    pet.add_task(t1)
    pet.add_task(t2)

    conflicts = scheduler.detect_conflicts(pet.get_tasks())
    assert len(conflicts) == 1
    assert {conflicts[0][0].description, conflicts[0][1].description} == {
        "Task A", "Task B"
    }


def test_filter_tasks_by_pet_name():
    """filter_tasks() should return only tasks matching the given pet name."""
    scheduler, pet, owner = make_scheduler()
    luna = Pet(name="Luna", species="Cat")
    owner.add_pet(luna)

    pet.add_task(make_task(pet_name="Buddy"))
    luna.add_task(make_task(description="Luna Task", pet_name="Luna"))

    all_tasks = owner.get_all_tasks()
    filtered = scheduler.filter_tasks(all_tasks, pet_name="Luna")
    assert len(filtered) == 1
    assert filtered[0].pet_name == "Luna"


# ── Edge Case Tests ────────────────────────────────────────────────────────

def test_pet_with_no_tasks_returns_empty_list():
    """A pet with no tasks should return an empty list without errors."""
    pet = Pet(name="Empty", species="Cat")
    assert pet.get_tasks() == []


def test_once_task_does_not_create_recurrence():
    """Completing a once task should NOT create any new tasks."""
    scheduler, pet, _ = make_scheduler()
    task = make_task(frequency="once")
    pet.add_task(task)

    scheduler.mark_task_complete(task.id)

    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0].completed is True


def test_double_completion_does_not_duplicate_recurrence():
    """Marking a task complete twice should not create two recurrences."""
    scheduler, pet, _ = make_scheduler()
    task = make_task(frequency="daily")
    pet.add_task(task)

    scheduler.mark_task_complete(task.id)
    scheduler.mark_task_complete(task.id)

    assert len(pet.get_tasks()) == 2  # original + 1 recurrence only


def test_non_overlapping_tasks_produce_no_conflicts():
    """Tasks at completely different times should produce zero conflicts."""
    scheduler, pet, _ = make_scheduler()
    pet.add_task(make_task(description="Morning", hour=8,  duration=30))
    pet.add_task(make_task(description="Noon",    hour=12, duration=30))
    pet.add_task(make_task(description="Evening", hour=18, duration=30))

    conflicts = scheduler.detect_conflicts(pet.get_tasks())
    assert conflicts == []


def test_tasks_ending_exactly_when_next_starts_no_conflict():
    """Task A ending exactly when Task B starts should NOT be a conflict."""
    scheduler, pet, _ = make_scheduler()
    # Task A: 9:00 AM for 60 min → ends at 10:00 AM
    # Task B: 10:00 AM → starts exactly when A ends
    pet.add_task(make_task(description="Task A", hour=9,  minute=0,  duration=60))
    pet.add_task(make_task(description="Task B", hour=10, minute=0, duration=30))

    conflicts = scheduler.detect_conflicts(pet.get_tasks())
    assert conflicts == []


def test_filter_tasks_no_filters_returns_all():
    """filter_tasks() with no arguments should return all tasks unchanged."""
    scheduler, pet, _ = make_scheduler()
    pet.add_task(make_task(description="Task 1"))
    pet.add_task(make_task(description="Task 2"))
    pet.add_task(make_task(description="Task 3"))

    all_tasks = pet.get_tasks()
    filtered = scheduler.filter_tasks(all_tasks)
    assert len(filtered) == 3


def test_invalid_frequency_does_not_crash():
    """A task with an unrecognized frequency should not crash on completion."""
    scheduler, pet, _ = make_scheduler()
    task = make_task(frequency="monthly")
    pet.add_task(task)

    scheduler.mark_task_complete(task.id)

    assert pet.get_tasks()[0].completed is True
    assert len(pet.get_tasks()) == 1 