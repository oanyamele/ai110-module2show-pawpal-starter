# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# Initial Termimal Output:
Today's Schedule (Wednesday, October 14, 2026)
Owner: Alex Morgan | Tasks: 3
TIME   PET      TASK                  FREQUENCY      STATUS
-----  -------  --------------------  -------------  ----------
07:30  Buddy    Morning walk          daily          Incomplete
08:00  Buddy    Breakfast             twice daily    Complete
09:00  Luna     Brush coat            weekly         Incomplete

Incomplete Tasks (2)
07:30  Buddy: Morning walk (daily)
09:00  Luna: Brush coat (weekly)
```

```
# Challenge 3 Termimal Output:
python main.py
Today's Schedule (Wednesday, October 14, 2026)
Owner: Alex Morgan | Tasks: 4
DUE TIME             PET      TASK                  FREQUENCY      STATUS
-------------------  -------  --------------------  -------------  ----------
2026-10-14 07:30  Buddy    Morning walk          daily          Complete
2026-10-14 07:30  Luna     Brush coat            weekly         Incomplete
2026-10-14 08:00  Buddy    Breakfast             twice daily    Incomplete
2026-10-15 07:30  Buddy    Morning walk          daily          Incomplete

Next occurrence: Morning walk for Buddy at 2026-10-15 07:30

Incomplete Tasks (3)
08:00  Buddy: Breakfast (twice daily)
07:30  Buddy: Morning walk (daily)
07:30  Luna: Brush coat (weekly)

Incomplete Buddy Tasks (2)
2026-10-14 08:00  Breakfast
2026-10-15 07:30  Morning walk

Schedule Conflicts
Schedule conflict at 2026-10-14 07:30:00: "Morning walk" for Buddy, "Brush coat" for Luna.

Priority-Based Schedule
PRIORITY  DUE TIME             PET      TASK
--------  -------------------  -------  --------------------
HIGH      2026-10-14 07:30  Buddy    Morning walk
HIGH      2026-10-15 07:30  Buddy    Morning walk
MEDIUM    2026-10-14 08:00  Buddy    Breakfast
LOW       2026-10-14 07:30  Luna     Brush coat
```

## 📐 Smarter Scheduling

The `Scheduler` collects tasks across an owner's pets and provides these scheduling algorithms:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `sort_tasks_by_due_time()` | Returns tasks in chronological due-time order. Python's stable sort preserves input order for tasks with equal due times. |
| Filtering | `filter_tasks(pet_name, is_complete=None)` | Returns tasks for the named pet. Pass `True` or `False` to filter by completion status, or omit it to include both statuses. `filter_incomplete_tasks()` returns incomplete tasks across all pets. |
| Recurring tasks | `mark_task_complete(pet, task)` | Verifies that the task belongs to the specified pet, marks it complete, then adds one next occurrence for `daily` (+1 day) or `weekly` (+7 days) tasks. One-time and unsupported frequencies do not recur; completing an already-completed task again does not add a duplicate. |
| Conflict detection | `find_conflicts()` | Returns readable warning strings for tasks that share the exact same date and time, including their descriptions and pet names. Conflicts are reported rather than raised as errors. |

| Priority-based scheduling | `sort_tasks_by_priority()` | Sorts tasks by priority (high, medium, low), then by due time. Includes tasks across all pets. |

## Data Persistence

PawPal+ stores the owner, pets, and their tasks in `data.json` in the project directory. The Streamlit app loads this file when it starts; if it is not present, the app starts with a new owner. The path is resolved relative to `app.py`, so it is consistent regardless of the current working directory.

`Owner.save_to_json(file_path)` writes the owner ID and name, pet details, and every task field (`description`, `due_time`, `is_complete`, `frequency`, and `priority`). Datetimes are stored as ISO 8601 strings. `Owner.load_from_json(file_path)` restores datetimes and the complete object hierarchy; it returns `None` for a missing file and raises a clear `ValueError` for malformed JSON or invalid data.

The app saves after owner-name changes, adding pets or tasks, and completing tasks. Recurring occurrences created by task completion are included in the saved owner data.

Automated tests in tests/test_pawpal.py verify that multiple pets and their task details survive a save-and-load round trip. Additional tests cover missing files, malformed JSON, and invalid task dates, and test are ran with python -m pytest

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:
python -m pytest
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/ogechi/Desktop/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 14 items                                                             

tests/test_pawpal.py ..............                                      [100%]

============================== 14 passed in 0.05s ==============================

```
# Confidence Level: 4/5 (The current tests cover the bases, however if there are more features then more tests might be necessary)



## 📸 Demo Walkthrough

PawPal+ is a Streamlit application that helps a pet owner organize pet care activities and review a schedule.

Using the Streamlit App
Enter owner information: Update the owner's name in the Pet Profile section.
Add pets: Enter a pet's name, select its species, and click Add Pet. Added pets remain available during the Streamlit session.
Schedule tasks: Select a pet, enter a task description, choose its date and time, select a frequency (once, daily, or weekly), and click Add task.
View the schedule: Select a date and click Generate schedule. Tasks scheduled for that date are displayed in chronological order, with their completion status.
Check for conflicts: The scheduler checks tasks across the owner's pets and displays warnings when two or more tasks have exactly the same due date and time. If no conflicts are detected, the app displays a success message.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

