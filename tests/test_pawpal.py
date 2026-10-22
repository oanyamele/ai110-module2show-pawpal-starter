from datetime import datetime, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_sets_task_as_complete() -> None:
	task = Task("Give medication", datetime(2026, 10, 14, 8, 0))

	assert task.is_complete is False

	task.mark_complete()

	assert task.is_complete is True


def test_adding_task_increases_pet_task_count_by_one() -> None:
	pet = Pet(1, "Buddy", "Dog")
	task = Task("Morning walk", datetime(2026, 10, 14, 7, 30))
	initial_count = len(pet.list_tasks())

	pet.add_task(task)

	assert len(pet.list_tasks()) == initial_count + 1
	assert pet.list_tasks() == [task]


def test_scheduler_sorts_tasks_across_multiple_pets_by_due_time() -> None:
	owner = Owner(1, "Alex")
	dog = Pet(1, "Buddy", "Dog")
	cat = Pet(2, "Luna", "Cat")
	late_task = Task("Evening walk", datetime(2026, 10, 14, 18, 0))
	early_task = Task("Breakfast", datetime(2026, 10, 14, 7, 0))
	middle_task = Task("Medication", datetime(2026, 10, 14, 12, 0))

	dog.add_task(late_task)
	dog.add_task(middle_task)
	cat.add_task(early_task)
	owner.add_pet(dog)
	owner.add_pet(cat)

	sorted_tasks = Scheduler(owner).sort_tasks_by_due_time()

	assert sorted_tasks == [early_task, middle_task, late_task]


def test_scheduler_sort_is_stable_for_equal_due_times() -> None:
	owner = Owner(1, "Alex")
	dog = Pet(1, "Buddy", "Dog")
	cat = Pet(2, "Luna", "Cat")
	first_task = Task("First added", datetime(2026, 10, 14, 8, 0))
	second_task = Task("Second added", datetime(2026, 10, 14, 8, 0))
	later_task = Task("Later", datetime(2026, 10, 14, 9, 0))

	dog.add_task(first_task)
	dog.add_task(later_task)
	cat.add_task(second_task)
	owner.add_pet(dog)
	owner.add_pet(cat)

	assert Scheduler(owner).sort_tasks_by_due_time() == [
		first_task,
		second_task,
		later_task,
	]


def test_filter_tasks_matches_pet_and_optional_completion_status() -> None:
	owner = Owner(1, "Alex")
	dog = Pet(1, "Buddy", "Dog")
	cat = Pet(2, "Luna", "Cat")
	completed_task = Task("Medication", datetime(2026, 10, 14, 8, 0), is_complete=True)
	dog_task = Task("Walk", datetime(2026, 10, 14, 9, 0))
	cat_task = Task("Grooming", datetime(2026, 10, 14, 10, 0))
	dog.add_task(completed_task)
	dog.add_task(dog_task)
	cat.add_task(cat_task)
	owner.add_pet(dog)
	owner.add_pet(cat)
	scheduler = Scheduler(owner)

	assert scheduler.filter_tasks("Buddy") == [completed_task, dog_task]
	assert scheduler.filter_tasks("Buddy", is_complete=True) == [completed_task]
	assert scheduler.filter_tasks("Buddy", is_complete=False) == [dog_task]
	assert scheduler.filter_tasks("Luna") == [cat_task]
	assert scheduler.filter_tasks("Unknown") == []


@pytest.mark.parametrize(
	("frequency", "days"),
	[("daily", 1), ("weekly", 7)],
)
def test_mark_task_complete_creates_next_recurring_occurrence(
	frequency: str,
	days: int,
) -> None:
	owner = Owner(1, "Alex")
	pet = Pet(1, "Buddy", "Dog")
	task = Task("Medication", datetime(2026, 10, 14, 8, 30), frequency=frequency)
	pet.add_task(task)
	owner.add_pet(pet)

	next_task = Scheduler(owner).mark_task_complete(pet, task)

	assert task.is_complete is True
	assert next_task is not None
	assert next_task.description == task.description
	assert next_task.frequency == frequency
	assert next_task.due_time == datetime(2026, 10, 14, 8, 30) + timedelta(days=days)
	assert next_task.is_complete is False
	assert pet.list_tasks() == [task, next_task]


def test_mark_task_complete_does_not_repeat_one_time_or_unsupported_tasks() -> None:
	owner = Owner(1, "Alex")
	pet = Pet(1, "Buddy", "Dog")
	once_task = Task("Vet visit", datetime(2026, 10, 14, 8, 0))
	unsupported_task = Task(
		"Extra care", datetime(2026, 10, 14, 9, 0), frequency="twice daily"
	)
	pet.add_task(once_task)
	pet.add_task(unsupported_task)
	owner.add_pet(pet)
	scheduler = Scheduler(owner)

	assert scheduler.mark_task_complete(pet, once_task) is None
	assert scheduler.mark_task_complete(pet, unsupported_task) is None
	assert once_task.is_complete is True
	assert unsupported_task.is_complete is True
	assert pet.list_tasks() == [once_task, unsupported_task]


def test_marking_already_completed_task_does_not_create_duplicate() -> None:
	owner = Owner(1, "Alex")
	pet = Pet(1, "Buddy", "Dog")
	task = Task("Walk", datetime(2026, 10, 14, 8, 0), frequency="daily")
	pet.add_task(task)
	owner.add_pet(pet)
	scheduler = Scheduler(owner)

	first_occurrence = scheduler.mark_task_complete(pet, task)
	second_occurrence = scheduler.mark_task_complete(pet, task)

	assert first_occurrence is not None
	assert second_occurrence is None
	assert pet.list_tasks() == [task, first_occurrence]


def test_mark_task_complete_rejects_task_not_owned_by_specified_pet() -> None:
	owner = Owner(1, "Alex")
	dog = Pet(1, "Buddy", "Dog")
	cat = Pet(2, "Luna", "Cat")
	task = Task("Walk", datetime(2026, 10, 14, 8, 0), frequency="daily")
	dog.add_task(task)
	owner.add_pet(dog)
	owner.add_pet(cat)

	with pytest.raises(ValueError, match="must belong"):
		Scheduler(owner).mark_task_complete(cat, task)

	assert task.is_complete is False
	assert cat.list_tasks() == []


def test_find_conflicts_returns_readable_warnings_for_exact_due_times() -> None:
	owner = Owner(1, "Alex")
	dog = Pet(1, "Buddy", "Dog")
	cat = Pet(2, "Luna", "Cat")
	dog_task = Task("Morning walk", datetime(2026, 10, 14, 8, 0))
	cat_task = Task("Breakfast", datetime(2026, 10, 14, 8, 0))
	dog.add_task(dog_task)
	cat.add_task(cat_task)
	owner.add_pet(dog)
	owner.add_pet(cat)

	warnings = Scheduler(owner).find_conflicts()

	assert len(warnings) == 1
	assert "2026-10-14 08:00:00" in warnings[0]
	assert '"Morning walk" for Buddy' in warnings[0]
	assert '"Breakfast" for Luna' in warnings[0]


def test_mark_task_complete_rejects_pet_not_owned_by_scheduler_owner() -> None:
	owner = Owner(1, "Alex")
	foreign_pet = Pet(2, "Luna", "Cat")
	task = Task("Grooming", datetime(2026, 10, 14, 8, 0), frequency="weekly")
	foreign_pet.add_task(task)

	with pytest.raises(ValueError, match="must belong"):
		Scheduler(owner).mark_task_complete(foreign_pet, task)

	assert task.is_complete is False
