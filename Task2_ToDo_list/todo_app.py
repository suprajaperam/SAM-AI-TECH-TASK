"""To-Do List Application - SAM AI Technologies Python Internship, Task 2.

Add, edit, delete and complete tasks. Tasks are stored in tasks.json.
"""
import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).with_name("tasks.json")


def load_tasks():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print("Warning: data file unreadable, starting with an empty list.")
        return []


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def find_task(tasks, prompt="Task ID: "):
    raw = input(prompt).strip()
    if not raw.isdigit():
        print("  Please enter a valid numeric ID.")
        return None
    for t in tasks:
        if t["id"] == int(raw):
            return t
    print("  No task with that ID.")
    return None


def show_tasks(tasks, which="all"):
    pending = [t for t in tasks if not t["completed"]]
    done = [t for t in tasks if t["completed"]]
    if not tasks:
        print("\nNo tasks yet. Add one!")
        return
    if which in ("all", "pending"):
        print(f"\n--- PENDING ({len(pending)}) ---")
        for t in pending:
            print(f"[ ] {t['id']:>3}. {t['title']}  (added {t['created']})")
        if not pending:
            print("Nothing pending.")
    if which in ("all", "completed"):
        print(f"\n--- COMPLETED ({len(done)}) ---")
        for t in done:
            print(f"[x] {t['id']:>3}. {t['title']}  (done {t.get('completed_on', '-')})")
        if not done:
            print("Nothing completed yet.")


def add_task(tasks):
    title = input("Task title: ").strip()
    if not title:
        print("  Title cannot be empty.")
        return
    new_id = max((t["id"] for t in tasks), default=0) + 1
    tasks.append({"id": new_id, "title": title, "completed": False,
                  "created": datetime.now().strftime("%Y-%m-%d")})
    save_tasks(tasks)
    print("Task added.")


def edit_task(tasks):
    show_tasks(tasks)
    t = find_task(tasks, "ID to edit: ")
    if not t:
        return
    title = input(f"New title [{t['title']}]: ").strip()
    if title:
        t["title"] = title
        save_tasks(tasks)
        print("Task updated.")
    else:
        print("No change made.")


def complete_task(tasks):
    show_tasks(tasks, "pending")
    t = find_task(tasks, "ID to mark complete: ")
    if not t:
        return
    if t["completed"]:
        print("  Already completed.")
        return
    t["completed"] = True
    t["completed_on"] = datetime.now().strftime("%Y-%m-%d")
    save_tasks(tasks)
    print("Marked as completed.")


def delete_task(tasks):
    show_tasks(tasks)
    t = find_task(tasks, "ID to delete: ")
    if t and input(f"Delete '{t['title']}'? (y/n): ").strip().lower() == "y":
        tasks.remove(t)
        save_tasks(tasks)
        print("Task deleted.")


def main():
    tasks = load_tasks()
    actions = {
        "1": ("Add task", add_task),
        "2": ("Edit task", edit_task),
        "3": ("Mark task completed", complete_task),
        "4": ("Delete task", delete_task),
        "5": ("Show pending tasks", lambda t: show_tasks(t, "pending")),
        "6": ("Show completed tasks", lambda t: show_tasks(t, "completed")),
        "7": ("Show all tasks", show_tasks),
    }
    while True:
        print("\n=== TO-DO LIST ===")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("0. Exit")
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        if choice in actions:
            actions[choice][1](tasks)
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
