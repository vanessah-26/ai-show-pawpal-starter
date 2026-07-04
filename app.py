import streamlit as st
from pawpal_system import User, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── Session state init ────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None        # User object

if "pets" not in st.session_state:
    st.session_state.pets = []           # list[Pet]

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None    # Scheduler object

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 0    # used to generate unique task IDs

if "plan" not in st.session_state:
    st.session_state.plan = []           # last generated list[ScheduledItem]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption("A pet care planning assistant for busy owners.")
st.divider()

# ── Section 1: Owner Setup ────────────────────────────────────────────────────
st.subheader("1. Owner Setup")

with st.form("owner_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        owner_name = st.text_input("Owner name", value="Jordan")
    with col2:
        avail_start = st.text_input("Available from", value="08:00")
    with col3:
        avail_end = st.text_input("Available until", value="18:00")
    submitted = st.form_submit_button("Save owner")

if submitted:
    try:
        owner = User(
            name=owner_name,
            available_time_start=avail_start,
            available_time_end=avail_end,
        )
        st.session_state.owner = owner
        st.session_state.scheduler = Scheduler(user=owner)
        # re-add any pets that already existed
        for pet in st.session_state.pets:
            st.session_state.scheduler.add_pet(pet)
        st.success(f"Owner '{owner_name}' saved — {owner.get_available_minutes()} min available.")
    except ValueError as e:
        st.error(str(e))

if st.session_state.owner:
    o = st.session_state.owner
    st.info(f"Current owner: **{o.name}** · {o.available_time_start} – {o.available_time_end}")

st.divider()

# ── Section 2: Add a Pet ──────────────────────────────────────────────────────
st.subheader("2. Add a Pet")

if not st.session_state.owner:
    st.warning("Set up an owner first.")
else:
    with st.form("pet_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            pet_name = st.text_input("Pet name", value="Mochi")
        with col2:
            species = st.selectbox("Species", ["dog", "cat", "other"])
        with col3:
            breed = st.text_input("Breed (optional)", value="")
        submitted = st.form_submit_button("Add pet")

    if submitted:
        pet_id = f"pet_{len(st.session_state.pets)}"
        pet = Pet(
            name=pet_name,
            species=species,
            pet_id=pet_id,
            breed=breed or None,
        )
        st.session_state.pets.append(pet)
        st.session_state.scheduler.add_pet(pet)
        st.success(f"Added {pet.summary()}")

    if st.session_state.pets:
        st.write("**Pets:**", ", ".join(p.summary() for p in st.session_state.pets))
    else:
        st.info("No pets added yet.")

st.divider()

# ── Section 3: Add a Task ─────────────────────────────────────────────────────
st.subheader("3. Add a Task")

if not st.session_state.owner:
    st.warning("Set up an owner first.")
else:
    pet_options = {p.name: p.pet_id for p in st.session_state.pets} if st.session_state.pets else {}

    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            task_name = st.text_input("Task name", value="Morning walk")
            category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"])
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.slider("Priority (1 = low, 5 = high)", 1, 5, 3)
            fixed_start = st.text_input("Fixed start time (HH:MM, optional)", value="")
            if pet_options:
                selected_pet = st.selectbox("Assign to pet", list(pet_options.keys()))
            else:
                selected_pet = None
                st.caption("No pets added yet — task won't be pet-specific.")
        submitted = st.form_submit_button("Add task")

    if submitted:
        try:
            st.session_state.task_counter += 1
            task = Task(
                task_id=f"task_{st.session_state.task_counter}",
                name=task_name,
                category=category,
                duration_min=int(duration),
                priority=priority,
                fixed_start_time=fixed_start or None,
                pet_id=pet_options.get(selected_pet) if selected_pet else None,
            )
            st.session_state.scheduler.add_task(task)
            st.success(f"Added task: '{task_name}' ({duration} min, priority {priority})")
        except ValueError as e:
            st.error(str(e))

    active = st.session_state.scheduler.active_tasks if st.session_state.scheduler else []
    if active:
        st.write("**Current tasks:**")
        st.table([
            {
                "Task": t.name,
                "Category": t.category,
                "Duration (min)": t.duration_min,
                "Priority": t.priority,
                "Fixed time": t.fixed_start_time or "—",
            }
            for t in active
        ])
    else:
        st.info("No tasks added yet.")

st.divider()

# ── Section 4: Generate Schedule ─────────────────────────────────────────────
st.subheader("4. Generate Schedule")

if not st.session_state.scheduler or not st.session_state.scheduler.tasks:
    st.warning("Add an owner and at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        try:
            st.session_state.plan = st.session_state.scheduler.generate_daily_plan()
            st.success(f"Scheduled {len(st.session_state.plan)} tasks.")
        except ValueError as e:
            st.error(str(e))

    if st.session_state.plan:
        scheduler = st.session_state.scheduler
        completed_tasks = scheduler.tasks_by_status(completed=True)
        planned_ids = {item.task.task_id for item in st.session_state.plan}

        st.markdown("**Today's Schedule:**")

        # pending tasks from the plan
        for item in st.session_state.plan:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"`{item.start} – {item.end}` &nbsp; **{item.task.name}** "
                    f"<span style='color:gray;font-size:12px'>({item.task.category}, {item.duration()} min)</span>",
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("✓ Done", key=f"done_{item.task.task_id}"):
                    scheduler.tasks[item.task.task_id].mark_complete()
                    st.rerun()

        # completed tasks shown faded below
        if completed_tasks:
            st.markdown("---")
            for task in completed_tasks:
                st.markdown(
                    f"<div style='opacity:0.38;text-decoration:line-through;font-size:14px'>"
                    f"✓ &nbsp; <code>completed</code> &nbsp; {task.name}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("")
        st.markdown("**Explanation:**")
        st.text(scheduler.explain_plan(st.session_state.plan))
