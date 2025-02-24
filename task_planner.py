import streamlit as st
import json
import os
from datetime import date, datetime

# Name of the JSON file where tasks will be saved
DATA_FILE = 'tasks.json'

def load_tasks():
    """
    Loads tasks from the JSON file.
    If the file does not exist or there is an error, it returns an empty list.

    This function also converts any old-format tasks (strings) to the new format (dict).
    And if day_of_week is missing, it calculates it from the deadline.
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                tasks = []
    else:
        tasks = []

    migrated_tasks = []
    for item in tasks:
        if isinstance(item, dict):
            # Ensure the dict has the needed keys
            if "task" in item and "deadline" in item and "completed" in item:
                # If day_of_week is missing, calculate it
                if "day_of_week" not in item:
                    try:
                        deadline_date = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
                        item["day_of_week"] = deadline_date.strftime("%A")
                    except ValueError:
                        # If the date is invalid, default to today
                        item["day_of_week"] = date.today().strftime("%A")
                migrated_tasks.append(item)
            else:
                # If it's missing essential keys, skip or handle as needed
                pass
        elif isinstance(item, str):
            # Convert old string tasks to the new dictionary format
            today_str = date.today().strftime("%Y-%m-%d")
            day_of_week = date.today().strftime("%A")
            migrated_tasks.append({
                "task": item,
                "deadline": today_str,
                "day_of_week": day_of_week,
                "completed": False
            })
        else:
            # Unknown format, skip or handle as needed
            pass

    # If we migrated or updated anything, save the new format
    if migrated_tasks and migrated_tasks != tasks:
        tasks = migrated_tasks
        save_tasks(tasks)

    return tasks

def save_tasks(tasks):
    """
    Saves the tasks list to a JSON file.
    """
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f)

def add_task(tasks, task_text, task_deadline):
    """
    Adds a new task to the list, including the day of the week.
    Each task is a dictionary with keys:
        - 'task'
        - 'deadline'
        - 'day_of_week'
        - 'completed'
    """
    day_of_week = task_deadline.strftime("%A")
    new_task = {
        "task": task_text,
        "deadline": task_deadline.strftime("%Y-%m-%d"),
        "day_of_week": day_of_week,
        "completed": False
    }
    tasks.append(new_task)
    save_tasks(tasks)

def remove_completed_tasks(tasks):
    """
    Removes tasks that are marked as completed.
    Returns the updated list of tasks.
    """
    updated_tasks = [task for task in tasks if not task.get("completed", False)]
    save_tasks(updated_tasks)
    return updated_tasks

def main():
    # Set page config for better display
    st.set_page_config(page_title="Growth Mindset App", layout="centered")

    # Main Heading
    st.title("Growth Mindset App 🚀")
    st.header("Daily Task Planner ✅")

    # Load tasks at the start
    tasks = load_tasks()

    # --- SIDEBAR FORM ---
    with st.sidebar.form("add_task_form", clear_on_submit=True):
        st.subheader("Add a New Task 📝")
        new_task_text = st.text_input("Task Description:")
        new_task_deadline = st.date_input("Deadline:", value=date.today())
        submit_button = st.form_submit_button("Add Task")

    # If the user clicked the "Add Task" button in the form
    if submit_button:
        if new_task_text.strip():
            add_task(tasks, new_task_text.strip(), new_task_deadline)
            st.rerun()  # Refresh the UI after adding a task
        else:
            st.sidebar.error("Please enter a task description!")

    # --- MAIN CONTENT ---
    st.header("Your Tasks")
    if not tasks:
        st.info("No tasks added yet. Use the sidebar to add a new task!")
    else:
        # Display each task with a checkbox
        for i, task in enumerate(tasks):
            # Show the task, its deadline, and the day of the week
            checkbox_label = (
                f"{task['task']} "
                f"(Deadline: {task['deadline']} - {task['day_of_week']})"
            )
            checkbox_value = st.checkbox(
                checkbox_label,
                value=task.get("completed", False),
                key=f"task_{i}"
            )
            # If checkbox state changes, update the task's 'completed' status
            if checkbox_value != task.get("completed", False):
                tasks[i]['completed'] = checkbox_value
                save_tasks(tasks)
                st.rerun()

        # Button to remove all completed tasks
        if st.button("Remove Completed Tasks 🗑️"):
            tasks = remove_completed_tasks(tasks)
            st.rerun()

        # Show a motivational message if all tasks are completed
        if tasks and all(task.get("completed", False) for task in tasks):
            st.success("Great job! All tasks are completed! 🎉")

if __name__ == "__main__":
    main()
