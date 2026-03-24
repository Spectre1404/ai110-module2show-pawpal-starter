# PawPal+ Project Reflection

## 1. System Design
System Design
Core User Actions

1. Register a Pet
As an owner, I can add a new pet to my profile by providing its name, species, breed, and age. This creates a dedicated profile for each pet so all their tasks and schedules stay organized separately.

2. Schedule a Care Task
As an owner, I can schedule a care activity (such as a walk, feeding, medication, or vet appointment) for a specific pet by setting a description, time, duration, priority level, and how often it repeats (once, daily, or weekly). This ensures no important routine gets missed.

3. View and Manage Today's Schedule
As an owner, I can view a sorted, filtered list of all tasks due today across all my pets — seeing which are done and which are pending — and mark tasks as complete directly from the schedule. This gives me a clear daily overview at a glance.

Why These Three?

These three actions cover the full lifecycle of the app:

Register a Pet → sets up the data model (Owner → Pet relationship).

Schedule a Task → populates the system with actionable data (Pet → Task relationship).

View Today's Schedule → triggers the Scheduler's sorting, filtering, and conflict detection logic.

Every other feature (recurring tasks, conflict warnings, filtering by priority) is an extension of one of these three core interactions.

**a. Initial design**

## 1a. Initial Design

For PawPal+, I designed four classes, each with a clear, single responsibility:

**Task** is a Python dataclass that represents one care activity for a pet.
It holds all the details needed to describe and schedule that activity: a unique
ID, description, the pet it belongs to, scheduled time, duration, priority level,
frequency (once/daily/weekly), and completion status. Its only behavior is
`mark_complete()`, keeping it a focused data object.

**Pet** is a Python dataclass that acts as a container for one animal's profile
and its associated tasks. It stores basic info (name, species, breed, age) and
owns a list of Task objects. Its methods `add_task()` and `get_tasks()` are
intentionally simple — Pet's job is to hold data, not process it.

**Owner** is a regular class that acts as the top-level manager of the system.
It holds a dictionary of Pet objects (keyed by name for fast lookup) and provides
three methods: registering a new pet, retrieving a pet by name, and aggregating
all tasks across every pet into one flat list. Owner bridges the UI layer and
the data layer.

**Scheduler** is the algorithmic engine of the app. It takes an Owner as input
and operates on its pets' tasks without storing any data itself. It is responsible
for filtering today's tasks, sorting by time, filtering by pet/status/priority,
marking tasks complete (with recurrence logic), and detecting time conflicts.
Keeping all scheduling logic in Scheduler means Pet and Owner stay clean and
focused.

The key design decision was to give Scheduler a *dependency* on Owner (not
ownership), so Owner and Pet remain reusable data containers while Scheduler
handles all the intelligent behavior.

**b. Design changes**

Copilot flagged two issues after reviewing the skeleton:

1. **Task IDs could collide** if manually assigned strings like "1", "2" are reused.
   I will use `uuid.uuid4()` when creating tasks in main.py and app.py to ensure
   every task ID is globally unique.

2. **`get_tasks()` should return a copy** of the internal list to prevent external
   code from accidentally mutating Pet's task list directly. I will implement it
   as `return list(self.tasks)` rather than `return self.tasks`.

The overall class structure and responsibility separation was confirmed as clean
with no structural changes needed.

---

## 2. Scheduling Logic and Tradeoffs

## Phase 2 Reflection

### Implementation Summary
I implemented all four classes in pawpal_system.py following the UML skeleton
from Phase 1. Each method was built to do exactly one thing:

- Task.mark_complete() simply flips the completed flag to True.
- Pet.add_task() and get_tasks() keep the task list encapsulated, returning
  a copy to prevent accidental mutation from outside the class.
- Owner.get_all_tasks() aggregates tasks from all pets into one flat list,
  acting as the bridge between the data layer and the Scheduler.
- Scheduler methods handle all algorithmic logic: filtering by date, sorting
  by time, filtering by attributes, conflict detection, and recurring task
  creation using timedelta.

### CLI Verification
Running python main.py confirmed that all 6 tasks display in sorted order,
filtering works correctly by pet and priority, and marking a daily task
complete automatically creates the next day's recurrence.

### Testing
Both pytest tests passed in 0.01 seconds, confirming that mark_complete()
and add_task() behave correctly at the unit level.

## Phase 4 - Recurring Tasks

Recurring task logic lives entirely in `Scheduler.mark_task_complete()`.
When a task with `frequency="daily"` is marked complete, Python's `timedelta(days=1)`
calculates the next due date by adding one day to the original task's `time`
attribute. For `frequency="weekly"`, `timedelta(weeks=1)` adds 7 days.
A new `Task` object is cloned with the updated time and added to the pet's
task list automatically. Tasks with `frequency="once"` return immediately
without creating a recurrence. A guard was added to prevent duplicate
recurrences if a task is accidentally marked complete twice.

## Phase 5 - Testing and Verification

### Test Plan
Before writing any tests, I reviewed pawpal_system.py and identified the
five most critical behaviors to verify:

1. Task completion -- mark_complete() correctly flips completed to True
2. Pet task management -- add_task() grows the task list without mutation
3. Sorting correctness -- sort_by_time() returns chronological order
4. Recurrence logic -- daily/weekly tasks auto-schedule on completion
5. Conflict detection -- overlapping intervals are correctly identified

I opened a new Copilot Chat session dedicated to testing and used #codebase
to generate a full test plan covering both happy paths and edge cases.

### AI-Generated Tests
Copilot suggested 10 test scenarios across happy paths and edge cases.
I reviewed each suggestion and added 4 additional tests of my own:
- test_tasks_ending_exactly_when_next_starts_no_conflict
- test_filter_tasks_no_filters_returns_all
- test_invalid_frequency_does_not_crash
- test_weekly_task_creates_next_week_recurrence

One Copilot suggestion I modified: it proposed testing "large task lists
for performance" but this is not meaningful for a pet scheduler with fewer
than 50 tasks per day. I replaced it with the boundary condition test
(tasks ending exactly when another starts) which is more relevant.

### Results
14/14 tests passed in 0.02 seconds with zero failures or warnings.

The double-completion guard test (test_double_completion_does_not_duplicate_
recurrence) was the most valuable edge case -- it directly verified the
fix added in Phase 4 where completing a daily task twice would previously
create two next-day recurrences.

### Confidence Level: 5/5
The test suite covers all core behaviors introduced in Phases 2 and 4.
Known untested limitations:
- Timezone-aware datetime handling (out of scope)
- Performance at scale beyond 50 tasks (not relevant for daily pet care)
- UI state persistence across browser refreshes (covered manually)

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
