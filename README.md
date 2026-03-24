# 🐾 PawPal+

**PawPal+** is a smart pet care management system that helps owners schedule
and track daily routines — feedings, walks, medications, and appointments —
using algorithmic logic to organize and prioritize tasks.

Built with Python OOP and Streamlit.

---

## 📸 Demo

<a href="/course_images/ai110/Pawpal+ demo.png" target="_blank">
  <img src='/course_images/ai110/Pawpal+ demo.png'
       title='PawPal App'
       width=''
       alt='PawPal App'
       class='center-block' />
</a>

---

## 🏗️ System Architecture

PawPal+ is built with four core classes:

| Class | Responsibility |
|---|---|
| `Task` | Represents a single care activity with time, priority, duration, and frequency |
| `Pet` | Stores pet profile and owns a list of Tasks |
| `Owner` | Manages multiple pets and provides access to all tasks |
| `Scheduler` | Algorithmic engine that retrieves, sorts, filters, and manages tasks |

See `Pawpal+ - Updated diagram .png` for the full class diagram.

---

## ✨ Features

### Core Task Management
- **Add pets and tasks** through a clean Streamlit UI
- **Mark tasks complete** via a dropdown — tasks are identified by UUID
- **💾 Auto-save persistence** — pets and tasks survive app restarts via `data.json`

### Smarter Scheduling

#### Sorting
- Chronological sort using `sorted()` with a `lambda t: t.time` key
- Optional **priority-first sorting** using a tuple key `(priority_weight, time)` —
  High tasks always appear before Medium and Low

#### Filtering
- Filter by any combination of **pet name**, **completion status**, and **priority**
- Implemented with chained list comprehensions for clean, readable logic

#### Recurring Tasks
- Daily tasks reschedule using `timedelta(days=1)` on completion
- Weekly tasks reschedule using `timedelta(weeks=1)` on completion
- A **completion guard** prevents duplicate recurrences
- Tasks with `frequency="once"` are never rescheduled
- Uses `dataclasses.replace()` to clone recurring tasks immutably

#### Conflict Detection
- Detects overlapping tasks using interval logic:
  `task_a.time < task_b_end AND task_b.time < task_a_end`
- Uses `itertools.combinations` for Pythonic pair iteration
- Displays `st.warning()` banners in the UI — never crashes
- Time complexity: O(n²), appropriate for daily pet schedules

#### Next Available Slot *(Challenge 1)*
- Scans today's schedule in 30-minute increments (8 AM – 8 PM)
- Returns the first conflict-free window for a given task duration
- Displayed live in the Streamlit UI after generating a schedule

---

## 🚀 Running the App

### Prerequisites

```bash
pip install streamlit pytest tabulate