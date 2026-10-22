from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
	schedule_date = datetime(2026, 10, 14)
	owner = Owner(owner_id=1, name="Alex Morgan")

	buddy = Pet(pet_id=1, name="Buddy", species="Dog")
	luna = Pet(pet_id=2, name="Luna", species="Cat")

	buddy_walk = Task(
		"Morning walk",
		datetime(2026, 10, 14, 7, 30),
		frequency="daily",
		priority="high",
	)

	buddy_meal = Task(
		"Breakfast",
		datetime(2026, 10, 14, 8, 0),
		frequency="twice daily",
		priority="medium",
	)

	luna_grooming = Task(
		"Brush coat",
		datetime(2026, 10, 14, 7, 30),
		frequency="weekly",
		priority="low",
	)

	buddy.add_task(buddy_walk)
	buddy.add_task(buddy_meal)
	luna.add_task(luna_grooming)
	owner.add_pet(buddy)
	owner.add_pet(luna)

	scheduler = Scheduler(owner)
	next_walk = scheduler.mark_task_complete(buddy, buddy_walk)
	all_tasks = scheduler.get_all_tasks()
	sorted_tasks = scheduler.sort_tasks_by_due_time()
	priority_tasks = scheduler.sort_tasks_by_priority()
	incomplete_tasks = scheduler.filter_incomplete_tasks()
	buddy_incomplete_tasks = scheduler.filter_tasks("Buddy", is_complete=False)
	pet_names = {
		id(task): pet.name
		for pet in owner.list_pets()
		for task in pet.list_tasks()
	}

	priority_icons = {
        "high": "🔴 HIGH",
        "medium": "🟡 MEDIUM",
        "low": "🟢 LOW",
    }

	print("=" * 100)
	print("🐾 PAWPAL+ | PET CARE SCHEDULER")
	print("=" * 100)
	print(f"📅 Schedule Date: ({schedule_date:%A, %B %d, %Y})")
	print(f"👤 Owner: {owner.name} | 📋 Tasks: {len(all_tasks)}")
	print(f"🐶 Pets: {len(owner.list_pets())} ")

	print("\n📅 CHRONOLOGICAL SCHEDULE")
	print("-" * 100)
	print(
        f"{'DUE TIME':<19} {'PET':<9} {'TASK':<22} "
        f"{'PRIORITY':<12} {'STATUS':<12}"
    )
	print("-" * 100)
	
	for task in sorted_tasks:
		status = "✅ Complete" if task.is_complete else "❌ Incomplete"
		priority = priority_icons.get(
            task.priority.lower(), "⚪ UNKNOWN"
        )
		print(
			f"{task.due_time:%Y-%m-%d %H:%M}  {pet_names[id(task)]:<7}  "
			f"{task.description:<20}  {task.frequency:<13}  {status}"
		)
	if next_walk is not None:
		print("\n🔁 RECURRING TASK")
		print(
			f"\nNext occurrence: {next_walk.description} for Buddy at "
			f"{next_walk.due_time:%Y-%m-%d %H:%M}"
		)

	print("\n⭐ PRIORITY-BASED SCHEDULE")
	print("-" * 100)
	print(f"{'PRIORITY':<14} {'DUE TIME':<19} {'PET':<9} TASK")
	print("-" * 100)

	for task in priority_tasks:
		priority = priority_icons.get(
        	task.priority.lower(), "⚪ UNKNOWN"
    	)
		print(
            f"{priority:<14} "
            f"{task.due_time:%Y-%m-%d %H:%M}  "
            f"{pet_names[id(task)]:<9} {task.description}"
        )

	print(f"\n⏳ Incomplete Tasks ({len(incomplete_tasks)})")
	print("-" * 100)
	for task in incomplete_tasks:
		print(
			f"{task.due_time:%H:%M}  {pet_names[id(task)]}: "
			f"{task.description} ({task.frequency})"
		)

	print(f"\nIncomplete Buddy Tasks ({len(buddy_incomplete_tasks)})")
	for task in buddy_incomplete_tasks:
		print(f"{task.due_time:%Y-%m-%d %H:%M}  {task.description}")

	print("\n⚠️ Schedule Conflicts")
	print("-" * 100)
	conflict_warnings = scheduler.find_conflicts()
	if conflict_warnings:
		for warning in conflict_warnings:
			print(warning)
	else:
		print("✅ No conflicts found.")


	print("\n" + "=" * 100)
	print("🐾 End of PawPal+ schedule")
	print("=" * 100)


if __name__ == "__main__":
	main()
