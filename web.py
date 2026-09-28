from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
import os
from urllib.parse import parse_qs, quote, urlsplit

from main import calculate_result, find_student, load_students, save_students, student_passed


HOST = "127.0.0.1"
PORT = 8000
PROJECT_FOLDER = os.path.dirname(__file__)
STYLESHEET = os.path.join(PROJECT_FOLDER, "static", "style.css")
MAX_FORM_SIZE = 1_000_000


def safe(value):
    """Escape text before placing it in an HTML page."""
    return escape(str(value), quote=True)


def page_start(title):
    """Return the shared HTML header and open the page body."""
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{safe(title)} | Student Management</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <header class="topbar">
        <a class="brand" href="/" aria-label="Student Management home">
            <span class="brand-mark">S</span>
            <span>STUDENT RECORDS</span>
        </a>
        <span class="topbar-note">ACADEMIC OFFICE <span class="live-dot"></span> LOCAL</span>
    </header>
    <main class="page-shell">
"""


def page_end():
    """Close the shared HTML page."""
    return """    </main>
    <footer class="footer">Student Management System <span>·</span> Python + CSV</footer>
</body>
</html>
"""


def render_result_card(student):
    """Build a compact result card for the selected student."""
    status = "PASS" if student_passed(student) else "FAIL"
    status_class = "pass" if status == "PASS" else "fail"
    roll = quote(student["roll_number"], safe="")
    return f"""
    <section class="result-panel" aria-labelledby="result-title">
        <div class="result-heading">
            <div>
                <span class="eyebrow">STUDENT RESULT</span>
                <h2 id="result-title">{safe(student['name'])}</h2>
            </div>
            <a class="close-link" href="/" aria-label="Close result">Close</a>
        </div>
        <div class="result-details">
            <div><span>Roll number</span><strong>{safe(student['roll_number'])}</strong></div>
            <div><span>Python</span><strong>{student['python_marks']} / 100</strong></div>
            <div><span>Mathematics</span><strong>{student['mathematics_marks']} / 100</strong></div>
            <div><span>English</span><strong>{student['english_marks']} / 100</strong></div>
            <div><span>Total</span><strong>{student['total_marks']} / 300</strong></div>
            <div><span>Percentage</span><strong>{student['percentage']:.2f}%</strong></div>
            <div><span>Grade</span><strong>{safe(student['grade'])}</strong></div>
            <div><span>Result</span><strong class="status {status_class}">{status}</strong></div>
        </div>
    </section>
"""


def render_student_row(student, selected_roll=""):
    """Build one row in the student table."""
    status = "PASS" if student_passed(student) else "FAIL"
    status_class = "pass" if status == "PASS" else "fail"
    roll = quote(student["roll_number"], safe="")
    selected_class = "selected-row" if student["roll_number"] == selected_roll else ""
    return f"""
    <tr class="{selected_class}">
        <td><span class="roll-value">{safe(student['roll_number'])}</span></td>
        <td class="name-cell">{safe(student['name'])}</td>
        <td>{student['python_marks']}</td>
        <td>{student['mathematics_marks']}</td>
        <td>{student['english_marks']}</td>
        <td>{student['total_marks']}</td>
        <td>{student['percentage']:.1f}%</td>
        <td><span class="grade-pill">{safe(student['grade'])}</span></td>
        <td><span class="status {status_class}">{status}</span></td>
        <td class="actions-cell">
            <a class="action-link" href="/?result={roll}">Result</a>
            <a class="action-link" href="/?edit={roll}">Edit</a>
            <form class="inline-form" method="post" action="/students/delete">
                <input type="hidden" name="roll_number" value="{safe(student['roll_number'])}">
                <button class="action-link delete-link" type="submit">Delete</button>
            </form>
        </td>
    </tr>
"""


def render_student_form(student=None, error=""):
    """Build the add-student or edit-student form."""
    editing = student is not None
    action = "/students/update" if editing else "/students/add"
    title = "Update student" if editing else "Add a student"
    button = "Save changes" if editing else "Add student"
    roll_number = student["roll_number"] if editing else ""
    name = student["name"] if editing else ""
    python_marks = student["python_marks"] if editing else ""
    mathematics_marks = student["mathematics_marks"] if editing else ""
    english_marks = student["english_marks"] if editing else ""
    roll_control = (
        f'<input type="hidden" name="old_roll_number" value="{safe(roll_number)}">'
        f'<input id="roll-number" name="roll_number" value="{safe(roll_number)}" readonly>'
        if editing
        else '<input id="roll-number" name="roll_number" required maxlength="40" autocomplete="off">'
    )
    cancel_link = '<a class="cancel-link" href="/">Cancel edit</a>' if editing else ""
    error_notice = f'<p class="form-error">{safe(error)}</p>' if error else ""

    return f"""
    <section class="form-panel" aria-labelledby="form-title">
        <div class="section-heading">
            <div>
                <span class="eyebrow">RECORD ENTRY</span>
                <h2 id="form-title">{title}</h2>
            </div>
            <span class="section-index">01</span>
        </div>
        {error_notice}
        <form method="post" action="{action}" class="student-form">
            <label for="roll-number">Roll number</label>
            {roll_control}
            <label for="student-name">Student name</label>
            <input id="student-name" name="name" value="{safe(name)}" required maxlength="100" autocomplete="name">
            <div class="marks-label-row">
                <label for="python-marks">Subject marks</label>
                <span>OUT OF 100</span>
            </div>
            <div class="marks-grid">
                <label for="python-marks">Python</label>
                <label for="mathematics-marks">Mathematics</label>
                <label for="english-marks">English</label>
                <input id="python-marks" name="python_marks" type="number" min="0" max="100" value="{python_marks}" required>
                <input id="mathematics-marks" name="mathematics_marks" type="number" min="0" max="100" value="{mathematics_marks}" required>
                <input id="english-marks" name="english_marks" type="number" min="0" max="100" value="{english_marks}" required>
            </div>
            <button class="primary-button" type="submit">{button}<span aria-hidden="true">↗</span></button>
            {cancel_link}
        </form>
    </section>
"""


def render_page(students, visible_students, query, edit_student, selected_result, message):
    """Render the student dashboard and all its current records."""
    count = len(students)
    average = sum(student["percentage"] for student in students) / count if count else 0
    passed_count = sum(1 for student in students if student_passed(student))
    failed_count = count - passed_count
    selected_student = edit_student or selected_result
    selected_roll = selected_student["roll_number"] if selected_student else ""
    rows = "".join(
        render_student_row(student, selected_roll) for student in visible_students
    )
    if not rows:
        empty_title = "No students match this search" if query else "No student records yet"
        rows = f'<tr><td colspan="10" class="empty-cell">{empty_title}</td></tr>'
    message_html = f'<div class="notice">{safe(message)}</div>' if message else ""
    result_html = render_result_card(selected_result) if selected_result else ""
    form_html = render_student_form(edit_student)
    search_value = safe(query)
    search_label = f"{len(visible_students)} shown" if query else f"{count} total"

    return page_start("Student records") + f"""
    <section class="page-heading">
        <div>
            <span class="eyebrow">STUDENT MANAGEMENT SYSTEM <span class="heading-rule"></span> ACADEMIC REGISTER</span>
            <h1>Student records<span class="period">.</span></h1>
            <p class="page-summary">Marks, results, and class progress in one place.</p>
        </div>
        <div class="heading-count"><strong>{count:02d}</strong><span>ENROLLED</span></div>
    </section>
    {message_html}
    {result_html}
    <section class="metric-strip" aria-label="Student summary">
        <div class="metric metric-primary"><span class="metric-label">TOTAL STUDENTS</span><strong>{count:02d}</strong><span class="metric-note">active records</span></div>
        <div class="metric"><span class="metric-label">CLASS AVERAGE</span><strong>{average:.1f}<small>%</small></strong><span class="metric-note">across all subjects</span></div>
        <div class="metric"><span class="metric-label">PASSING</span><strong>{passed_count:02d}</strong><span class="metric-note">all subjects ≥ 33</span></div>
        <div class="metric metric-alert"><span class="metric-label">NEEDS ATTENTION</span><strong>{failed_count:02d}</strong><span class="metric-note">below 33 in a subject</span></div>
    </section>
    <div class="workspace-grid">
        <aside class="form-column">{form_html}</aside>
        <section class="records-section" aria-labelledby="records-title">
            <div class="records-heading">
                <div>
                    <span class="eyebrow">ROSTER</span>
                    <h2 id="records-title">All students <span class="record-count">{search_label}</span></h2>
                </div>
                <form class="search-form" method="get" action="/">
                    <label class="visually-hidden" for="student-search">Search by name or roll number</label>
                    <input id="student-search" type="search" name="q" value="{search_value}" placeholder="Search students...">
                    <button type="submit" aria-label="Search students">Search</button>
                    {f'<a class="clear-search" href="/" aria-label="Clear search">Clear</a>' if query else ''}
                </form>
            </div>
            <div class="table-wrap">
                <table>
                    <thead><tr>
                        <th>ROLL NO.</th><th>STUDENT</th><th>PYTHON</th><th>MATHS</th>
                        <th>ENGLISH</th><th>TOTAL</th><th>PERCENT</th><th>GRADE</th>
                        <th>STATUS</th><th>ACTIONS</th>
                    </tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
            <div class="table-footer"><span>SUBJECTS: PYTHON · MATHEMATICS · ENGLISH</span><span>GRADING SCALE: A+ TO F</span></div>
        </section>
    </div>
""" + page_end()


def render_delete_confirmation(student):
    """Ask for a second confirmation before removing a record."""
    return page_start("Confirm deletion") + f"""
    <section class="confirm-panel">
        <span class="eyebrow">DELETE RECORD</span>
        <h1>Remove this student<span class="period">?</span></h1>
        <p><strong>{safe(student['name'])}</strong> <span class="confirm-roll">({safe(student['roll_number'])})</span></p>
        <p class="confirm-copy">This student record will be removed from the CSV file.</p>
        <div class="confirm-actions">
            <form method="post" action="/students/confirm-delete">
                <input type="hidden" name="roll_number" value="{safe(student['roll_number'])}">
                <button class="danger-button" type="submit">Confirm delete</button>
            </form>
            <a class="cancel-link" href="/">Keep student</a>
        </div>
    </section>
""" + page_end()


class StudentHandler(BaseHTTPRequestHandler):
    """Handle browser page requests and student form submissions."""

    def do_GET(self):
        parsed_url = urlsplit(self.path)
        if parsed_url.path == "/style.css":
            self.serve_stylesheet()
            return
        if parsed_url.path != "/":
            self.send_error(404, "Page not found")
            return

        query_values = parse_qs(parsed_url.query)
        students = load_students()
        search_term = query_values.get("q", [""])[0].strip()
        search_lower = search_term.casefold()
        visible_students = [
            student for student in students
            if search_lower in student["name"].casefold()
            or search_lower in student["roll_number"].casefold()
        ]
        edit_student = find_student(students, query_values.get("edit", [""])[0])
        selected_result = find_student(students, query_values.get("result", [""])[0])
        message = query_values.get("message", [""])[0]
        page = render_page(
            students, visible_students, search_term, edit_student, selected_result, message
        )
        self.send_html(page)

    def do_POST(self):
        form = self.read_form()
        if form is None:
            return

        if self.path == "/students/add":
            self.add_student(form)
        elif self.path == "/students/update":
            self.update_student(form)
        elif self.path == "/students/delete":
            self.start_delete(form)
        elif self.path == "/students/confirm-delete":
            self.confirm_delete(form)
        else:
            self.send_error(404, "Page not found")

    def read_form(self):
        """Parse a small URL-encoded browser form safely."""
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length < 0 or content_length > MAX_FORM_SIZE:
                self.send_error(413, "Form is too large")
                return None
            body = self.rfile.read(content_length).decode("utf-8")
            return parse_qs(body, keep_blank_values=True)
        except (UnicodeDecodeError, ValueError):
            self.send_error(400, "Invalid form data")
            return None

    @staticmethod
    def form_value(form, key):
        """Return one trimmed field from a parsed browser form."""
        return form.get(key, [""])[0].strip()

    def redirect(self, message):
        """Return to the dashboard with a short status message."""
        destination = "/?message=" + quote(message, safe="")
        self.send_response(303)
        self.send_header("Location", destination)
        self.end_headers()

    def send_html(self, page, status=200):
        """Send a complete HTML page to the browser."""
        content = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def serve_stylesheet(self):
        """Send the local CSS stylesheet."""
        try:
            with open(STYLESHEET, "rb") as file:
                content = file.read()
        except OSError:
            self.send_error(404, "Stylesheet not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/css; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    @staticmethod
    def read_marks(form):
        """Validate and return the three subject marks from a form."""
        marks = {}
        for field in ("python_marks", "mathematics_marks", "english_marks"):
            value = form.get(field, [""])[0].strip()
            try:
                mark = int(value)
            except ValueError:
                raise ValueError("Enter a whole number for every subject mark.")
            if not 0 <= mark <= 100:
                raise ValueError("Subject marks must be between 0 and 100.")
            marks[field] = mark
        return marks

    def add_student(self, form):
        """Validate and save a new student record."""
        roll_number = self.form_value(form, "roll_number")
        name = self.form_value(form, "name")
        students = load_students()
        if not roll_number or not name:
            self.redirect("Roll number and student name are required.")
            return
        if find_student(students, roll_number):
            self.redirect("That roll number is already in use.")
            return

        try:
            student = {"roll_number": roll_number, "name": name}
            student.update(self.read_marks(form))
        except ValueError as error:
            self.redirect(str(error))
            return
        calculate_result(student)
        students.append(student)
        if save_students(students):
            self.redirect("Student added successfully.")
        else:
            self.redirect("Could not save the student record.")

    def update_student(self, form):
        """Validate and save changes to an existing student."""
        old_roll_number = self.form_value(form, "old_roll_number")
        students = load_students()
        student = find_student(students, old_roll_number)
        if not student:
            self.redirect("Student not found.")
            return

        name = self.form_value(form, "name")
        if not name:
            self.redirect("Student name is required.")
            return
        try:
            marks = self.read_marks(form)
        except ValueError as error:
            self.redirect(str(error))
            return

        previous_values = student.copy()
        student["name"] = name
        student.update(marks)
        calculate_result(student)
        if save_students(students):
            self.redirect("Student updated successfully.")
        else:
            student.update(previous_values)
            self.redirect("Could not save the student changes.")

    def start_delete(self, form):
        """Show a confirmation page before deleting a student."""
        students = load_students()
        student = find_student(students, self.form_value(form, "roll_number"))
        if not student:
            self.redirect("Student not found.")
            return
        self.send_html(render_delete_confirmation(student))

    def confirm_delete(self, form):
        """Delete a student only after the confirmation form is submitted."""
        students = load_students()
        student = find_student(students, self.form_value(form, "roll_number"))
        if not student:
            self.redirect("Student not found.")
            return

        original_index = students.index(student)
        students.pop(original_index)
        if save_students(students):
            self.redirect("Student deleted successfully.")
        else:
            students.insert(original_index, student)
            self.redirect("Could not delete the student record.")


def run_server():
    """Start the local Student Management website."""
    try:
        server = ThreadingHTTPServer((HOST, PORT), StudentHandler)
    except OSError:
        server = ThreadingHTTPServer((HOST, 0), StudentHandler)
    server_port = server.server_address[1]
    print(f"Student Management System is running at http://{HOST}:{server_port}")
    print("Press Ctrl+C to stop the website.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWebsite stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()