import streamlit as st
from datetime import datetime, date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)
if "owner_name_set" not in st.session_state:
    st.session_state.owner_name_set = False

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler


st.title("PawPal+")
st.caption("Smart pet care scheduling for busy owners.")

with st.expander("About PawPal+", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care
tasks for their pet(s) based on constraints like time, priority, and frequency.

**Features:**
- Register pets and schedule care tasks
- Sort tasks by time or priority
- Detect scheduling conflicts and overlaps
- Auto-schedule recurring daily and weekly tasks
        """
    )

st.divider()

# ── Step 1: Owner Setup
st.subheader("Owner Setup")
owner_name_input = st.text_input(
    "Your name", value=owner.name or "", placeholder="e.g. Shivansh"
)
if st.button("Set Owner Name"):
    if owner_name_input.strip() == "":
        st.warning("Please enter your name.")
    else:
        st.session_state.owner.name = owner_name_input.strip()
        st.session_state.owner_name_set = True
        st.success(f"Welcome, {owner_name_input}!")

if owner.name:
    st.caption(f"Logged in as: **{owner.name}**")

st.divider()

# ── Step 2: Add a Pet 
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", placeholder="e.g. Bella")
with col2:
    species = st.selectbox("Species", ["Dog", "Cat", "Other"])
with col3:
    breed = st.text_input("Breed (optional)", placeholder="e.g. Golden Retriever")

if st.button("Add Pet"):
    if pet_name.strip() == "":
        st.warning("Please enter a pet name.")
    elif owner.get_pet(pet_name.strip()):
        st.warning(f"'{pet_name}' is already registered.")
    else:
        new_pet = Pet(
            name=pet_name.strip(),
            species=species,
            breed=breed.strip() or None,
        )
        owner.add_pet(new_pet)
        st.success(f"Added {species.lower()} '{pet_name}' successfully!")

if owner.pets:
    st.markdown("**Registered Pets:**")
    cols = st.columns(len(owner.pets))
    for i, pet in enumerate(owner.pets.values()):
        with cols[i]:
            st.info(f"**{pet.name}**\n\n{pet.species}" +
                   (f"\n\n_{pet.breed}_" if pet.breed else ""))
else:
    st.info("No pets registered yet. Add one above.")

st.divider()

# ── Step 3: Schedule a Task 
st.subheader("Schedule a Task")

if not owner.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        task_pet = st.selectbox("Pet", options=list(owner.pets.keys()))
        task_title = st.text_input("Task description", placeholder="e.g. Morning Walk")
        task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    with col2:
        task_time = st.time_input(
            "Scheduled time",
            value=datetime.now().replace(hour=8, minute=0)
        )
        task_duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=30
        )
        task_frequency = st.selectbox(
            "Frequency", ["once", "daily", "weekly"]
        )

    if st.button("Schedule Task"):
        if task_title.strip() == "":
            st.warning("Please enter a task description.")
        else:
            pet = owner.get_pet(task_pet)
            if pet:
                new_task = Task(
                    description=task_title.strip(),
                    pet_name=task_pet,
                    time=datetime.combine(date.today(), task_time),
                    duration_minutes=int(task_duration),
                    priority=task_priority,
                    frequency=task_frequency,
                )
                pet.add_task(new_task)
                st.success(
                    f"Scheduled '{task_title}' for {task_pet} at "
                    f"{task_time.strftime('%I:%M %p')} "
                    f"({task_priority} priority, {task_frequency})"
                )

st.divider()

# ── Step 4: Today's Schedule
st.subheader("Today's Schedule")

priority_first = st.checkbox(
    "Sort by priority first, then time",
    help="When checked, High priority tasks appear before Medium and Low"
)

filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    filter_pet = st.selectbox(
        "Filter by pet",
        options=["All"] + list(owner.pets.keys())
    )
with filter_col2:
    filter_status = st.selectbox(
        "Filter by status",
        options=["All", "Pending", "Done"]
    )
with filter_col3:
    filter_priority = st.selectbox(
        "Filter by priority",
        options=["All", "High", "Medium", "Low"]
    )

if st.button("Generate Schedule", type="primary"):
    all_today = scheduler.get_todays_tasks(date.today())
    all_today = scheduler.sort_by_time(all_today, priority_first=priority_first)

    # Apply filters
    if filter_pet != "All":
        all_today = scheduler.filter_tasks(all_today, pet_name=filter_pet)
    if filter_status == "Pending":
        all_today = scheduler.filter_tasks(all_today, completed=False)
    elif filter_status == "Done":
        all_today = scheduler.filter_tasks(all_today, completed=True)
    if filter_priority != "All":
        all_today = scheduler.filter_tasks(all_today, priority=filter_priority)

    # Conflict detection — run on full unfiltered today's tasks
    raw_today = scheduler.get_todays_tasks(date.today())
    conflicts = scheduler.detect_conflicts(raw_today)

    if conflicts:
        st.error(f"**{len(conflicts)} scheduling conflict(s) detected!**")
        for t1, t2 in conflicts:
            t1_end = t1.time + timedelta(minutes=t1.duration_minutes)
            st.warning(
                f"**Conflict:** {t1.pet_name} — {t1.description} "
                f"({t1.time.strftime('%I:%M %p')} - {t1_end.strftime('%I:%M %p')}) "
                f"overlaps with **{t2.pet_name} — {t2.description}** "
                f"({t2.time.strftime('%I:%M %p')})"
            )
    else:
        st.success("No scheduling conflicts detected.")

    st.markdown(f"**Showing {len(all_today)} task(s) for {date.today().strftime('%A, %B %d')}**")

    if not all_today:
        st.info("No tasks match the selected filters.")
    else:
        priority_icons = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
        rows = [
            {
                "Status": "Done" if t.completed else "Pending",
                "Time": t.time.strftime("%I:%M %p"),
                "Pet": t.pet_name,
                "Task": t.description,
                "Priority": f"{priority_icons.get(t.priority, '')} {t.priority}",
                "Duration": f"{t.duration_minutes} min",
                "Frequency": t.frequency,
            }
            for t in all_today
        ]
        st.table(rows)

    # Recurring tasks section
    recurring = scheduler.get_recurring_tasks()
    if recurring:
        st.markdown("---")
        st.markdown("**Recurring Tasks (auto-schedule active):**")
        for t in recurring:
            st.info(
                f"{t.pet_name}: **{t.description}** — "
                f"repeats {t.frequency} — "
                f"next at {t.time.strftime('%I:%M %p')}"
            )

st.divider()

# ── Step 5: Mark Task Complete 
st.subheader("Mark Task Complete")

all_tasks = owner.get_all_tasks()
pending_tasks = [t for t in all_tasks if not t.completed]

if not pending_tasks:
    st.info("No pending tasks to complete.")
else:
    task_options = {
        f"{t.pet_name} — {t.description} ({t.time.strftime('%I:%M %p')})": t.id
        for t in pending_tasks
    }
    selected_label = st.selectbox("Select task to complete", options=list(task_options.keys()))

    if st.button("Mark as Complete"):
        task_id = task_options[selected_label]
        scheduler.mark_task_complete(task_id)
        st.success(f"Marked complete: {selected_label}")

        # Check if recurrence was created
        task_obj = next((t for t in all_tasks if t.id == task_id), None)
        if task_obj and task_obj.frequency in {"daily", "weekly"}:
            delta_label = "tomorrow" if task_obj.frequency == "daily" else "next week"
            st.info(f"Next recurrence auto-scheduled for {delta_label}.")