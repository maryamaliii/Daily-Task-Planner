import streamlit as st
import json
import os
from datetime import date, datetime

def get_data_file(username):
    return f"tasks_{username}.json"

def load_tasks(username):
    data_file = get_data_file(username)
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                tasks = []
    else:
        tasks = []
    
    migrated_tasks = []
    for item in tasks:
        if isinstance(item, dict):
            if "task" in item and "deadline" in item and "completed" in item:
                if "day_of_week" not in item:
                    try:
                        deadline_date = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
                        item["day_of_week"] = deadline_date.strftime("%A")
                    except ValueError:
                        item["day_of_week"] = date.today().strftime("%A")
                migrated_tasks.append(item)
        elif isinstance(item, str):
            today_str = date.today().strftime("%Y-%m-%d")
            day_of_week = date.today().strftime("%A")
            migrated_tasks.append({
                "task": item,
                "deadline": today_str,
                "day_of_week": day_of_week,
                "completed": False
            })
    if migrated_tasks and migrated_tasks != tasks:
        tasks = migrated_tasks
        save_tasks(username, tasks)
    return tasks

def save_tasks(username, tasks):
    data_file = get_data_file(username)
    with open(data_file, 'w') as f:
        json.dump(tasks, f)

def add_task(username, tasks, task_text, task_deadline):
    day_of_week = task_deadline.strftime("%A")
    new_task = {
        "task": task_text,
        "deadline": task_deadline.strftime("%Y-%m-%d"),
        "day_of_week": day_of_week,
        "completed": False
    }
    tasks.append(new_task)
    save_tasks(username, tasks)

def edit_task(username, tasks, index, new_text, new_deadline):
    tasks[index]["task"] = new_text
    tasks[index]["deadline"] = new_deadline.strftime("%Y-%m-%d")
    tasks[index]["day_of_week"] = new_deadline.strftime("%A")
    save_tasks(username, tasks)

def delete_task(username, tasks, index):
    del tasks[index]
    save_tasks(username, tasks)

def remove_completed_tasks(username, tasks):
    updated_tasks = [task for task in tasks if not task.get("completed", False)]
    save_tasks(username, updated_tasks)
    return updated_tasks

def main():
    st.set_page_config(page_title="Growth Mindset App", layout="centered")
    st.title("Growth Mindset App 🌟")
    st.header("📋 Daily Task Planner")
    
    username = st.sidebar.text_input("Enter your username:")
    if not username.strip():
        st.sidebar.error("Please enter your username to see your tasks!")
        st.stop()
    
    tasks = load_tasks(username.strip())
    
    with st.sidebar.form("add_task_form", clear_on_submit=True):
        st.subheader("📝 Add a New Task")
        new_task_text = st.text_input("Task Description:")
        new_task_deadline = st.date_input("Deadline:", value=date.today())
        submit_button = st.form_submit_button("Add Task")
    
    if submit_button:
        if new_task_text.strip():
            add_task(username.strip(), tasks, new_task_text.strip(), new_task_deadline)
            st.rerun()
        else:
            st.sidebar.error("Please enter a task description!")
    
    st.header("Your Tasks")
    if not tasks:
        st.info("No tasks added yet. Use the sidebar to add a new task!")
    else:
        for i, task in enumerate(tasks):
            cols = st.columns([0.7, 0.2, 0.1])  # Column layout for better UI
            checkbox_value = cols[0].checkbox(
                f"{task['task']} (Deadline: {task['deadline']} - {task['day_of_week']})", 
                value=task.get("completed", False), key=f"task_{i}"
            )
            
            if checkbox_value != task.get("completed", False):
                tasks[i]['completed'] = checkbox_value
                save_tasks(username.strip(), tasks)
                st.rerun()
            
            with cols[1]:
                with st.expander("⋮", expanded=False):
                    if st.button(" Edit", key=f"edit_{i}"):
                        new_text = st.text_input("Edit Task Description:", value=task["task"])
                        new_deadline = st.date_input("Edit Deadline:", value=datetime.strptime(task["deadline"], "%Y-%m-%d").date())
                        if st.button("Update Task", key=f"update_{i}"):
                            edit_task(username.strip(), tasks, i, new_text.strip(), new_deadline)
                            st.rerun()

                    if st.button(" Delete", key=f"delete_{i}"):
                        delete_task(username.strip(), tasks, i)
                        st.rerun()
        
        if st.button("Remove Completed Tasks 🗑️"):
            tasks = remove_completed_tasks(username.strip(), tasks)
            st.rerun()
        
        if tasks and all(task.get("completed", False) for task in tasks):
            st.success("Great job! All tasks are completed! 🎉")

if __name__ == "__main__":
    main()
