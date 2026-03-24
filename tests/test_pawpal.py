from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler


# HELPERS

def make_task(description="Test Task", pet_name="Buddy",
              hour=9, priority="Medium", frequency="once") -> Task:
    """Return a simple Task for use in tests."""
    return Task(
        description=description,
        pet_name=pet_name,
        time=datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0),
        duration_minutes=15,
        priority=priority,
        frequency=frequency,
    )


def make_scheduler() -> tuple:
    """Return a (scheduler, pet, owner) tuple pre-loaded with one pet."""
    owner = Owner(name="Test Owner")
    pet = Pet(name="Buddy", species="Dog")
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    return scheduler, pet, owner


# TEST 1

def test_mark_complete_changes_status():
    """Calling mark_complete() should set completed to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


# TEST 2

def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task count by 1."""
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1
    pet.add_task(make_task(description="Second Task"))
    assert len(pet.get_tasks()) == 2