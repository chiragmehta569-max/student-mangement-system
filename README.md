# Student Management System

## Introduction

This beginner-friendly student manager provides a browser interface served by Python's built-in web server. Student records are saved in a CSV file and remain available after the app is restarted. The original console menu can also be run from `main.py`.

## Objective

Practice core Python by managing student records, calculating results, validating input, and saving data to a file.

## Features

- Add students with a unique roll number and marks validated from 0 to 100.
- View and search student records in a table.
- Update names and marks, or delete a record after a confirmation step.
- Calculate totals, percentage, grade, and pass/fail status automatically.
- Persist records in `students.csv`.

## Technologies Used

- Python 3 and its standard library (`csv`, `html`, `http.server`, `os`, and `urllib.parse`)
- HTML forms and CSS for the browser interface

No third-party packages, frameworks, external APIs, or databases are used.

## Python Concepts Used

- Variables and basic data types
- Input and output through console prompts and web forms
- Conditional statements and `for`/`while` loops
- Functions, lists, and dictionaries
- File handling and CSV handling
- Exception handling and input validation
- Basic HTTP request handling

## How to Run

1. Install Python 3 if it is not already installed.
2. Open a terminal in this project folder.
3. Start the website:

	```bash
	python3 web.py
	```

4. Open <http://127.0.0.1:8000> in a browser.
5. Press `Ctrl+C` in the terminal to stop the server.

The app creates `students.csv` automatically if it is missing.

To use the original console version instead, run `python3 main.py`.

## Project Structure

```text
student-management-system/
├── main.py          # CSV storage and student result calculations
├── web.py           # Local web server and browser pages
├── static/
│   └── style.css    # Website layout and styling
├── students.csv     # Student records; created automatically if missing
└── README.md        # Project overview and instructions
```

## Future Improvements

- Add sorting and filtering options.
- Export formatted result cards to a text file.
- Add more subjects or configurable grading rules.
- Add automated tests for calculations and record operations.