import yaml
import csv
import datetime
import argparse
import os
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
                start_time = datetime.datetime.combine(
                    datetime.date.today(), datetime.datetime.strptime(custom_start, "%H:%M").time()
                )
            except ValueError:
                print("Invalid time format. Please use HH:MM.")
                return
        else:
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
        print(f"Stopped work on '{session['project']['name']}' at {end_time.strftime('%H:%M:%S')}. Entry logged.")
        with open(SESSION_FILE, "w") as file:
            yaml.dump({}, file)  # Clear the session
    else:
        print("No session to stop.")


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


def summarize(period="this_week"):
    try:
        with open(LOG_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            entries = list(reader)
    except FileNotFoundError:
        print("No log file found. No hours to summarize.")
        return

    today = datetime.date.today()
    regular_hours_per_day = 7.5

    if period == "this_week":
        start_date = today - datetime.timedelta(days=today.weekday())  # Monday of this week
        end_date = today
        header = "Summary for This Week"
    elif period == "last_week":
        start_date = today - datetime.timedelta(days=today.weekday() + 7)  # Monday of last week
        end_date = start_date + datetime.timedelta(days=6)  # Sunday of last week
        header = "Summary for Last Week"
    elif period == "this_month":
        start_date = today.replace(day=1)  # First day of this month
        end_date = today
        header = "Summary for This Month"
    elif period == "last_month":
        first_day_of_this_month = today.replace(day=1)
        last_month_end = first_day_of_this_month - datetime.timedelta(days=1)
        start_date = last_month_end.replace(day=1)  # First day of last month
        end_date = last_month_end  # Last day of last month
        header = "Summary for Last Month"
    elif period == "this_year":
        start_date = today.replace(month=1, day=1)  # First day of this year
        end_date = today
        header = "Summary for This Year"
        print(header)  # Print header

        # Special handling for yearly summary
        while start_date <= end_date:
            week_end = start_date + datetime.timedelta(days=6)  # End of the week (Sunday)
            week_summary = defaultdict(float)
            print(f"Week {start_date.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")

            for entry in entries:
                entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
                if start_date <= entry_date <= week_end:
                    start_time = datetime.datetime.combine(
                        entry_date, datetime.datetime.strptime(entry["start_time"], "%H:%M:%S").time()
                    )
                    end_time = datetime.datetime.combine(
                        entry_date, datetime.datetime.strptime(entry["end_time"], "%H:%M:%S").time()
                    )
                    duration = (end_time - start_time).total_seconds() / 3600  # Convert seconds to hours
                    week_summary[entry_date] += duration

            # Ensure all weekdays are considered
            current_date = start_date
            while current_date <= week_end:
                if current_date.weekday() < 5:  # Monday to Friday
                    if current_date not in week_summary:
                        week_summary[current_date] = 0.0
                current_date += datetime.timedelta(days=1)

            for day, hours in sorted(week_summary.items()):
                print(f"{day.strftime('%A')}: {hours:.2f} hours")

            start_date = week_end + datetime.timedelta(days=1)  # Move to next Monday
        return
    else:
        print("Invalid period specified.")
        return

    week_summary = defaultdict(float)
    print(header)  # Print header

    for entry in entries:
        entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if start_date <= entry_date <= end_date:
            start_time = datetime.datetime.combine(
                entry_date, datetime.datetime.strptime(entry["start_time"], "%H:%M:%S").time()
            )
            end_time = datetime.datetime.combine(
                entry_date, datetime.datetime.strptime(entry["end_time"], "%H:%M:%S").time()
            )
            duration = (end_time - start_time).total_seconds() / 3600  # Convert seconds to hours
            week_summary[entry_date] += duration

    # Ensure all weekdays are considered
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday
            if current_date not in week_summary:
                week_summary[current_date] = 0.0
        current_date += datetime.timedelta(days=1)

    total_hours = sum(week_summary.values())
    expected_hours = regular_hours_per_day * sum(1 for d in week_summary if d.weekday() < 5)
    time_buffer = total_hours - expected_hours

    for day, hours in sorted(week_summary.items()):
        print(f"{day.strftime('%A')}: {hours:.2f} hours")

    print(f"Total Hours Worked: {total_hours:.2f} hours")
    print(f"Expected Hours: {expected_hours:.2f} hours")
    print(f"Time Buffer: {time_buffer:.2f} hours")


def summarize_project(period="this_week"):
    try:
        with open(LOG_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            entries = list(reader)
    except FileNotFoundError:
        print("No log file found. No hours to summarize.")
        return

    today = datetime.date.today()

    if period == "this_week":
        start_date = today - datetime.timedelta(days=today.weekday())  # Monday of this week
        end_date = today
        header = "Project Summary for This Week"
    elif period == "last_week":
        start_date = today - datetime.timedelta(days=today.weekday() + 7)  # Monday of last week
        end_date = start_date + datetime.timedelta(days=6)  # Sunday of last week
        header = "Project Summary for Last Week"
    elif period == "this_month":
        start_date = today.replace(day=1)  # First day of this month
        end_date = today
        header = "Project Summary for This Month"
    elif period == "last_month":
        first_day_of_this_month = today.replace(day=1)
        last_month_end = first_day_of_this_month - datetime.timedelta(days=1)
        start_date = last_month_end.replace(day=1)  # First day of last month
        end_date = last_month_end  # Last day of last month
        header = "Project Summary for Last Month"
    elif period == "this_year":
        start_date = datetime.date(today.year, 1, 1)  # Start of this year
        end_date = today
        header = "Project Summary for This Year"
        print(header)  # Print header

        project_summary = defaultdict(float)

        for entry in entries:
            entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
            if start_date <= entry_date <= end_date:
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
        return
    else:
        print("Invalid period specified.")
        return

    project_summary = defaultdict(float)
    print(header)  # Print header

    for entry in entries:
        entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if start_date <= entry_date <= end_date:
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


def show_entries_today():
    try:
        with open(LOG_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            entries = list(reader)
    except FileNotFoundError:
        print("No log file found. No entries to show.")
        return

    today = datetime.date.today()
    today_entries = []
    total_hours_today = 0.0

    for entry in entries:
        entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if entry_date == today:
            start_time = datetime.datetime.strptime(entry["start_time"], "%H:%M:%S")
            end_time = datetime.datetime.strptime(entry["end_time"], "%H:%M:%S")
            duration = (end_time - start_time).total_seconds() / 3600  # Convert seconds to hours
            total_hours_today += duration
            entry_info = {
                "start_time": start_time,
                "end_time": end_time,
                "project_name": entry["project_name"],
                "project_code": entry["project_code"],
                "duration": duration,
            }
            today_entries.append(entry_info)

    today_entries.sort(key=lambda x: x["start_time"])  # Sort by start time

    print(f"Entries for Today ({today.strftime('%Y-%m-%d')}):")
    for entry in today_entries:
        print(
            f"Project {entry['project_code']} - {entry['project_name']}: "
            f"{entry['start_time'].strftime('%H:%M:%S')} to {entry['end_time'].strftime('%H:%M:%S')} - "
            f"{entry['duration']:.2f} hours"
        )

    print(f"Total Hours Worked Today: {total_hours_today:.2f} hours")


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
    overall_parser = summary_subparsers.add_parser("overall", help="Show summary of work hours for a specified period")
    overall_parser.add_argument(
        "period",
        nargs="?",
        default="this_week",
        choices=["this_week", "last_week", "this_month", "last_month", "this_year", "today"],
        help="Period to summarize",
    )

    # Summary per project command
    project_parser = summary_subparsers.add_parser(
        "project", help="Show summary of work hours per project for a specified period"
    )
    project_parser.add_argument(
        "period",
        nargs="?",
        default="this_week",
        choices=["this_week", "last_week", "this_month", "last_month", "this_year"],
        help="Period to summarize",
    )

    # Add entry command
    entry_parser = subparsers.add_parser("add_entry", help="Add a manual entry to the log")
    entry_parser.add_argument("project_code", help="Code of the project")
    entry_parser.add_argument("date", help="Date of the entry in dd:mm format")
    entry_parser.add_argument("start_time", help="Start time in HH:MM format")
    entry_parser.add_argument("stop_time", help="Stop time in HH:MM format")

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
        period = args.period if args.period else "this_week"
        if args.summary_command == "overall":
            if period == "today":
                show_entries_today()
            else:
                summarize(period)
    elif args.command == "add_entry":
        add_entry(args.project_code, args.date, args.start_time, args.stop_time)


if __name__ == "__main__":
    main()
