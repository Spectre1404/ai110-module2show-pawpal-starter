from datetime import datetime, date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


def build_demo_data() -> Owner:
    """Create a demo owner with two pets and several tasks."""
    owner = Owner(name="Shivansh")

    # --- Pet 1: Bella the dog ---
    bella = Pet(name="Bella", species="Dog", breed="Golden Retriever", age=3)

    bella.add_task(Task(
        description="Morning Walk",
        pet_name="Bella",
        time=datetime.now().replace(hour=7, minute=30, second=0, microsecond=0),
        duration_minutes=30,
        priority="High",
        frequency="daily",
    ))

    bella.add_task(Task(
        description="Feed Breakfast",
        pet_name="Bella",
        time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
        duration_minutes=10,
        priority="High",
        frequency="daily",
    ))

    bella.add_task(Task(
        description="Heartworm Medication",
        pet_name="Bella",
        time=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0),
        duration_minutes=5,
        priority="High",
        frequency="weekly",
    ))

    # --- Pet 2: Luna the cat ---
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=2)

    luna.add_task(Task(
        description="Feed Lunch",
        pet_name="Luna",
        time=datetime.now().replace(hour=12, minute=0, second=0, microsecond=0),
        duration_minutes=10,
        priority="Medium",
        frequency="daily",
    ))

    luna.add_task(Task(
        description="Vet Appointment",
        pet_name="Luna",
        time=datetime.now().replace(hour=15, minute=30, second=0, microsecond=0),
        duration_minutes=60,
        priority="High",
        frequency="once",
    ))

    luna.add_task(Task(
        description="Evening Playtime",
        pet_name="Luna",
        time=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0),
        duration_minutes=20,
        priority="Low",
        frequency="daily",
    ))

    owner.add_pet(bella)
    owner.add_pet(luna)
    return owner


def print_schedule(scheduler: Scheduler) -> None:
    """Print a formatted Today's Schedule to the terminal."""
    today = date.today()
    tasks = scheduler.get_todays_tasks(today)
    tasks = scheduler.sort_by_time(tasks)

    print("\n" + "-" * 55)
    print(f"  PawPal+ -- Today's Schedule ({today})")
    print("-" * 55)

    if not tasks:
        print("  No tasks scheduled for today.")
    else:
        for task in tasks:
            status = "[DONE]" if task.completed else "[    ]"
            time_str = task.time.strftime("%I:%M %p")
            print(
                f"  {status}  {time_str}  "
                f"{task.priority:<6}  "
                f"{task.pet_name:<6}  "
                f"{task.description}  "
                f"({task.duration_minutes} min)"
            )

    print("-" * 55)
    print(f"  Total tasks: {len(tasks)}")
    print("-" * 55 + "\n")


def print_conflicts(scheduler: Scheduler) -> None:
    """Print any scheduling conflicts detected for today."""
    today = date.today()
    tasks = scheduler.get_todays_tasks(today)
    conflicts = scheduler.detect_conflicts(tasks)

    if conflicts:
        print("WARNING -- CONFLICTS DETECTED:")
        for t1, t2 in conflicts:
            print(
                f"  {t1.time.strftime('%I:%M %p')}: "
                f"{t1.pet_name} ({t1.description}) "
                f"conflicts with {t2.pet_name} ({t2.description})"
            )
        print()
    else:
        print("No scheduling conflicts detected.\n")


def demo_filtering(scheduler: Scheduler) -> None:
    """Demo filtering tasks by pet name, status, and priority."""
    today = date.today()
    all_tasks = scheduler.get_todays_tasks(today)

    bella_tasks = scheduler.filter_tasks(all_tasks, pet_name="Bella")
    print(f"Bella's tasks today: {len(bella_tasks)}")
    for t in bella_tasks:
        print(f"  - {t.description} at {t.time.strftime('%I:%M %p')}")

    pending = scheduler.filter_tasks(all_tasks, completed=False)
    print(f"\nPending tasks: {len(pending)}")

    high_priority = scheduler.filter_tasks(all_tasks, priority="High")
    print(f"High priority tasks: {len(high_priority)}\n")


def demo_recurrence(scheduler: Scheduler) -> None:
    """Demo marking a daily task complete and verifying recurrence."""
    today = date.today()
    tasks = scheduler.get_todays_tasks(today)
    morning_walk = next(
        (t for t in tasks if t.description == "Morning Walk"), None
    )

    if morning_walk:
        print(f"Marking '{morning_walk.description}' as complete...")
        scheduler.mark_task_complete(morning_walk.id)
        print("Done. Next recurrence has been auto-scheduled for tomorrow.\n")


def demo_sorting_and_filtering(scheduler: Scheduler) -> None:
    """Demonstrate sorting and filtering with tasks added out of order."""
    print("-" * 55)
    print("  SORTING AND FILTERING DEMO")
    print("-" * 55)

    # Create a temporary owner with tasks added OUT OF ORDER intentionally
    temp_owner = Owner(name="Sort Test")
    temp_pet = Pet(name="Rex", species="Dog")

    # Added deliberately out of chronological order
    temp_pet.add_task(Task(
        description="Evening Walk",
        pet_name="Rex",
        time=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0),
        duration_minutes=30,
        priority="Low",
        frequency="daily",
    ))
    temp_pet.add_task(Task(
        description="Morning Medication",
        pet_name="Rex",
        time=datetime.now().replace(hour=7, minute=0, second=0, microsecond=0),
        duration_minutes=5,
        priority="High",
        frequency="daily",
    ))
    temp_pet.add_task(Task(
        description="Midday Feed",
        pet_name="Rex",
        time=datetime.now().replace(hour=12, minute=0, second=0, microsecond=0),
        duration_minutes=10,
        priority="Medium",
        frequency="daily",
    ))

    temp_owner.add_pet(temp_pet)
    temp_scheduler = Scheduler(temp_owner)

    raw_tasks = temp_pet.get_tasks()

    # Print UNSORTED order
    print("\n  Tasks as added (unsorted):")
    for t in raw_tasks:
        print(f"    {t.time.strftime('%I:%M %p')} - {t.description} [{t.priority}]")

    # Print SORTED by time
    sorted_tasks = temp_scheduler.sort_by_time(raw_tasks)
    print("\n  After sort_by_time():")
    for t in sorted_tasks:
        print(f"    {t.time.strftime('%I:%M %p')} - {t.description} [{t.priority}]")

    # Print SORTED by priority first
    priority_sorted = temp_scheduler.sort_by_time(raw_tasks, priority_first=True)
    print("\n  After sort_by_time(priority_first=True):")
    for t in priority_sorted:
        print(f"    {t.time.strftime('%I:%M %p')} - {t.description} [{t.priority}]")

    # Filter by completion status
    pending = temp_scheduler.filter_tasks(raw_tasks, completed=False)
    print(f"\n  Pending tasks (filter completed=False): {len(pending)}")

    # Filter by priority
    high = temp_scheduler.filter_tasks(raw_tasks, priority="High")
    print(f"  High priority tasks only: {len(high)}")
    for t in high:
        print(f"    - {t.description}")

    print("-" * 55 + "\n")

def demo_conflict_detection(scheduler: Scheduler) -> None:
    """Demo conflict detection by scheduling two tasks at the same time."""
    print("-" * 55)
    print("  CONFLICT DETECTION DEMO")
    print("-" * 55)

    # Create a temporary owner with conflicting tasks
    temp_owner = Owner(name="Conflict Test")
    temp_pet = Pet(name="Max", species="Dog")

    conflict_time = datetime.now().replace(
        hour=10, minute=0, second=0, microsecond=0
    )

    # Two tasks starting at the same time — direct conflict
    temp_pet.add_task(Task(
        description="Vet Appointment",
        pet_name="Max",
        time=conflict_time,
        duration_minutes=60,
        priority="High",
        frequency="once",
    ))

    temp_pet.add_task(Task(
        description="Grooming Session",
        pet_name="Max",
        time=conflict_time,
        duration_minutes=45,
        priority="Medium",
        frequency="once",
    ))

    # A third task that overlaps (starts 30 min in, before first task ends)
    temp_pet.add_task(Task(
        description="Training Class",
        pet_name="Max",
        time=conflict_time.replace(minute=30),
        duration_minutes=60,
        priority="Medium",
        frequency="weekly",
    ))

    temp_owner.add_pet(temp_pet)
    temp_scheduler = Scheduler(temp_owner)

    from datetime import date
    todays_tasks = temp_scheduler.get_todays_tasks(date.today())
    conflicts = temp_scheduler.detect_conflicts(todays_tasks)

    if conflicts:
        print(f"\n  WARNING: {len(conflicts)} conflict(s) detected:")
        for t1, t2 in conflicts:
            t1_end = t1.time + timedelta(minutes=t1.duration_minutes)
            print(
                f"  -> {t1.description} "
                f"({t1.time.strftime('%I:%M %p')} - {t1_end.strftime('%I:%M %p')}) "
                f"conflicts with {t2.description} "
                f"({t2.time.strftime('%I:%M %p')})"
            )
    else:
        print("  No conflicts detected.")

    print("-" * 55 + "\n")

if __name__ == "__main__":
    owner = build_demo_data()
    scheduler = Scheduler(owner)

    print_schedule(scheduler)
    print_conflicts(scheduler)
    demo_filtering(scheduler)
    demo_recurrence(scheduler)
    demo_sorting_and_filtering(scheduler)
    demo_conflict_detection(scheduler)    # ← add this line

    print("Updated schedule after marking Morning Walk complete:")
    print_schedule(scheduler)