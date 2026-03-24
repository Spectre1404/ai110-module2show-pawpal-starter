# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.


## Smarter Scheduling

PawPal+ goes beyond a simple task list by implementing intelligent scheduling algorithms:

### Sorting
- Tasks are sorted chronologically by default using Python's `sorted()` with a `lambda` key
- Optional priority-first sorting ranks High tasks before Medium and Low, then sorts by time within each group using a tuple key: `(priority_weight, time)`

### Filtering
- Tasks can be filtered by any combination of pet name, completion status, and priority
- Chained list comprehensions keep filtering logic clean and readable

### Recurring Tasks
- Daily tasks auto-schedule the next occurrence using `timedelta(days=1)` when marked complete
- Weekly tasks use `timedelta(weeks=1)` for the next occurrence
- A completion guard prevents duplicate recurrences if a task is accidentally marked complete twice
- Tasks with `frequency="once"` are never rescheduled

### Conflict Detection
- The Scheduler detects overlapping tasks using interval logic:
  `task_a.time < task_b_end AND task_b.time < task_a_end`
- Implemented using `itertools.combinations` for cleaner, more Pythonic pair iteration
- Returns warning pairs without crashing — the app stays running and notifies the user
- Time complexity: O(n²), acceptable for daily schedules with a small number of tasks

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest -v