# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked my AI coding assistant to implement a next available time slot algorithm for PawPal+.

**What did the agent do?**

- Added an optional duration: timedelta | None field at the end of the dataclass. Existing constructors still work without changes, but the new slot finder raises a clear ValueError if an unfinished task has no duration; it does not guess one.
- Changed these files - pawpal_system.py, main.py, test_pawpal.py
- pawpal_system.py: Added Scheduler.find_next_available_slot(requested_start, duration). It checks unfinished tasks across all pets, sorts them by start time, and moves the proposed start to the end of each overlapping task until it finds an open interval.
- main.py: Assigned explicit durations to the demo tasks and printed a readable next-slot example. It suggests 2026-10-14 08:30 for a 30-minute task requested at 07:45.
- test_pawpal.py: Added tests for an open slot, a conflict, a conflict with another pet, and missing existing durations. Also verified durations survive JSON round-tripping and recurring-task creation.


**What did you have to verify or fix manually?**

The agent kept existing features and tests compatible so I ran python -m pytest and python main.py to verify the updates and didn't have to do manual fixes. just verification.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
