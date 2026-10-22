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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My find_conflicts() method groups tasks by their exact due date and time, allowing it to detect scheduling conflicts in O(n) time. I considered using collections.defaultdict(list) instead of setdefault() to make the grouping code shorter. However, the existing implementation is already efficient and easy to understand, so I decided to keep it. The scheduler also only detects tasks with identical start times, not tasks that overlap because of their durations.

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
