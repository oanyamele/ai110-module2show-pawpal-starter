import streamlit as st

from datetime import datetime, date
from pathlib import Path
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

DATA_FILE = Path(__file__).resolve().parent / "data.json"

if "owner" not in st.session_state:
    try:
        saved_owner = Owner.load_from_json(DATA_FILE)
    except (OSError, ValueError) as error:
        st.error(f"Could not load saved PawPal+ data: {error}")
        st.stop()

    st.session_state.owner = saved_owner or Owner(owner_id=1, name="Jordan")

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = max(
        (pet.pet_id for pet in st.session_state.owner.list_pets()),
        default=0,
    ) + 1

owner = st.session_state.owner

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
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

st.subheader("Your Pet Profile")

owner_name = st.text_input(
    "Owner name",
    value=owner.name,
    key="owner_name_input",
)

if owner.name != owner_name:
    owner.name = owner_name
    owner.save_to_json(DATA_FILE)

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    if pet_name.strip():
        new_pet = Pet(
            pet_id=st.session_state.next_pet_id,
            name=pet_name.strip(),
            species=species,
        )

        owner.add_pet(new_pet)
        owner.save_to_json(DATA_FILE)
        st.session_state.next_pet_id += 1

        st.success(f"{new_pet.name} was added!")
    else:
        st.error("Please enter a pet name.")

st.subheader("Your Pets")

if owner.list_pets():
    for pet in owner.list_pets():
        st.write(f"🐾 **{pet.name}** — {pet.species}")
else:
    st.info("No pets added yet.")

st.divider()

pets = owner.list_pets()

if not pets:
    st.info("Add a pet before scheduling tasks.")

else:
    pet_options = {
        f"{pet.name} ({pet.species})": pet
        for pet in pets
    }

    selected_pet_name = st.selectbox(
        "Choose a pet",
        list(pet_options.keys()),
    )
    selected_pet = pet_options[selected_pet_name]

    task_title = st.text_input("Task title", value="Morning walk")
    task_date = st.date_input("Task date", value=date.today())
    task_time = st.time_input("Task time")

    frequency = st.selectbox(
        "Frequency",
        ["once", "daily", "weekly"],
    )

    if st.button("Add task"):
        if task_title.strip():
            due_time = datetime.combine(task_date, task_time)

            new_task = Task(
                description=task_title.strip(),
                due_time=due_time,
                frequency=frequency,
            )

            selected_pet.add_task(new_task)
            owner.save_to_json(DATA_FILE)

            st.success(
                f"Added '{new_task.description}' for "
                f"{selected_pet.name}!"
            )
        else:
            st.error("Please enter a task title.")

    st.subheader("Current Tasks")

    for pet in owner.list_pets():
        st.write(f"**{pet.name}'s tasks**")

        pet_tasks = pet.list_tasks()

        if pet_tasks:
            for task_index, task in enumerate(pet_tasks):
                status = "Completed" if task.is_complete else "Pending"

                st.write(
                    f"- {task.description} — "
                    f"{task.due_time.strftime('%b %d, %Y %I:%M %p')} "
                    f"({task.frequency}, {status})"
                )

                if not task.is_complete and st.button(
                    f"Mark '{task.description}' complete",
                    key=f"complete-{pet.pet_id}-{task_index}",
                ):
                    Scheduler(owner).mark_task_complete(pet, task)
                    owner.save_to_json(DATA_FILE)
                    st.rerun()
        else:
            st.caption("No tasks scheduled for this pet.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate an ordered schedule from your pets' care tasks.")

schedule_date = st.date_input(
    "Choose schedule date",
    value=date.today(),
    key="schedule_date",
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)

    all_tasks = scheduler.sort_tasks_by_due_time()

    scheduled_tasks = [
        task
        for task in all_tasks
        if task.due_time.date() == schedule_date
    ]

    if not scheduled_tasks:
        st.info(
            f"No tasks scheduled for {schedule_date.strftime('%B %d, %Y')}."
        )
    else:
        st.markdown(
            f"### Schedule for {schedule_date.strftime('%B %d, %Y')}"
        )

        for task in scheduled_tasks:
            status = "Completed" if task.is_complete else "Pending"

            st.write(
                f"**{task.due_time.strftime('%I:%M %p')}** — "
                f"{task.description} ({status})"
            )

        incomplete_tasks = [
            task for task in scheduled_tasks
            if not task.is_complete
        ]

        st.caption(
            f"{len(incomplete_tasks)} incomplete task(s) for this date."
        )

        conflicts = scheduler.find_conflicts()

        st.subheader("Schedule Conflict Check")

        if conflicts:
            for conflict in conflicts:
                st.warning(f"⚠️ {conflict}")
        else:
            st.success("No scheduling conflicts detected!")
