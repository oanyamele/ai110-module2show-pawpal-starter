from datetime import datetime

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
