# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design includes four main classes, Owner, Pet, Task, and Scheduler. Owner is meant to store the owner's information and their pets and a way to add pets. Pet is meant to store information about each pet and a collection of care tasks. Task is meant to store pet care activity, so it includes decriptions, due dates, and completion status and a way to mark a task as complete. Scheduler is meant to manage tasks across multiple pets belonging to an owner and sort tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I updated the list_pets() and list_tasks() methods to return copies of internal lists instead of the original lists to help prevent accidentally modifying the collections directly. I kept the four-class structure as it is.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers task due dates and times, completion status, pet ownership, and recurrence frequency. It sorts tasks chronologically, filters tasks by pet or completion status, and creates the next occurrence of daily and weekly tasks when they are completed.

I decided having a clear, reliable schedule and preventing duplicate recurring tasks was most important. The current implementation doesn't consider task duration, priority scores, or owner preferences when ordering tasks yet, but these would be useful improvements for a later version.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My find_conflicts() method groups tasks by their exact due date and time, allowing it to detect scheduling conflicts in O(n) time. I considered using collections.defaultdict(list) instead of setdefault() to make the grouping code shorter. However, the existing implementation is already efficient and easy to understand, so I decided to keep it. The scheduler also only detects tasks with identical start times, not tasks that overlap because of their durations.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used my AI coding assistant throughout the project to brainstorm class designs, generate Python class skeletons, implement scheduling algorithms, connect the backend to Streamlit, and develop automated tests. The most helpful prompts involve me asking specific questions about individual methods to understand how the classes interacted and how to handle edge cases. Reviewing the suggestions helped me decide whether the proposed solutions were needed or not.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One AI suggestion I considered was replacing setdefault() with collections.defaultdict(list) in the conflict-detection algorithm. I decided to keep the original implementation because it was already efficient and readable, and the suggested change didn't add a notable benefit from including it. I also verified suggestions by running python -m pytest, running main.py, and testing the Streamlit interface to help me check that the code worked while updating it.



---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested for task completion, adding tasks to pets, chronological sorting, stable ordering for equal due times, filtering by pet and completion status, daily and weekly recurrence, prevention of duplicate recurring tasks, and conflict detection. I also tested invalid pet and task ownership relationships. These tests were important because they verified both the returned results and the state changes made by the scheduler. They help catch errors when new features are added and make it easier to check that existing functionality continues to work.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am pretty confident in the scheduler because the automated test suite passed all 14 tests during my verification run. However, I think it's also realistic to admit that passing tests doesn't guarantee that every potential situation is handled correctly.

If I had more time, I would test additional edge cases, including an owner with no pets, a pet with no tasks, and tasks whose durations overlap even though their start times differ. I would also expand the scheduler to support priority-based scheduling and more flexible recurrence patterns.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with connecting the backend classes to a working Streamlit interface. The automated tests also gave me a way to verify the implementation as it developed.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would improve the scheduling algorithm by considering task durations, priorities, and owner availability. This would allow the scheduler to detect overlapping activities and make more useful scheduling decisions. I would also add more tests to make it easier to manage existing tasks and mark them complete.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

My main takeaway is that building a system with AI requires more as you need to make design decisions, review suggestions, understand the relationships between classes, and verify behavior through tests. Acting as the driver meant deciding what the system should do and ensuring that the final implementation matched those goals, while using AI as a tool or kind of like a pit crew to support my decisions.
