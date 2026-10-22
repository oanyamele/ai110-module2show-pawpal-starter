from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
	schedule_date = datetime(2026, 10, 14)
	owner = Owner(owner_id=1, name="Alex Morgan")

	buddy = Pet(pet_id=1, name="Buddy", species="Dog")
	luna = Pet(pet_id=2, name="Luna", species="Cat")

	buddy_walk = Task("Morning walk", datetime(2026, 10, 14, 7, 30), frequency="daily")
	buddy_meal = Task("Breakfast", datetime(2026, 10, 14, 8, 0), frequency="twice daily")
	luna_grooming = Task("Brush coat", datetime(2026, 10, 14, 7, 30), frequency="weekly")

	buddy.add_task(buddy_walk)
	buddy.add_task(buddy_meal)
	luna.add_task(luna_grooming)
	owner.add_pet(buddy)
	owner.add_pet(luna)

	scheduler = Scheduler(owner)
	next_walk = scheduler.mark_task_complete(buddy, buddy_walk)
	all_tasks = scheduler.get_all_tasks()
	sorted_tasks = scheduler.sort_tasks_by_due_time()
	incomplete_tasks = scheduler.filter_incomplete_tasks()
	buddy_incomplete_tasks = scheduler.filter_tasks("Buddy", is_complete=False)
	pet_names = {
		id(task): pet.name
		for pet in owner.list_pets()
		for task in pet.list_tasks()
	}

	print(f"Today's Schedule ({schedule_date:%A, %B %d, %Y})")
	print(f"Owner: {owner.name} | Tasks: {len(all_tasks)}")
	print("DUE TIME             PET      TASK                  FREQUENCY      STATUS")
	print("-------------------  -------  --------------------  -------------  ----------")
	for task in sorted_tasks:
		status = "Complete" if task.is_complete else "Incomplete"
		print(
			f"{task.due_time:%Y-%m-%d %H:%M}  {pet_names[id(task)]:<7}  "
			f"{task.description:<20}  {task.frequency:<13}  {status}"
		)
	if next_walk is not None:
		print(
			f"\nNext occurrence: {next_walk.description} for Buddy at "
			f"{next_walk.due_time:%Y-%m-%d %H:%M}"
		)

	print(f"\nIncomplete Tasks ({len(incomplete_tasks)})")
	for task in incomplete_tasks:
		print(
			f"{task.due_time:%H:%M}  {pet_names[id(task)]}: "
			f"{task.description} ({task.frequency})"
		)

	print(f"\nIncomplete Buddy Tasks ({len(buddy_incomplete_tasks)})")
	for task in buddy_incomplete_tasks:
		print(f"{task.due_time:%Y-%m-%d %H:%M}  {task.description}")

	print("\nSchedule Conflicts")
	conflict_warnings = scheduler.find_conflicts()
	if conflict_warnings:
		for warning in conflict_warnings:
			print(warning)
	else:
		print("No conflicts found.")


if __name__ == "__main__":
	main()
