# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The classes I chose include:
- User, Pet, Task, Scheduler

The purpose of each class:
- User: Stores the pet owner’s info + availability constraints.
- Pet: Stores pet details that can affect tasks (meds, age, energy level, etc)
- Task: Represents one care activity with scheduling requirements.
- Scheduler: Core logic: takes user availability + tasks and returns a daily plan (and can generate explanations + validate schedules for tests).

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

1. I changed the type of available start time and fixed start time from string to "HH:MM" strings format, and added a helper function to validate that. This is for better datetime parsing 

2. Changed Task from list to dict type for more efficient lookup time. The initial suggestion from AI was list, so if scanning every task_id throuhg the whole list, it would be O(n) every single call. Use dict and look up task_id as a key would make it to be O(1)
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
1. Time availability: the owner's available_time_start and available_time_end bound every task; nothing can be scheduled outside that window
2. Fixed start time: tasks with fixed_start_time are anchored to an exact slot and placed first before anything else
3. Time windows: earliest_start and latest_end give flexible tasks a range they must fit within
4. Priority: among flexible tasks, higher priority tasks are placed before lower ones when time is limited
5. Duration: tasks that don't fit remaining availability are skipped rather than truncated
6. Completion status: completed tasks are excluded from scheduling so the plan only shows what's left to do
7. Recurring frequency: daily, weekly, and 2x/day tasks affect how many slots are generated and when the next occurrence is created

- How did you decide which constraints mattered most?
1. Fixed time first: some tasks have no flexibility (medication at a specific hour); getting those wrong breaks real-world care, so they anchor the schedule before anything else is placed
2. Priority over duration: a 5-minute high-priority task (meds) should never be bumped for a 45-minute low-priority task (grooming); priority determines ordering, duration determines fit
3. Availability as a hard boundary: unlike priority which ranks preferences, the owner's availability is a hard limit; violating it makes the schedule useless, so reject_if_impossible enforces it before any planning starts
4. Completion status added later: this constraint only matters once the app is used across a real day rather than generating a one-shot plan, so it was the right call to add it after the core scheduler worked


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The genereate daily plan triggers active task multiple times. For a small task list, it's not a big issue, but for longer list it can be inefficient. There were two options to go about this: 
First, cache it: invalidate on add_task, remove_task, or mark_task_complete
Or second, maintain a secodn dict: this keeps the active dict insync 
- Why is that tradeoff reasonable for this scenario?
Caching is fine for now, and assuming the daily tasks is around 10 tasks, that wouldn't be an issue for this version 1. There are other critical things which impact the quality of the app so I'd prioritize fixing them first. 

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
I'm most satisfied with the features implementation and improvements. I gave direction on which features to focus on, how I wanted it to be implemented and scoped out the structure, then AI implemented based on that foundation. It was helpful in flagging bottlenecks and improved those areas. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would love to have some existing sample feedback or example constraints from users' perspective, that would make the problem more interesting and feel more realistic. 
- I would also add Co-care-giver profile so another person outside of the main user can access care info and help the user to take care of the pet when the main owner is not around. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

It's important to have a solid understanding of the problem, structure the approach clearly, define the main scope before expanding the features. This way, it is easier and faster to implement and solve the main problem, before expanding to other nice-to-have areas.
