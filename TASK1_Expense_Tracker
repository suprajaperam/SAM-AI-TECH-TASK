"""Expense Tracker - SAM AI Technologies Python Internship, Task 1.

Add, update and delete expenses; see total, monthly and category summaries.
Data is stored in expenses.json next to this script.
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).with_name("expenses.json")


def load_expenses():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print("Warning: data file unreadable, starting with an empty list.")
        return []


def save_expenses(expenses):
    DATA_FILE.write_text(json.dumps(expenses, indent=2), encoding="utf-8")


def next_id(expenses):
    return max((e["id"] for e in expenses), default=0) + 1


def ask_amount(prompt, default=None):
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            value = float(raw)
            if value <= 0:
                raise ValueError
            return round(value, 2)
        except ValueError:
            print("  Please enter a positive number.")


def ask_date(prompt, default=None):
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            return datetime.strptime(raw, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print("  Use the format YYYY-MM-DD (e.g. 2026-10-02).")


def ask_id(expenses, prompt):
    raw = input(prompt).strip()
    if not raw.isdigit():
        print("  Invalid ID.")
        return None
    for e in expenses:
        if e["id"] == int(raw):
            return e
    print("  No expense with that ID.")
    return None


def print_table(expenses):
    if not expenses:
        print("\nNo expenses recorded.")
        return
    print(f"\n{'ID':<4} {'Date':<11} {'Category':<14} {'Description':<22} {'Amount':>10}")
    print("-" * 65)
    for e in sorted(expenses, key=lambda x: x["date"]):
        print(f"{e['id']:<4} {e['date']:<11} {e['category'][:13]:<14} "
              f"{e['description'][:21]:<22} {e['amount']:>10.2f}")


def add_expense(expenses):
    today = datetime.now().strftime("%Y-%m-%d")
    date = ask_date(f"Date [{today}]: ", default=today)
    category = input("Category (Food, Travel, ...): ").strip() or "General"
    description = input("Description: ").strip() or "-"
    amount = ask_amount("Amount: ")
    expenses.append({"id": next_id(expenses), "date": date, "category": category,
                     "description": description, "amount": amount})
    save_expenses(expenses)
    print("Expense added.")


def update_expense(expenses):
    print_table(expenses)
    e = ask_id(expenses, "ID to update: ")
    if not e:
        return
    print("Press Enter to keep the current value.")
    e["date"] = ask_date(f"Date [{e['date']}]: ", default=e["date"])
    e["category"] = input(f"Category [{e['category']}]: ").strip() or e["category"]
    e["description"] = input(f"Description [{e['description']}]: ").strip() or e["description"]
    e["amount"] = ask_amount(f"Amount [{e['amount']}]: ", default=e["amount"])
    save_expenses(expenses)
    print("Expense updated.")


def delete_expense(expenses):
    print_table(expenses)
    e = ask_id(expenses, "ID to delete: ")
    if e and input(f"Delete '{e['description']}'? (y/n): ").lower() == "y":
        expenses.remove(e)
        save_expenses(expenses)
        print("Expense deleted.")


def show_summary(expenses):
    if not expenses:
        print("\nNo expenses recorded.")
        return
    monthly, by_category = defaultdict(float), defaultdict(float)
    for e in expenses:
        monthly[e["date"][:7]] += e["amount"]
        by_category[e["category"]] += e["amount"]
    print("\n===== EXPENSE SUMMARY =====")
    print(f"Total expenses : {sum(monthly.values()):.2f}")
    print("\nMonthly totals:")
    for month in sorted(monthly):
        print(f"  {month} : {monthly[month]:>10.2f}")
    print("\nBy category:")
    for cat, amt in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat:<14}: {amt:>10.2f}")


def main():
    expenses = load_expenses()
    actions = {
        "1": ("Add expense", lambda: add_expense(expenses)),
        "2": ("View all expenses", lambda: print_table(expenses)),
        "3": ("Update expense", lambda: update_expense(expenses)),
        "4": ("Delete expense", lambda: delete_expense(expenses)),
        "5": ("Summary (total / monthly / category)", lambda: show_summary(expenses)),
    }
    while True:
        print("\n=== EXPENSE TRACKER ===")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("0. Exit")
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        if choice in actions:
            actions[choice][1]()
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
