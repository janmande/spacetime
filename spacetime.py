import os
import yaml
import csv
import datetime
import argparse
from collections import defaultdict

PROJECTS_FILE = "projects.yaml"
LOG_FILE = "work_log.csv"
SESSION_FILE = "session.yaml"


def load_projects():
    try:
        with open(PROJECTS_FILE, "r") as file:
            return yaml.safe_load(file) or []
    except FileNotFoundError:
        return []


def save_projects(projects):
    with open(PROJECTS_FILE, "w") as file:
        yaml.dump(projects, file)


def add_project(name, code):
    projects = load_projects()
    projects.append({"name": name, "code": code})
    save_projects(projects)
    print(f"Project '{name}' with code '{code}' added.")


def list_projects():
    projects = load_projects()
    for project in projects:
        print(f"Code: {project['code']} - Name: {project['name']}")


def start_work(project_code, custom_start=None):
    projects = load_projects()
    project = next((p for p in projects if p["code"] == project_code), None)
    if project:
        if custom_start:
            try:
                # Use specified time if provided
                start_time = datetime.datetime.combine(
                    datetime.date.today(), datetime.datetime.strptime(custom_start, "%H:%M").time()
                )
            except ValueError:
                print("Invalid time format. Please use HH:MM.")
                return
        else:
            # Default to current time if no custom time is provided
            start_time = datetime.datetime.now()

        session = {"project": project, "start_time": start_time}
        with open(SESSION_FILE, "w") as file:
            yaml.dump(session, file)
        print(f"Started work on '{project['name']}' at {start_time.strftime('%H:%M:%S')}")
    else:
        print("Project not found.")


def load_session():
    try:
        with open(SESSION_FILE, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("No active session found.")
        return None


def stop_work():
    session = load_session()
    if session:
        end_time = datetime.datetime.now()
        # Format times without milliseconds
        entry = {
            "date": session["start_time"].date().strftime("%Y-%m-%d"),
            "start_time": session["start_time"].strftime("%H:%M:%S"),
            "end_time": end_time.strftime("%H:%M:%S"),
            "project_name": session["project"]["name"],
            "project_code": session["project"]["code"],
        }
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=entry.keys())
            if not file_exists:
                writer.writeheader()  # Write headers if file doesn't exist
            writer.writerow(entry)
        print(f"Stopped work on '{session['project']['name']}' at {end_time}. Entry logged.")
        with open(SESSION_FILE, "w") as file:
            yaml.dump({}, file)  # Clear the session
    else:
        print("No session to stop.")


def summarize_week():
    entries = []
    try:
        with open(LOG_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            entries = list(reader)
    except FileNotFoundError:
        print("No log file found. No hours to summarize.")
        return

    week_summary = defaultdict(float)
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())  # Monday of the current week

    for entry in entries:
        entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if start_of_week <= entry_date <= today:
            start_time = datetime.datetime.strptime(entry["start_time"], "%H:%M:%S")
            end_time = datetime.datetime.strptime(entry["end_time"], "%H:%M:%S")
            duration = (end_time - start_time).total_seconds() / 3600  # Convert seconds to hours
            week_summary[entry_date] += duration

    for day, hours in sorted(week_summary.items()):
        print(f"{day.strftime('%A')}: {hours:.2f} hours")


def add_entry(project_code, date, start_time, stop_time):
    # Load projects to validate the project code
    projects = load_projects()
    project = next((p for p in projects if p["code"] == project_code), None)
    if project:
        try:
            # Parse date and times
            entry_date = datetime.datetime.strptime(date, "%d:%m").date()
            entry_date = entry_date.replace(year=datetime.date.today().year)  # Assume current year
            start_time = datetime.datetime.combine(entry_date, datetime.datetime.strptime(start_time, "%H:%M").time())
            stop_time = datetime.datetime.combine(entry_date, datetime.datetime.strptime(stop_time, "%H:%M").time())

            # Ensure start time is before stop time
            if start_time >= stop_time:
                print("Start time must be before stop time.")
                return

            # Create the entry
            entry = {
                "date": entry_date.strftime("%Y-%m-%d"),
                "start_time": start_time.strftime("%H:%M:%S"),
                "end_time": stop_time.strftime("%H:%M:%S"),
                "project_name": project["name"],
                "project_code": project["code"],
            }

            file_exists = os.path.isfile(LOG_FILE)
            with open(LOG_FILE, "a", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=entry.keys())
                if not file_exists:
                    writer.writeheader()  # Write headers if file doesn't exist
                writer.writerow(entry)

            print(f"Entry for project '{project['name']}' on {entry['date']} added.")

        except ValueError:
            print("Invalid date or time format. Please use dd:mm for date and HH:MM for time.")
    else:
        print("Project not found.")


def summarize_project_week():
    try:
        with open(LOG_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            entries = list(reader)
    except FileNotFoundError:
        print("No log file found. No hours to summarize.")
        return

    project_summary = defaultdict(float)
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())  # Monday of the current week

    for entry in entries:
        entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if start_of_week <= entry_date <= today:
            start_time = datetime.datetime.combine(
                entry_date, datetime.datetime.strptime(entry["start_time"], "%H:%M:%S").time()
            )
            end_time = datetime.datetime.combine(
                entry_date, datetime.datetime.strptime(entry["end_time"], "%H:%M:%S").time()
            )
            duration = (end_time - start_time).total_seconds() / 3600  # Convert seconds to hours
            project_summary[entry["project_code"]] += duration

    for project_code, hours in project_summary.items():
        print(f"Project {project_code}: {hours:.2f} hours")


def main():
    parser = argparse.ArgumentParser(description="Project Hours Logger CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add project command
    add_parser = subparsers.add_parser("add_project", help="Add a new project")
    add_parser.add_argument("name", help="Name of the project")
    add_parser.add_argument("code", help="Code of the project")

    # List projects command
    list_parser = subparsers.add_parser("list_projects", help="List all projects")

    # Start work command
    start_parser = subparsers.add_parser("start", help="Start working on a project")
    start_parser.add_argument("code", help="Code of the project to start working on")
    start_parser.add_argument("--time", help="Custom start time in HH:MM format", default=None)

    # Stop work command
    subparsers.add_parser("stop", help="Stop working and log the session")

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show summaries")
    summary_subparsers = summary_parser.add_subparsers(dest="summary_command", help="Summary commands")

    # Summary overall command
    summary_subparsers.add_parser("overall", help="Show summary of work hours this week")

    # Summary per project command
    summary_subparsers.add_parser("project", help="Show summary of work hours per project this week")

    args = parser.parse_args()

    if args.command == "add_project":
        add_project(args.name, args.code)
    elif args.command == "list_projects":
        list_projects()
    elif args.command == "start":
        start_work(args.code, args.time)
    elif args.command == "stop":
        stop_work()
    elif args.command == "summary":
        # Default to 'overall' if no subcommand is specified
        if args.summary_command is None or args.summary_command == "overall":
            summarize_week()
        elif args.summary_command == "project":
            summarize_project_week()
    elif args.command == "add_entry":
        add_entry(args.project_code, args.date, args.start_time, args.stop_time)


if __name__ == "__main__":
    main()
