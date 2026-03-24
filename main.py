from datetime import datetime, date, timedelta
from tabulate import tabulate
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Challenge 3 & 4: Emoji maps ───────────────────────────────────────────────
PRIORITY_EMOJI = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
SPECIES_EMOJI  = {"dog": "🐶", "cat": "🐱", "bird": "🐦",
                  "rabbit": "🐰", "fish": "🐠", "other": "🐾"}


# ─────────────────────────────────────────────
# Demo Data
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# Challenge 4: tabulate-powered print helpers
# ─────────────────────────────────────────────

def _task_rows(tasks: list[Task], owner: Owner) -> list[list]:
    """Build display rows for a tabulate table from a task list."""
    rows = []
    for t in tasks:
        pet        = owner.get_pet(t.pet_name)
        species    = pet.species.lower() if pet else "other"
        p_emoji    = PRIORITY_EMOJI.get(t.priority, "⚪")
        s_emoji    = SPECIES_EMOJI.get(species, "🐾")
        status     = "✅" if t.completed else "⏳"
        rows.append([
            status,
            f"{p_emoji} {t.priority}",
            f"{s_emoji} {t.pet_name}",
            t.description,
            t.time.strftime("%I:%M %p"),
            f"{t.duration_minutes} min",
            t.frequency.capitalize(),
        ])
    return rows


def print_schedule(scheduler: Scheduler) -> None:
    """Print a tabulate-formatted Today's Schedule to the terminal."""
    today = date.today()
    tasks = scheduler.sort_by_time(scheduler.get_todays_tasks(today))

    print(f"\n🐾  PawPal+ — Today's Schedule ({today})")
    if not tasks:
        print("  No tasks scheduled for today.\n")
        return

    headers = ["", "Priority", "Pet", "Task", "Time", "Duration", "Repeat"]
    rows    = _task_rows(tasks, scheduler.owner)
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print(f"  Total tasks: {len(tasks)}\n")


def print_conflicts(scheduler: Scheduler) -> None:
    """Print any scheduling conflicts detected for today."""
    today     = date.today()
    tasks     = scheduler.get_todays_tasks(today)
    conflicts = scheduler.detect_conflicts(tasks)

    if conflicts:
        print("⚠️  CONFLICTS DETECTED:")
        rows = []
        for t1, t2 in conflicts:
            t1_end = t1.time + timedelta(minutes=t1.duration_minutes)
            rows.append([
                f"{PRIORITY_EMOJI.get(t1.priority,'')} {t1.description}",
                f"{t1.time.strftime('%I:%M %p')} – {t1_end.strftime('%I:%M %p')}",
                "overlaps ↔",
                f"{PRIORITY_EMOJI.get(t2.priority,'')} {t2.description}",
                t2.time.strftime("%I:%M %p"),
            ])
        print(tabulate(rows,
                       headers=["Task A", "Window A", "", "Task B", "Start B"],
                       tablefmt="rounded_outline"))
        print()
    else:
        print("✅  No scheduling conflicts detected.\n")


# ─────────────────────────────────────────────
# Demo Functions
# ─────────────────────────────────────────────

def demo_filtering(scheduler: Scheduler) -> None:
    """Demo filtering tasks by pet name, status, and priority."""
    today     = date.today()
    all_tasks = scheduler.get_todays_tasks(today)

    bella_tasks  = scheduler.filter_tasks(all_tasks, pet_name="Bella")
    pending      = scheduler.filter_tasks(all_tasks, completed=False)
    high_priority = scheduler.filter_tasks(all_tasks, priority="High")

    print("🔍  FILTERING DEMO")
    print(tabulate(
        [
            ["Bella's tasks today",  len(bella_tasks)],
            ["Pending tasks",        len(pending)],
            ["High priority tasks",  len(high_priority)],
        ],
        headers=["Filter", "Count"],
        tablefmt="rounded_outline",
    ))

    print("\n  Bella's tasks:")
    for t in bella_tasks:
        print(f"    {PRIORITY_EMOJI.get(t.priority,'⚪')}  "
              f"{t.time.strftime('%I:%M %p')}  {t.description}")
    print()


def demo_recurrence(scheduler: Scheduler) -> None:
    """Demo marking a daily task complete and verifying recurrence."""
    today = date.today()
    tasks = scheduler.get_todays_tasks(today)
    morning_walk = next(
        (t for t in tasks if t.description == "Morning Walk"), None
    )

    if morning_walk:
        print(f"🔄  Marking '{morning_walk.description}' as complete...")
        scheduler.mark_task_complete(morning_walk.id)
        tomorrow_tasks = scheduler.get_todays_tasks(today + timedelta(days=1))
        recurred = next(
            (t for t in tomorrow_tasks if t.description == "Morning Walk"), None
        )
        status = f"✅ rescheduled for {recurred.time.strftime('%b %d %I:%M %p')}" \
                 if recurred else "⚠️  no recurrence found"
        print(f"  Next occurrence: {status}\n")


def demo_sorting_and_filtering(scheduler: Scheduler) -> None:
    """Demonstrate sorting and filtering with tasks added out of order."""
    print("─" * 60)
    print("  SORTING & FILTERING DEMO")
    print("─" * 60)

    temp_owner = Owner(name="Sort Test")
    temp_pet   = Pet(name="Rex", species="Dog")

    temp_pet.add_task(Task(
        description="Evening Walk",      pet_name="Rex",
        time=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0),
        duration_minutes=30, priority="Low",    frequency="daily",
    ))
    temp_pet.add_task(Task(
        description="Morning Medication", pet_name="Rex",
        time=datetime.now().replace(hour=7,  minute=0, second=0, microsecond=0),
        duration_minutes=5,  priority="High",   frequency="daily",
    ))
    temp_pet.add_task(Task(
        description="Midday Feed",        pet_name="Rex",
        time=datetime.now().replace(hour=12, minute=0, second=0, microsecond=0),
        duration_minutes=10, priority="Medium", frequency="daily",
    ))

    temp_owner.add_pet(temp_pet)
    temp_scheduler = Scheduler(temp_owner)
    raw_tasks      = temp_pet.get_tasks()

    def task_table(tasks, title):
        print(f"\n  {title}")
        rows = [[f"{PRIORITY_EMOJI.get(t.priority,'⚪')} {t.priority}",
                 t.time.strftime("%I:%M %p"), t.description] for t in tasks]
        print(tabulate(rows, headers=["Priority", "Time", "Task"],
                       tablefmt="rounded_outline"))

    task_table(raw_tasks,                                             "As added (unsorted):")
    task_table(temp_scheduler.sort_by_time(raw_tasks),               "sort_by_time():")
    task_table(temp_scheduler.sort_by_time(raw_tasks,
               priority_first=True),                                  "sort_by_time(priority_first=True):")

    pending = temp_scheduler.filter_tasks(raw_tasks, completed=False)
    high    = temp_scheduler.filter_tasks(raw_tasks, priority="High")
    print(f"\n  Pending tasks (completed=False): {len(pending)}")
    print(f"  High priority only: {len(high)}")
    for t in high:
        print(f"    - {t.description}")
    print()


def demo_conflict_detection(scheduler: Scheduler) -> None:
    """Demo conflict detection by scheduling overlapping tasks."""
    print("─" * 60)
    print("  CONFLICT DETECTION DEMO")
    print("─" * 60)

    temp_owner    = Owner(name="Conflict Test")
    temp_pet      = Pet(name="Max", species="Dog")
    conflict_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)

    temp_pet.add_task(Task(
        description="Vet Appointment",  pet_name="Max",
        time=conflict_time,             duration_minutes=60,
        priority="High",                frequency="once",
    ))
    temp_pet.add_task(Task(
        description="Grooming Session", pet_name="Max",
        time=conflict_time,             duration_minutes=45,
        priority="Medium",              frequency="once",
    ))
    temp_pet.add_task(Task(
        description="Training Class",   pet_name="Max",
        time=conflict_time.replace(minute=30), duration_minutes=60,
        priority="Medium",              frequency="weekly",
    ))

    temp_owner.add_pet(temp_pet)
    temp_scheduler = Scheduler(temp_owner)
    todays_tasks   = temp_scheduler.get_todays_tasks(date.today())
    conflicts      = temp_scheduler.detect_conflicts(todays_tasks)

    if conflicts:
        print(f"\n  ⚠️  {len(conflicts)} conflict(s) detected:")
        rows = []
        for t1, t2 in conflicts:
            t1_end = t1.time + timedelta(minutes=t1.duration_minutes)
            rows.append([
                f"{PRIORITY_EMOJI.get(t1.priority,'')} {t1.description}",
                f"{t1.time.strftime('%I:%M %p')}–{t1_end.strftime('%I:%M %p')}",
                "↔",
                f"{PRIORITY_EMOJI.get(t2.priority,'')} {t2.description}",
            ])
        print(tabulate(rows,
                       headers=["Task A", "Window", "", "Task B"],
                       tablefmt="rounded_outline"))
    else:
        print("  No conflicts detected.")
    print()


# ── Challenge 1: Next Available Slot Demo ─────────────────────────────────────

def demo_next_available_slot(scheduler: Scheduler) -> None:
    """Demo the find_next_available_slot() algorithm."""
    print("─" * 60)
    print("  NEXT AVAILABLE SLOT DEMO  (Challenge 1)")
    print("─" * 60)

    for duration in [15, 30, 60, 90]:
        slot = scheduler.find_next_available_slot(duration_minutes=duration)
        if slot:
            print(f"  ✅  Next open {duration}-min slot: "
                  f"{slot.strftime('%I:%M %p')}")
        else:
            print(f"  ❌  No open {duration}-min slot found today (8 AM–8 PM)")
    print()


# ── Challenge 2: JSON Persistence Demo ───────────────────────────────────────

def demo_persistence(owner: Owner) -> None:
    """Demo save_to_json and load_from_json round-trip."""
    print("─" * 60)
    print("  JSON PERSISTENCE DEMO  (Challenge 2)")
    print("─" * 60)

    owner.save_to_json("data.json")
    print("  💾  Saved to data.json")

    restored = Owner.load_from_json("data.json")
    total    = len(restored.get_all_tasks())
    print(f"  📂  Loaded from data.json — owner: '{restored.name}', "
          f"pets: {len(restored.pets)}, tasks: {total}")
    print(f"  ✅  Round-trip successful: "
          f"{'PASS' if total == len(owner.get_all_tasks()) else 'FAIL'}\n")


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    owner     = build_demo_data()
    scheduler = Scheduler(owner)

    print_schedule(scheduler)
    print_conflicts(scheduler)
    demo_filtering(scheduler)
    demo_recurrence(scheduler)
    demo_sorting_and_filtering(scheduler)
    demo_conflict_detection(scheduler)
    demo_next_available_slot(scheduler)       # Challenge 1
    demo_persistence(owner)                   # Challenge 2

    print("📅  Updated schedule after marking Morning Walk complete:")
    print_schedule(scheduler)