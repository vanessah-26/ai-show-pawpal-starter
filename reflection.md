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
