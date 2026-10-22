from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


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
