import streamlit as st
from datetime import datetime, time

from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    ActivityType, TaskKind, TaskPriority, TaskStatus, TaskFrequency,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state bootstrap
# Streamlit re-runs this file top-to-bottom on every interaction.
# Storing objects in st.session_state keeps them alive across re-runs.
# ---------------------------------------------------------------------------
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

if "owner" not in st.session_state:
    st.session_state.owner = None

if "_ids" not in st.session_state:
    st.session_state._ids = {"pet": 1, "task": 1}

scheduler: Scheduler = st.session_state.scheduler

# ---------------------------------------------------------------------------
# Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner")
owner_name = st.text_input("Your name", value=st.session_state.owner.name if st.session_state.owner else "")

if st.button("Set Owner"):
    if owner_name.strip():
        if st.session_state.owner is None:
            owner = Owner(id=1, name=owner_name.strip())
            st.session_state.owner = owner
            scheduler.add_owner(owner)
        else:
            # Update name in place without resetting pets/tasks
            st.session_state.owner.name = owner_name.strip()
        st.success(f"Welcome, {st.session_state.owner.name}!")
    else:
        st.warning("Please enter a name before continuing.")

owner: Owner | None = st.session_state.owner

# Everything below requires an owner to be set first
if not owner:
    st.info("Set your name above to get started.")
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------
st.subheader("My Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name  = st.text_input("Pet name")
        breed     = st.text_input("Breed")
    with col2:
        species   = st.selectbox("Species", ["dog", "cat", "other"])
        age       = st.number_input("Age", min_value=0, max_value=30, value=1)
    add_pet = st.form_submit_button("Add Pet")

if add_pet:
    if pet_name.strip():
        pet_id  = st.session_state._ids["pet"]
        new_pet = Pet(id=pet_id, name=pet_name.strip(), breed=breed, age=age, species=species)
        scheduler.add_pet(new_pet, owner_id=owner.id)
        st.session_state._ids["pet"] += 1
        st.success(f"{pet_name} added!")
    else:
        st.warning("Pet name cannot be empty.")

if owner.pet_ids:
    pets = [scheduler.pets[pid] for pid in owner.pet_ids]
    st.table([
        {"Name": p.name, "Species": p.species, "Breed": p.breed, "Age": p.age}
        for p in pets
    ])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Schedule a Task  (only shown once at least one pet exists)
# ---------------------------------------------------------------------------
if not owner.pet_ids:
    st.stop()

st.subheader("Schedule a Task")

pets        = [scheduler.pets[pid] for pid in owner.pet_ids]
pet_options = {p.name: p.id for p in pets}

with st.form("add_task_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        selected_pet    = st.selectbox("Pet", list(pet_options.keys()))
        activity        = st.selectbox("Activity",  [a.value for a in ActivityType])
        description     = st.text_input("Description")
        task_kind_val   = st.selectbox("Task type", [k.value for k in TaskKind])
    with col2:
        priority_val    = st.selectbox("Priority",  [p.value for p in TaskPriority], index=1)
        duration        = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
        frequency_val   = st.selectbox("Frequency", [f.value for f in TaskFrequency])
        scheduled_time  = st.time_input("Scheduled time", value=time(9, 0))
    add_task = st.form_submit_button("Add Task")

if add_task:
    scheduled_at     = datetime.combine(datetime.now().date(), scheduled_time)
    owner_id_for_task = None if task_kind_val == TaskKind.EVENT.value else owner.id
    task_id          = st.session_state._ids["task"]

    new_task = Task(
        id               = task_id,
        pet_id           = pet_options[selected_pet],
        task_kind        = TaskKind(task_kind_val),
        activity         = ActivityType(activity),
        priority         = TaskPriority(priority_val),
        duration_minutes = int(duration),
        status           = TaskStatus.PENDING,
        scheduled_at     = scheduled_at,
        description      = description,
        frequency        = TaskFrequency(frequency_val),
        owner_id         = owner_id_for_task,
    )
    conflict_warning = scheduler.add_task(new_task)
    st.session_state._ids["task"] += 1
    if conflict_warning:
        st.warning(conflict_warning)
    else:
        st.success(f"Task scheduled for {selected_pet} at {scheduled_time.strftime('%I:%M %p')}!")

st.divider()

# ---------------------------------------------------------------------------
# Today's Schedule
# ---------------------------------------------------------------------------
st.subheader("Today's Schedule")

col_filter, col_btn = st.columns([3, 1])
with col_filter:
    pet_names    = ["All pets"] + [scheduler.pets[pid].name for pid in owner.pet_ids]
    filter_pet   = st.selectbox("Filter by pet", pet_names, label_visibility="collapsed")
with col_btn:
    show_schedule = st.button("Generate Schedule", use_container_width=True)

if show_schedule:
    schedule = scheduler.get_todays_schedule(owner_id=owner.id)

    if filter_pet != "All pets":
        selected_pet_id = next(pid for pid in owner.pet_ids if scheduler.pets[pid].name == filter_pet)
        schedule = scheduler.filter_tasks(schedule, pet_id=selected_pet_id)

    if not schedule:
        st.info("No tasks scheduled for today. Add some above.")
    else:
        for task in schedule:
            pet        = scheduler.pets[task.pet_id]
            assigned   = f"{owner.name}" if task.owner_id else "Shared Event"
            status_icon = "✅" if task.status == TaskStatus.DONE else "⏳"

            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f"**{status_icon} {task.scheduled_at.strftime('%I:%M %p')} — "
                        f"{pet.name} | {task.activity.value.replace('_', ' ').upper()}**"
                    )
                    st.caption(task.description or "No description.")
                    st.markdown(
                        f"`{task.priority.value}` priority · "
                        f"`{task.duration_minutes} min` · "
                        f"`{task.frequency.value}` · "
                        f"Assigned to: **{assigned}**"
                    )
                with col2:
                    if task.status == TaskStatus.PENDING:
                        if st.button("Mark done", key=f"done_{task.id}"):
                            next_task = scheduler.mark_task_complete(task.id)
                            if next_task:
                                st.toast(f"Next {task.frequency.value} recurrence scheduled for {next_task.scheduled_at.strftime('%b %d')}.")
                            st.rerun()
                    else:
                        st.caption("Completed")
