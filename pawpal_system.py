from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Owner:
	owner_id: int
	name: str
	pets: list[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner's collection."""
		self.pets.append(pet)

	def list_pets(self) -> list[Pet]:
		"""Return a copy of this owner's pets."""
		return self.pets.copy()

	def list_tasks(self) -> list[Task]:
		"""Return tasks belonging to all of this owner's pets."""
		return [task for pet in self.list_pets() for task in pet.list_tasks()]


@dataclass
class Pet:
	pet_id: int
	name: str
	species: str
	tasks: list[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		"""Add a task to this pet's collection."""
		self.tasks.append(task)

	def list_tasks(self) -> list[Task]:
		"""Return a copy of this pet's tasks."""
		return self.tasks.copy()


@dataclass
class Task:
	description: str
	due_time: datetime
	is_complete: bool = False
	frequency: str = "once"

	def mark_complete(self) -> None:
		"""Mark this task as complete."""
		self.is_complete = True


@dataclass
class Scheduler:
	owner: Owner

	def get_all_tasks(self) -> list[Task]:
		"""Return all tasks across the owner's pets."""
		return self.owner.list_tasks()

	def sort_tasks_by_due_time(self) -> list[Task]:
		"""Return all tasks in stable due-time order."""
		return sorted(self.get_all_tasks(), key=lambda task: task.due_time)

	def filter_incomplete_tasks(self) -> list[Task]:
		"""Return all tasks that are not complete."""
		return [task for task in self.get_all_tasks() if not task.is_complete]

	def filter_tasks(
		self,
		pet_name: str,
		is_complete: bool | None = None,
	) -> list[Task]:
		"""Return tasks for a named pet, optionally filtered by completion."""
		return [
			task
			for pet in self.owner.list_pets()
			if pet.name == pet_name
			for task in pet.list_tasks()
			if is_complete is None or task.is_complete is is_complete
		]

	def mark_task_complete(self, pet: Pet, task: Task) -> Task | None:
		"""Complete an owned task and add its next daily or weekly occurrence."""
		pet_is_owned = any(owner_pet is pet for owner_pet in self.owner.list_pets())
		task_is_owned = any(pet_task is task for pet_task in pet.list_tasks())
		if not pet_is_owned or not task_is_owned:
			raise ValueError("The task must belong to the specified owner's pet.")

		if task.is_complete:
			return None

		task.mark_complete()
		delta_by_frequency = {
			"daily": timedelta(days=1),
			"weekly": timedelta(days=7),
		}
		delta = delta_by_frequency.get(task.frequency)
		if delta is None:
			return None

		next_task = Task(
			description=task.description,
			due_time=task.due_time + delta,
			frequency=task.frequency,
		)
		pet.add_task(next_task)
		return next_task

	def find_conflicts(self) -> list[str]:
		"""Return readable warnings for tasks sharing an exact due time."""
		tasks_by_due_time: dict[datetime, list[tuple[str, Task]]] = {}
		for pet in self.owner.list_pets():
			for task in pet.list_tasks():
				tasks_by_due_time.setdefault(task.due_time, []).append((pet.name, task))

		warnings = []
		for due_time, pet_tasks in tasks_by_due_time.items():
			if len(pet_tasks) < 2:
				continue
			task_details = ", ".join(
				f'"{task.description}" for {pet_name}'
				for pet_name, task in pet_tasks
			)
			warnings.append(
				f"Schedule conflict at {due_time.isoformat(sep=' ')}: {task_details}."
			)
		return warnings
