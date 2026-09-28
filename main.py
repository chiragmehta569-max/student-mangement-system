import csv
import os


CSV_FILE = os.path.join(os.path.dirname(__file__), "students.csv")
FIELDNAMES = [
    "roll_number",
    "name",
    "python_marks",
    "mathematics_marks",
    "english_marks",
    "total_marks",
    "percentage",
    "grade",
]


def calculate_result(student):
    """Calculate and store total marks, percentage, and grade."""
    student["total_marks"] = (
        student["python_marks"]
        + student["mathematics_marks"]
        + student["english_marks"]
    )
    student["percentage"] = student["total_marks"] / 3

    if student["percentage"] >= 90:
        student["grade"] = "A+"
    elif student["percentage"] >= 80:
        student["grade"] = "A"
    elif student["percentage"] >= 70:
        student["grade"] = "B"
    elif student["percentage"] >= 60:
        student["grade"] = "C"
    elif student["percentage"] >= 50:
        student["grade"] = "D"
    else:
        student["grade"] = "F"


def student_passed(student):
    """Return whether the student scored at least 33 in every subject."""
    return (
        student["python_marks"] >= 33
        and student["mathematics_marks"] >= 33
        and student["english_marks"] >= 33
    )


def load_students():
    """Load valid student records from the CSV file."""
    students = []

    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != FIELDNAMES:
                print("The CSV file has an unexpected format. No records were loaded.")
                return students

            for row in reader:
                try:
                    student = {
                        "roll_number": row["roll_number"].strip(),
                        "name": row["name"].strip(),
                        "python_marks": int(row["python_marks"]),
                        "mathematics_marks": int(row["mathematics_marks"]),
                        "english_marks": int(row["english_marks"]),
                    }
                    marks = [
                        student["python_marks"],
                        student["mathematics_marks"],
                        student["english_marks"],
                    ]
                    if not student["roll_number"] or not student["name"]:
                        raise ValueError("Missing roll number or name")
                    if any(mark < 0 or mark > 100 for mark in marks):
                        raise ValueError("Marks are outside the valid range")

                    calculate_result(student)
                    students.append(student)
                except (AttributeError, KeyError, TypeError, ValueError):
                    print("A malformed student row was skipped.")
    except FileNotFoundError:
        save_students(students)
    except (OSError, csv.Error) as error:
        print(f"Could not read student records: {error}")

    return students


def save_students(students):
    """Save all student records to the CSV file."""
    try:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(students)
        return True
    except OSError as error:
        print(f"Could not save student records: {error}")
        return False


def get_marks(prompt):
    """Ask for a whole-number mark from 0 to 100."""
    while True:
        try:
            marks = int(input(prompt))
            if 0 <= marks <= 100:
                return marks
            print("Marks must be between 0 and 100.")
        except ValueError:
            print("Please enter a whole number.")


def find_student(students, roll_number):
    """Return the student with this roll number, or None if not found."""
    for student in students:
        if student["roll_number"].lower() == roll_number.lower():
            return student
    return None


def print_student(student):
    """Display all details for one student."""
    print(f"\nName: {student['name']}")
    print(f"Roll Number: {student['roll_number']}")
    print(f"Python Marks: {student['python_marks']}")
    print(f"Mathematics Marks: {student['mathematics_marks']}")
    print(f"English Marks: {student['english_marks']}")
    print(f"Total: {student['total_marks']} / 300")
    print(f"Percentage: {student['percentage']:.2f}%")
    print(f"Grade: {student['grade']}")


def add_student(students):
    """Collect and save a new student record."""
    roll_number = input("Enter roll number: ").strip()
    if not roll_number:
        print("Roll number cannot be empty.")
        return
    if find_student(students, roll_number):
        print("A student with that roll number already exists.")
        return

    name = input("Enter student name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    student = {
        "roll_number": roll_number,
        "name": name,
        "python_marks": get_marks("Enter Python marks (0-100): "),
        "mathematics_marks": get_marks("Enter Mathematics marks (0-100): "),
        "english_marks": get_marks("Enter English marks (0-100): "),
    }
    calculate_result(student)
    students.append(student)

    if save_students(students):
        print("Student added successfully.")
    else:
        students.pop()


def view_students(students):
    """Display all saved students in a table."""
    if not students:
        print("No student records found.")
        return

    print(
        f"{'Roll Number':<14} {'Name':<22} {'Python':>7} {'Maths':>7} "
        f"{'English':>7} {'Total':>7} {'Percent':>10} {'Grade':>6}"
    )
    print("-" * 87)
    for student in students:
        print(
            f"{student['roll_number']:<14} {student['name']:<22} "
            f"{student['python_marks']:>7} {student['mathematics_marks']:>7} "
            f"{student['english_marks']:>7} {student['total_marks']:>7} "
            f"{student['percentage']:>9.2f}% {student['grade']:>6}"
        )


def search_student(students):
    """Find a student by roll number and display their details."""
    roll_number = input("Enter roll number to search: ").strip()
    student = find_student(students, roll_number)
    if student:
        print_student(student)
    else:
        print("Student not found.")


def update_student(students):
    """Update a student's name and/or marks."""
    roll_number = input("Enter roll number to update: ").strip()
    student = find_student(students, roll_number)
    if not student:
        print("Student not found.")
        return

    print("Press Enter to keep the current value.")
    name = input(f"Name [{student['name']}]: ").strip()
    if name:
        student["name"] = name

    subjects = [
        ("python_marks", "Python"),
        ("mathematics_marks", "Mathematics"),
        ("english_marks", "English"),
    ]
    for field, subject in subjects:
        while True:
            value = input(f"{subject} marks [{student[field]}]: ").strip()
            if not value:
                break
            try:
                marks = int(value)
                if 0 <= marks <= 100:
                    student[field] = marks
                    break
                print("Marks must be between 0 and 100.")
            except ValueError:
                print("Please enter a whole number, or press Enter to keep the current value.")

    calculate_result(student)
    if save_students(students):
        print("Student updated successfully.")


def delete_student(students):
    """Delete a student after asking for confirmation."""
    roll_number = input("Enter roll number to delete: ").strip()
    student = find_student(students, roll_number)
    if not student:
        print("Student not found.")
        return

    confirmation = input(f"Delete {student['name']}? (y/n): ").strip().lower()
    if confirmation != "y":
        print("Deletion cancelled.")
        return

    students.remove(student)
    if save_students(students):
        print("Student deleted successfully.")
    else:
        students.append(student)


def display_student_result(students):
    """Display a student's result card and pass/fail status."""
    roll_number = input("Enter roll number for result: ").strip()
    student = find_student(students, roll_number)
    if not student:
        print("Student not found.")
        return

    print("\n========== STUDENT RESULT ==========")
    print_student(student)
    status = "PASS" if student_passed(student) else "FAIL"
    print(f"Status: {status}")
    print("===================================")


def main_menu():
    """Run the application menu until the user chooses Exit."""
    students = load_students()

    while True:
        print("\n========================================")
        print("       STUDENT MANAGEMENT SYSTEM")
        print("========================================")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Display Student Result")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()
        if choice == "1":
            add_student(students)
        elif choice == "2":
            view_students(students)
        elif choice == "3":
            search_student(students)
        elif choice == "4":
            update_student(students)
        elif choice == "5":
            delete_student(students)
        elif choice == "6":
            display_student_result(students)
        elif choice == "7":
            print("Thank you for using the Student Management System.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main_menu()