from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path


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

	def save_to_json(self, file_path: str | Path) -> None:
		"""Save this owner, pets, and tasks to a JSON file."""
		data = {
			"owner_id": self.owner_id,
			"name": self.name,
			"pets": [
				{
					"pet_id": pet.pet_id,
					"name": pet.name,
					"species": pet.species,
					"tasks": [
						{
							"description": task.description,
							"due_time": task.due_time.isoformat(),
							"is_complete": task.is_complete,
							"frequency": task.frequency,
							"priority": task.priority,
							"duration_seconds": (
								task.duration.total_seconds()
								if task.duration is not None
								else None
							),
						}
						for task in pet.list_tasks()
					],
				}
				for pet in self.list_pets()
			],
		}
		with Path(file_path).open("w", encoding="utf-8") as json_file:
			json.dump(data, json_file, indent=2)
			json_file.write("\n")

	@classmethod
	def load_from_json(cls, file_path: str | Path) -> Owner | None:
		"""Load an owner from JSON, returning None if the file is missing."""
		path = Path(file_path)
		try:
			with path.open(encoding="utf-8") as json_file:
				data = json.load(json_file)
		except FileNotFoundError:
			return None
		except json.JSONDecodeError as error:
			raise ValueError(f"Invalid JSON in {path}: {error.msg}.") from error

		if not isinstance(data, dict):
			raise ValueError("Invalid owner data: expected a JSON object.")

		def require_value(record: dict, key: str, expected_type: type) -> object:
			value = record.get(key)
			if not isinstance(value, expected_type) or (
				expected_type is int and isinstance(value, bool)
			):
				raise ValueError(
					f"Invalid owner data: '{key}' must be {expected_type.__name__}."
				)
			return value

		owner_id = require_value(data, "owner_id", int)
		name = require_value(data, "name", str)
		pets_data = require_value(data, "pets", list)
		pets = []
		for pet_index, pet_data in enumerate(pets_data):
			if not isinstance(pet_data, dict):
				raise ValueError(f"Invalid owner data: pet at index {pet_index} must be an object.")
			pet_id = require_value(pet_data, "pet_id", int)
			pet_name = require_value(pet_data, "name", str)
			species = require_value(pet_data, "species", str)
			tasks_data = require_value(pet_data, "tasks", list)
			tasks = []
			for task_index, task_data in enumerate(tasks_data):
				if not isinstance(task_data, dict):
					raise ValueError(
						f"Invalid owner data: task at pet index {pet_index}, "
						f"task index {task_index} must be an object."
					)
				description = require_value(task_data, "description", str)
				due_time_text = require_value(task_data, "due_time", str)
				is_complete = require_value(task_data, "is_complete", bool)
				frequency = require_value(task_data, "frequency", str)
				priority = require_value(task_data, "priority", str)
				duration_seconds = task_data.get("duration_seconds")
				if duration_seconds is not None and (
					isinstance(duration_seconds, bool)
					or not isinstance(duration_seconds, (int, float))
					or duration_seconds <= 0
				):
					raise ValueError(
						f"Invalid owner data: 'duration_seconds' for task "
						f"'{description}' must be a positive number or null."
					)
				try:
					due_time = datetime.fromisoformat(due_time_text)
				except ValueError as error:
					raise ValueError(
						f"Invalid owner data: invalid due_time for task "
						f"'{description}'."
					) from error
				tasks.append(
					Task(
						description=description,
						due_time=due_time,
						is_complete=is_complete,
						frequency=frequency,
						priority=priority,
						duration=(
							timedelta(seconds=duration_seconds)
							if duration_seconds is not None
							else None
						),
					)
				)
			pets.append(
				Pet(
					pet_id=pet_id,
					name=pet_name,
					species=species,
					tasks=tasks,
				)
			)
		return cls(owner_id=owner_id, name=name, pets=pets)


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
	priority: str = "medium"
	duration: timedelta | None = None

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

	def sort_tasks_by_priority(self) -> list[Task]:
		"""Sort tasks by priority first, then by due date and time."""
		priority_order = {
			"high": 0,
			"medium": 1,
			"low": 2,
		}

		return sorted(
			self.get_all_tasks(),
			key=lambda task: (
				priority_order.get(task.priority.lower(), 1),
				task.due_time,
			),
		)
	
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
			priority=task.priority,
			duration=task.duration,
		)
		pet.add_task(next_task)
		return next_task

	def find_next_available_slot(
		self,
		requested_start: datetime,
		duration: timedelta,
	) -> datetime:
		"""Find the earliest non-overlapping slot using known task durations."""
		if duration <= timedelta(0):
			raise ValueError("Proposed task duration must be greater than zero.")

		existing_tasks = [
			task for task in self.get_all_tasks() if not task.is_complete
		]
		for task in existing_tasks:
			if task.duration is None:
				raise ValueError(
					f"Task '{task.description}' has no duration; "
					"set durations for unfinished tasks before finding an available slot."
				)

		candidate_start = requested_start
		for task in sorted(existing_tasks, key=lambda existing: existing.due_time):
			task_end = task.due_time + task.duration
			candidate_end = candidate_start + duration
			if candidate_end <= task.due_time:
				break
			if candidate_start < task_end:
				candidate_start = task_end

		return candidate_start

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
