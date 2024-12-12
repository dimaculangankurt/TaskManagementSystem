import time
import os
import threading
from datetime import datetime, timedelta


class Task:
    def __init__(self, title, description, category, priority, deadline, assigned_user):
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority  # 1 - High, 2 - Medium, 3 - Low
        self.deadline = datetime.strptime(deadline, '%Y-%m-%d')
        self.completed = False
        self.assigned_user = assigned_user

    def mark_as_completed(self):
        self.completed = True

    def to_file_string(self):
        return f"{self.title}|{self.description}|{self.category}|{self.priority}|{self.deadline.date()}|{self.assigned_user}|{self.completed}"

    @classmethod
    def from_file_string(cls, line):
        parts = line.split('|')
        task = cls(parts[0], parts[1], parts[2], int(parts[3]), parts[4], parts[5])
        if parts[6].lower() == 'true':
            task.mark_as_completed()
        return task

    def to_row(self):
        priority_str = {1: "High", 2: "Medium", 3: "Low"}.get(self.priority, "Unknown")
        completed_str = "Yes" if self.completed else "No"
        return [self.title, self.description, self.category, priority_str, str(self.deadline.date()), self.assigned_user, completed_str]


class TaskManager:
    def __init__(self):
        self.tasks = []
        self.file_path = "database.txt"
        self.notification_active = True
        self.upcoming_reminders = []  # Shared list for reminders
        self.load_tasks_from_file()
        self.start_notification_thread()

    def add_task(self, task):
        self.tasks.append(task)
        self.save_tasks_to_file()

    def format_as_table(self, rows, headers):
        col_widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]
        table = []
        header_line = " | ".join(f"{headers[i].ljust(col_widths[i])}" for i in range(len(headers)))
        table.append(header_line)
        table.append("-+-".join("-" * col_widths[i] for i in range(len(headers))))
        for row in rows:
            table.append(" | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(row))))
        return "\n".join(table)

    def list_tasks(self):
        if not self.tasks:
            print("No tasks available.")
            return

        headers = ["Title", "Description", "Category", "Priority", "Deadline", "Assigned To", "Completed"]
        rows = [task.to_row() for task in self.tasks]
        print(self.format_as_table(rows, headers))

    def list_tasks_by_category(self, category):
        headers = ["Title", "Description", "Category", "Priority", "Deadline", "Assigned To", "Completed"]
        rows = [task.to_row() for task in self.tasks if task.category.lower() == category.lower()]
        if rows:
            print(f"Tasks in category: {category}")
            print(self.format_as_table(rows, headers))
        else:
            print(f"No tasks found in category: {category}")

    def list_tasks_by_priority(self, priority):
        headers = ["Title", "Description", "Category", "Priority", "Deadline", "Assigned To", "Completed"]
        rows = [task.to_row() for task in self.tasks if task.priority == priority]
        if rows:
            priority_str = {1: "High", 2: "Medium", 3: "Low"}.get(priority, "Unknown")
            print(f"Tasks with priority: {priority_str}")
            print(self.format_as_table(rows, headers))
        else:
            print(f"No tasks found with priority: {priority}")

    def mark_task_as_completed(self, title):
        for task in self.tasks:
            if task.title.lower() == title.lower():
                task.mark_as_completed()
                self.save_tasks_to_file()
                print(f"Task marked as completed: {task.title}")
                return
        print(f"Task not found: {title}")

    def delete_task(self, title):
        to_remove = None
        for task in self.tasks:
            if task.title.lower() == title.lower():
                to_remove = task
                break
        if to_remove:
            self.tasks.remove(to_remove)
            self.save_tasks_to_file()
            print(f"Task deleted: {title}")
        else:
            print(f"Task not found: {title}")

    def load_tasks_from_file(self):
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path, 'r') as file:
            for line in file:
                self.tasks.append(Task.from_file_string(line.strip()))

    def save_tasks_to_file(self):
        with open(self.file_path, 'w') as file:
            for task in self.tasks:
                file.write(task.to_file_string() + '\n')

    def start_notification_thread(self):
        threading.Thread(target=self.notification_thread, daemon=True).start()

    def notification_thread(self):
        while self.notification_active:
            self.check_upcoming_deadlines()
            time.sleep(60)  # Check every minute

    def check_upcoming_deadlines(self):
        now = datetime.now()
        self.upcoming_reminders.clear()

        for task in self.tasks:
            if not task.completed and task.deadline > now and task.deadline < now + timedelta(days=1):
                self.upcoming_reminders.append(f"Task '{task.title}' has a deadline within 24 hours!")

    def stop_notifications(self):
        self.notification_active = False


def main():
    task_manager = TaskManager()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        
        if task_manager.upcoming_reminders:
            print("\n--- To-Do ---")
            print("\n".join(task_manager.upcoming_reminders))
            print("\n")

        print("--- Task Management System ---")
        print("1. Add Task")
        print("2. List All Tasks")
        print("3. List Tasks by Category")
        print("4. List Tasks by Priority")
        print("5. Mark Task as Completed")
        print("6. Delete Task")
        print("7. Exit")

        try:
            choice = int(input("Choose an option: "))
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue

        if choice == 1:
            title = input("Enter task title: ")
            description = input("Enter description: ")
            category = input("Enter category: ")
            try:
                priority = int(input("Enter priority (1-High, 2-Medium, 3-Low): "))
            except ValueError:
                print("Invalid priority. Please enter a number between 1 and 3.")
                continue
            deadline = input("Enter deadline (yyyy-mm-dd): ")
            assigned_user = input("Assign to user: ")

            try:
                task = Task(title, description, category, priority, deadline, assigned_user)
                task_manager.add_task(task)
                print("Task added successfully!")
            except ValueError:
                print("Invalid date format. Please use yyyy-mm-dd.")

        elif choice == 2:
            os.system('cls' if os.name == 'nt' else 'clear')
            task_manager.list_tasks()
            input("\n\nPress Enter to continue...")

        elif choice == 3:
            os.system('cls' if os.name == 'nt' else 'clear')
            filter_category = input("Enter category: ")
            task_manager.list_tasks_by_category(filter_category)
            input("\n\nPress Enter to continue...")

        elif choice == 4:
            os.system('cls' if os.name == 'nt' else 'clear')
            try:
                filter_priority = int(input("Enter priority (1-High, 2-Medium, 3-Low): "))
                task_manager.list_tasks_by_priority(filter_priority)
            except ValueError:
                print("Invalid priority. Please enter a valid number.")
            input("\n\nPress Enter to continue...")

        elif choice == 5:
            os.system('cls' if os.name == 'nt' else 'clear')
            completed_task_title = input("Enter task title to mark as completed: ")
            task_manager.mark_task_as_completed(completed_task_title)
            input("\n\nPress Enter to continue...")

        elif choice == 6:
            os.system('cls' if os.name == 'nt' else 'clear')
            delete_task_title = input("Enter task title to delete: ")
            task_manager.delete_task(delete_task_title)
            input("\n\nPress Enter to continue...")

        elif choice == 7:
            print(".........")
            task_manager.stop_notifications()  # Stop the notification thread
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
