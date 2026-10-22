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
	task = Task(
		"Medication",
		datetime(2026, 10, 14, 8, 30),
		frequency=frequency,
		duration=timedelta(minutes=20),
	)
	pet.add_task(task)
	owner.add_pet(pet)

	next_task = Scheduler(owner).mark_task_complete(pet, task)

	assert task.is_complete is True
	assert next_task is not None
	assert next_task.description == task.description
	assert next_task.frequency == frequency
	assert next_task.duration == task.duration
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


def test_scheduler_handles_owner_with_no_tasks() -> None:
    owner = Owner(1, "Alex")
    pet = Pet(1, "Buddy", "Dog")
    owner.add_pet(pet)

    scheduler = Scheduler(owner)

    assert scheduler.sort_tasks_by_due_time() == []
    assert scheduler.filter_tasks("Buddy") == []
    assert scheduler.find_conflicts() == []


def test_find_conflicts_returns_no_warnings_for_different_times() -> None:
    owner = Owner(1, "Alex")
    pet = Pet(1, "Buddy", "Dog")

    pet.add_task(Task("Breakfast", datetime(2026, 10, 14, 8, 0)))
    pet.add_task(Task("Walk", datetime(2026, 10, 14, 9, 0)))
    owner.add_pet(pet)

    assert Scheduler(owner).find_conflicts() == []


def test_scheduler_sorts_by_priority_then_due_time() -> None:
    owner = Owner(1, "Alex")
    dog = Pet(1, "Buddy", "Dog")
    cat = Pet(2, "Luna", "Cat")

    low_task = Task(
        "Grooming",
        datetime(2026, 10, 14, 7, 0),
        priority="low",
    )
    high_late = Task(
        "Evening medication",
        datetime(2026, 10, 14, 18, 0),
        priority="high",
    )
    high_early = Task(
        "Morning medication",
        datetime(2026, 10, 14, 8, 0),
        priority="high",
    )
    medium_task = Task(
        "Feeding",
        datetime(2026, 10, 14, 9, 0),
        priority="medium",
    )

    dog.add_task(low_task)
    dog.add_task(high_late)
    cat.add_task(high_early)
    cat.add_task(medium_task)

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)

    assert scheduler.sort_tasks_by_priority() == [
        high_early,
        high_late,
        medium_task,
        low_task,
    ]


def test_owner_json_round_trip_preserves_multiple_pets_and_task_fields(tmp_path) -> None:
	due_time = datetime.fromisoformat("2026-10-14T08:30:45+00:00")
	owner = Owner(7, "Alex")
	dog = Pet(1, "Buddy", "Dog")
	cat = Pet(2, "Luna", "Cat")
	dog.add_task(
		Task(
			"Medication",
			due_time,
			is_complete=True,
			frequency="daily",
			priority="high",
			duration=timedelta(minutes=30),
		)
	)
	cat.add_task(
		Task(
			"Grooming",
			datetime(2026, 10, 15, 9, 15),
			frequency="weekly",
			priority="low",
			duration=timedelta(minutes=45),
		)
	)
	owner.add_pet(dog)
	owner.add_pet(cat)
	file_path = tmp_path / "data.json"

	owner.save_to_json(file_path)
	restored_owner = Owner.load_from_json(file_path)

	assert restored_owner is not None
	assert (restored_owner.owner_id, restored_owner.name) == (7, "Alex")
	restored_pets = restored_owner.list_pets()
	assert [(pet.pet_id, pet.name, pet.species) for pet in restored_pets] == [
		(1, "Buddy", "Dog"),
		(2, "Luna", "Cat"),
	]
	restored_medication = restored_pets[0].list_tasks()[0]
	assert restored_medication.description == "Medication"
	assert restored_medication.due_time == due_time
	assert restored_medication.due_time.tzinfo is not None
	assert restored_medication.is_complete is True
	assert restored_medication.frequency == "daily"
	assert restored_medication.priority == "high"
	assert restored_medication.duration == timedelta(minutes=30)
	restored_grooming = restored_pets[1].list_tasks()[0]
	assert restored_grooming.due_time == datetime(2026, 10, 15, 9, 15)
	assert restored_grooming.is_complete is False
	assert restored_grooming.frequency == "weekly"
	assert restored_grooming.priority == "low"
	assert restored_grooming.duration == timedelta(minutes=45)


def test_owner_load_from_json_returns_none_for_missing_file(tmp_path) -> None:
	missing_file = tmp_path / "missing.json"

	assert Owner.load_from_json(missing_file) is None


def test_owner_load_from_json_rejects_malformed_json(tmp_path) -> None:
	malformed_file = tmp_path / "malformed.json"
	malformed_file.write_text("{not valid json", encoding="utf-8")

	with pytest.raises(ValueError, match="Invalid JSON"):
		Owner.load_from_json(malformed_file)


def test_owner_load_from_json_rejects_invalid_task_datetime(tmp_path) -> None:
	invalid_file = tmp_path / "invalid.json"
	invalid_file.write_text(
		'{"owner_id": 1, "name": "Alex", "pets": [{"pet_id": 1, '
		'"name": "Buddy", "species": "Dog", "tasks": [{"description": '
		'"Walk", "due_time": "not-a-date", "is_complete": false, '
		'"frequency": "daily", "priority": "medium"}]}]}',
		encoding="utf-8",
	)

	with pytest.raises(ValueError, match="invalid due_time"):
		Owner.load_from_json(invalid_file)


def test_find_next_available_slot_returns_requested_time_when_available() -> None:
	owner = Owner(1, "Alex")
	pet = Pet(1, "Buddy", "Dog")
	pet.add_task(
		Task(
			"Morning walk",
			datetime(2026, 10, 14, 8, 0),
			duration=timedelta(minutes=30),
		)
	)
	owner.add_pet(pet)

	available_start = Scheduler(owner).find_next_available_slot(
		datetime(2026, 10, 14, 9, 0),
		timedelta(minutes=30),
	)

	assert available_start == datetime(2026, 10, 14, 9, 0)


def test_find_next_available_slot_moves_after_conflict() -> None:
	owner = Owner(1, "Alex")
	pet = Pet(1, "Buddy", "Dog")
	pet.add_task(
		Task(
			"Walk",
			datetime(2026, 10, 14, 8, 0),
			duration=timedelta(hours=1),
		)
	)
	owner.add_pet(pet)

	available_start = Scheduler(owner).find_next_available_slot(
		datetime(2026, 10, 14, 8, 30),
		timedelta(minutes=30),
	)

	assert available_start == datetime(2026, 10, 14, 9, 0)


def test_find_next_available_slot_checks_tasks_across_pets() -> None:
	owner = Owner(1, "Alex")
	dog = Pet(1, "Buddy", "Dog")
	cat = Pet(2, "Luna", "Cat")
	cat.add_task(
		Task(
			"Grooming",
			datetime(2026, 10, 14, 10, 0),
			duration=timedelta(minutes=45),
		)
	)
	owner.add_pet(dog)
	owner.add_pet(cat)

	available_start = Scheduler(owner).find_next_available_slot(
		datetime(2026, 10, 14, 10, 15),
		timedelta(minutes=30),
	)

	assert available_start == datetime(2026, 10, 14, 10, 45)


def test_find_next_available_slot_rejects_unknown_existing_duration() -> None:
	owner = Owner(1, "Alex")
	pet = Pet(1, "Buddy", "Dog")
	pet.add_task(Task("Walk", datetime(2026, 10, 14, 8, 0)))
	owner.add_pet(pet)

	with pytest.raises(ValueError, match="has no duration"):
		Scheduler(owner).find_next_available_slot(
			datetime(2026, 10, 14, 8, 15),
			timedelta(minutes=30),
		)