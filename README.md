# 🐾 PawPal+

**PawPal+** is a smart pet care management system that helps owners keep
their pets happy and healthy. It tracks daily routines — feedings, walks,
medications, and appointments — while using algorithmic logic to organize
and prioritize tasks.

Built with Python OOP and Streamlit.

---

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
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

See `uml_final.png` for the full class diagram.

---

## ✨ Features

### Task Management
- **Add pets and tasks** through a clean Streamlit UI — all data persists
  in `st.session_state` across page reruns
- **Mark tasks complete** via a dropdown — the system automatically
  identifies the task by UUID and updates its status

### Smarter Scheduling

#### Sorting
- Tasks are sorted chronologically by default using Python's `sorted()`
  with a `lambda t: t.time` key
- Optional **priority-first sorting** ranks High tasks before Medium and
  Low, then sorts by time within each group using a tuple key:
  `(priority_weight, time)`

#### Filtering
- Tasks can be filtered by any combination of **pet name**,
  **completion status**, and **priority**
- Implemented with chained list comprehensions for clean, readable logic

#### Recurring Tasks
- Daily tasks auto-schedule the next occurrence using `timedelta(days=1)`
  when marked complete
- Weekly tasks use `timedelta(weeks=1)` for the next occurrence
- A **completion guard** (`if task.completed: return`) prevents duplicate
  recurrences if a task is accidentally marked complete twice
- Tasks with `frequency="once"` are never rescheduled

#### Conflict Detection
- The Scheduler detects overlapping tasks using interval logic:
  `task_a.time < task_b_end AND task_b.time < task_a_end`
- Implemented using `itertools.combinations` for Pythonic pair iteration
- Returns **warning pairs without crashing** — displayed as
  `st.warning()` banners in the UI
- Time complexity: O(n²), acceptable for daily schedules

---

## 🚀 Running the App

### Prerequisites

```bash
pip install streamlit pytest

#Project Structure
pawpal-starter/
├── app.py               # Streamlit UI
├── pawpal_system.py     # Core OOP logic layer
├── main.py              # CLI demo script
├── uml_final.png        # Final class diagram
├── reflection.md        # Design and AI collaboration reflection
├── tests/
│   └── test_pawpal.py   # Automated pytest suite (14 tests)
└── README.md