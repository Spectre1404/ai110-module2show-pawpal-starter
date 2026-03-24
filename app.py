import streamlit as st
from datetime import datetime, date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("PawPal+")

# ── Session State Initialization ───────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)
if "owner_name_set" not in st.session_state:
    st.session_state.owner_name_set = False

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ── Scenario Info ──────────────────────────────────────────────────────────
with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ── Step 1: Set Owner Name ─────────────────────────────────────────────────
st.subheader("Step 1: Set Owner Name")
owner_name_input = st.text_input("Your name", value=owner.name or "Jordan")
if st.button("Set Owner Name"):
    st.session_state.owner.name = owner_name_input
    st.session_state.owner_name_set = True
    st.success(f"Owner set to: {owner_name_input}")

st.divider()

# ── Step 2: Add a Pet ──────────────────────────────────────────────────────
st.subheader("Step 2: Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    if pet_name.strip() == "":
        st.warning("Please enter a pet name.")
    elif owner.get_pet(pet_name):
        st.warning(f"{pet_name} is already registered.")
    else:
        new_pet = Pet(name=pet_name, species=species)
        owner.add_pet(new_pet)
        st.success(f"Added pet: {pet_name} ({species})")

# Show registered pets
if owner.pets:
    st.write("Registered pets:")
    for p in owner.pets.values():
        st.write(f"  - {p.name} ({p.species})")
else:
    st.info("No pets registered yet.")

st.divider()

# ── Step 3: Schedule a Task ────────────────────────────────────────────────
st.subheader("Step 3: Schedule a Task")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_pet = st.selectbox("Pet", options=list(owner.pets.keys()))
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        task_time = st.time_input("Time", value=datetime.now().replace(hour=8, minute=0))
    with col5:
        task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col6:
        task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add Task"):
        pet = owner.get_pet(task_pet)
        if pet:
            new_task = Task(
                description=task_title,
                pet_name=task_pet,
                time=datetime.combine(date.today(), task_time),
                duration_minutes=int(task_duration),
                priority=task_priority,
                frequency=task_frequency,
            )
            pet.add_task(new_task)
            st.success(f"Task '{task_title}' scheduled for {task_pet} at {task_time}")

st.divider()

# ── Step 4: View Today's Schedule ─────────────────────────────────────────
st.subheader("Step 4: Today's Schedule")

if st.button("Generate Schedule"):
    all_today = scheduler.get_todays_tasks(date.today())
    all_today = scheduler.sort_by_time(all_today)

    # Conflict detection
    conflicts = scheduler.detect_conflicts(all_today)
    if conflicts:
        for t1, t2 in conflicts:
            st.warning(
                f"Conflict at {t1.time.strftime('%I:%M %p')}: "
                f"{t1.pet_name} ({t1.description}) vs "
                f"{t2.pet_name} ({t2.description})"
            )

    if not all_today:
        st.info("No tasks scheduled for today.")
    else:
        rows = [
            {
                "Time": t.time.strftime("%I:%M %p"),
                "Pet": t.pet_name,
                "Task": t.description,
                "Priority": t.priority,
                "Duration (min)": t.duration_minutes,
                "Status": "Done" if t.completed else "Pending",
            }
            for t in all_today
        ]
        st.table(rows)
        st.success(f"Total tasks today: {len(all_today)}")