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

    scheduler = st.session_state.scheduler
    active = scheduler.active_tasks if scheduler else []
    if active:
        # Sort by scheduling priority so the table matches what generate_daily_plan will do:
        # fixed-time tasks first, then highest priority, then shortest duration.
        sorted_active = scheduler.sort_tasks(active)
        st.write("**Current tasks** (sorted by scheduling priority):")
        st.table([
            {
                "Task": t.name,
                "Category": t.category,
                "Duration (min)": t.duration_min,
                "Priority": "⭐" * t.priority,
                "Fixed time": t.fixed_start_time or "—",
                "Earliest": t.earliest_start or "—",
                "Latest end": t.latest_end or "—",
            }
            for t in sorted_active
        ])

        # Show conflict warnings immediately so the owner can fix issues before generating.
        warnings = scheduler.conflict_warnings()
        if warnings:
            st.markdown("**⚠️ Scheduling issues detected — fix these before generating:**")
            for w in warnings:
                st.warning(w)
        else:
            st.success("No scheduling conflicts — ready to generate.")
    else:
        st.info("No tasks added yet.")

st.divider()

# ── Section 4: Generate Schedule ─────────────────────────────────────────────
st.subheader("4. Generate Schedule")

if not st.session_state.scheduler or not st.session_state.scheduler.tasks:
    st.warning("Add an owner and at least one task before generating a schedule.")
else:
    scheduler = st.session_state.scheduler

    # Block generation if there are conflicts — show them as actionable warnings.
    pre_warnings = scheduler.conflict_warnings()
    if pre_warnings:
        st.markdown("**Resolve these conflicts before generating:**")
        for w in pre_warnings:
            st.warning(w)

    generate_disabled = bool(pre_warnings)
    if st.button("Generate schedule", disabled=generate_disabled):
        try:
            st.session_state.plan = scheduler.generate_daily_plan()
            total_active = len(scheduler.active_tasks)
            scheduled = len(st.session_state.plan)
            if scheduled == total_active:
                st.success(f"All {scheduled} tasks scheduled.")
            else:
                skipped = total_active - scheduled
                st.warning(
                    f"{scheduled} of {total_active} tasks scheduled — "
                    f"{skipped} task(s) were skipped because they couldn't fit "
                    f"within your availability or time window constraints."
                )
        except ValueError as e:
            st.error(str(e))

    if st.session_state.plan:
        completed_tasks = scheduler.tasks_by_status(completed=True)
        completed_ids = {t.task_id for t in completed_tasks}

        st.markdown("**Today's Schedule:**")

        for item in st.session_state.plan:
            is_done = item.task.task_id in completed_ids
            col1, col2 = st.columns([5, 1])
            with col1:
                # Colour-code the time slot by priority: high (>=4) gets a warm tint label.
                priority_badge = " 🔴" if item.task.priority >= 4 else (" 🟡" if item.task.priority == 3 else " 🔵")
                if is_done:
                    st.markdown(
                        f"<div style='opacity:0.4;text-decoration:line-through;font-size:15px'>"
                        f"<code>{item.start} – {item.end}</code> &nbsp; {item.task.name}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"`{item.start} – {item.end}` &nbsp; **{item.task.name}**{priority_badge} "
                        f"<span style='color:gray;font-size:12px'>({item.task.category}, {item.duration()} min)</span>",
                        unsafe_allow_html=True,
                    )
            with col2:
                if not is_done:
                    if st.button("✓ Done", key=f"done_{item.task.task_id}"):
                        scheduler.tasks[item.task.task_id].mark_complete()
                        st.rerun()

        st.markdown("")
        with st.expander("Why was each task placed here?"):
            st.text(scheduler.explain_plan(st.session_state.plan))
