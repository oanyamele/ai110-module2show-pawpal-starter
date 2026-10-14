from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Owner:
	owner_id: int
	name: str
	pets: list[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		self.pets.append(pet)

	def list_pets(self) -> list[Pet]:
		return self.pets.copy()


@dataclass
class Pet:
	pet_id: int
	name: str
	species: str
	tasks: list[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		self.tasks.append(task)

	def list_tasks(self) -> list[Task]:
		return self.tasks.copy()


@dataclass
class Task:
	description: str
	due_time: datetime
	is_complete: bool = False

	def mark_complete(self) -> None:
		self.is_complete = True


@dataclass
class Scheduler:
	owner: Owner

	def get_all_tasks(self) -> list[Task]:
		return [task for pet in self.owner.list_pets() for task in pet.list_tasks()]

	def sort_tasks_by_due_time(self) -> list[Task]:
		return sorted(self.get_all_tasks(), key=lambda task: task.due_time)

	def filter_incomplete_tasks(self) -> list[Task]:
		return [task for task in self.get_all_tasks() if not task.is_complete]
