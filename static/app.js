const STORAGE_KEY = "student-management-records-v1";
const form = document.querySelector("#student-form");
const searchForm = document.querySelector("#search-form");
const searchInput = document.querySelector("#student-search");
const rows = document.querySelector("#student-rows");
const notice = document.querySelector("#notice");
const resultPanel = document.querySelector("#result-panel");
let students = loadStudents();
let editingRollNumber = "";
let selectedRollNumber = "";
let noticeTimer;

function calculateResult(student) {
    student.total_marks =
        student.python_marks + student.mathematics_marks + student.english_marks;
    student.percentage = student.total_marks / 3;

    if (student.percentage >= 90) {
        student.grade = "A+";
    } else if (student.percentage >= 80) {
        student.grade = "A";
    } else if (student.percentage >= 70) {
        student.grade = "B";
    } else if (student.percentage >= 60) {
        student.grade = "C";
    } else if (student.percentage >= 50) {
        student.grade = "D";
    } else {
        student.grade = "F";
    }

    return student;
}

function studentPassed(student) {
    return student.python_marks >= 33
        && student.mathematics_marks >= 33
        && student.english_marks >= 33;
}

function loadStudents() {
    try {
        const savedStudents = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
        if (!Array.isArray(savedStudents)) {
            return [];
        }

        return savedStudents.filter((student) => {
            return student
                && typeof student.roll_number === "string"
                && typeof student.name === "string"
                && [student.python_marks, student.mathematics_marks, student.english_marks]
                    .every((mark) => Number.isInteger(mark) && mark >= 0 && mark <= 100);
        }).map(calculateResult);
    } catch (error) {
        return [];
    }
}

function saveStudents() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(students));
        return true;
    } catch (error) {
        showNotice("Could not save records in this browser. Check available storage.");
        return false;
    }
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (character) => {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        };
        return entities[character];
    });
}

function showNotice(message) {
    clearTimeout(noticeTimer);
    notice.textContent = message;
    notice.hidden = false;
    noticeTimer = setTimeout(() => {
        notice.hidden = true;
    }, 4500);
}

function findStudent(rollNumber) {
    const normalizedRollNumber = rollNumber.trim().toLocaleLowerCase();
    return students.find((student) => {
        return student.roll_number.toLocaleLowerCase() === normalizedRollNumber;
    });
}

function renderRow(student) {
    const safeRoll = escapeHtml(student.roll_number);
    const safeName = escapeHtml(student.name);
    const status = studentPassed(student) ? "PASS" : "FAIL";
    const statusClass = status === "PASS" ? "pass" : "fail";
    const selectedClass = student.roll_number === selectedRollNumber ? "selected-row" : "";

    return `
        <tr class="${selectedClass}">
            <td><span class="roll-value">${safeRoll}</span></td>
            <td class="name-cell">${safeName}</td>
            <td>${student.python_marks}</td>
            <td>${student.mathematics_marks}</td>
            <td>${student.english_marks}</td>
            <td>${student.total_marks}</td>
            <td>${student.percentage.toFixed(1)}%</td>
            <td><span class="grade-pill">${student.grade}</span></td>
            <td><span class="status ${statusClass}">${status}</span></td>
            <td class="actions-cell">
                <button class="action-link" type="button" data-action="result" data-roll="${safeRoll}">Result</button>
                <button class="action-link" type="button" data-action="edit" data-roll="${safeRoll}">Edit</button>
                <button class="action-link delete-link" type="button" data-action="delete" data-roll="${safeRoll}">Delete</button>
            </td>
        </tr>
    `;
}

function renderResult(student) {
    const status = studentPassed(student) ? "PASS" : "FAIL";
    const statusClass = status === "PASS" ? "pass" : "fail";
    const details = [
        ["Roll number", escapeHtml(student.roll_number)],
        ["Python", `${student.python_marks} / 100`],
        ["Mathematics", `${student.mathematics_marks} / 100`],
        ["English", `${student.english_marks} / 100`],
        ["Total", `${student.total_marks} / 300`],
        ["Percentage", `${student.percentage.toFixed(2)}%`],
        ["Grade", student.grade],
        ["Result", `<span class="status ${statusClass}">${status}</span>`],
    ];

    document.querySelector("#result-title").textContent = student.name;
    document.querySelector("#result-details").innerHTML = details.map(([label, value]) => {
        return `<div><span>${label}</span><strong>${value}</strong></div>`;
    }).join("");
    resultPanel.hidden = false;
}

function render() {
    const searchTerm = searchInput.value.trim().toLocaleLowerCase();
    const visibleStudents = students.filter((student) => {
        return student.name.toLocaleLowerCase().includes(searchTerm)
            || student.roll_number.toLocaleLowerCase().includes(searchTerm);
    });
    const totalCount = students.length;
    const passingCount = students.filter(studentPassed).length;
    const average = totalCount
        ? students.reduce((sum, student) => sum + student.percentage, 0) / totalCount
        : 0;

    document.querySelector("#heading-count").textContent = String(totalCount).padStart(2, "0");
    document.querySelector("#total-count").textContent = String(totalCount).padStart(2, "0");
    document.querySelector("#average-score").textContent = average.toFixed(1);
    document.querySelector("#passing-count").textContent = String(passingCount).padStart(2, "0");
    document.querySelector("#failing-count").textContent = String(totalCount - passingCount).padStart(2, "0");
    document.querySelector("#record-count").textContent = searchTerm
        ? `${visibleStudents.length} shown`
        : `${totalCount} total`;
    document.querySelector("#clear-search").hidden = !searchTerm;

    if (visibleStudents.length) {
        rows.innerHTML = visibleStudents.map(renderRow).join("");
    } else {
        const emptyMessage = searchTerm ? "No students match this search" : "No student records yet";
        rows.innerHTML = `<tr><td colspan="10" class="empty-cell">${emptyMessage}</td></tr>`;
    }
}

function clearForm() {
    form.reset();
    editingRollNumber = "";
    document.querySelector("#roll-number").readOnly = false;
    document.querySelector("#form-title").textContent = "Add a student";
    document.querySelector("#submit-student").innerHTML = 'Add student<span aria-hidden="true">↗</span>';
    document.querySelector("#cancel-edit").hidden = true;
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.reportValidity()) {
        return;
    }

    const rollNumber = form.elements.roll_number.value.trim();
    const name = form.elements.name.value.trim();
    const marks = {
        python_marks: form.elements.python_marks.valueAsNumber,
        mathematics_marks: form.elements.mathematics_marks.valueAsNumber,
        english_marks: form.elements.english_marks.valueAsNumber,
    };
    if (!rollNumber || !name || Object.values(marks).some((mark) => {
        return !Number.isInteger(mark) || mark < 0 || mark > 100;
    })) {
        showNotice("Enter a name, roll number, and whole-number marks from 0 to 100.");
        return;
    }

    const duplicate = findStudent(rollNumber);
    if (!editingRollNumber && duplicate) {
        showNotice("That roll number is already in use.");
        return;
    }

    const updatedStudent = calculateResult({ roll_number: rollNumber, name, ...marks });
    if (editingRollNumber) {
        const index = students.findIndex((student) => student.roll_number === editingRollNumber);
        if (index !== -1) {
            students[index] = updatedStudent;
        }
        selectedRollNumber = rollNumber;
        showNotice("Student updated successfully.");
    } else {
        students.push(updatedStudent);
        selectedRollNumber = rollNumber;
        showNotice("Student added successfully.");
    }

    if (!saveStudents()) {
        students = loadStudents();
        return;
    }
    clearForm();
    render();
});

rows.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) {
        return;
    }

    const student = findStudent(button.dataset.roll);
    if (!student) {
        showNotice("Student not found.");
        return;
    }

    if (button.dataset.action === "result") {
        selectedRollNumber = student.roll_number;
        render();
        renderResult(student);
        resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else if (button.dataset.action === "edit") {
        editingRollNumber = student.roll_number;
        form.elements.roll_number.value = student.roll_number;
        form.elements.name.value = student.name;
        form.elements.python_marks.value = student.python_marks;
        form.elements.mathematics_marks.value = student.mathematics_marks;
        form.elements.english_marks.value = student.english_marks;
        form.elements.roll_number.readOnly = true;
        document.querySelector("#form-title").textContent = "Update student";
        document.querySelector("#submit-student").innerHTML = 'Save changes<span aria-hidden="true">↗</span>';
        document.querySelector("#cancel-edit").hidden = false;
        selectedRollNumber = student.roll_number;
        render();
        form.scrollIntoView({ behavior: "smooth", block: "center" });
        form.elements.name.focus();
    } else if (button.dataset.action === "delete") {
        if (!window.confirm(`Delete ${student.name} (${student.roll_number})?`)) {
            return;
        }
        students = students.filter((record) => record.roll_number !== student.roll_number);
        if (saveStudents()) {
            selectedRollNumber = "";
            resultPanel.hidden = true;
            if (editingRollNumber === student.roll_number) {
                clearForm();
            }
            render();
            showNotice("Student deleted successfully.");
        }
    }
});

searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    render();
});

searchInput.addEventListener("input", render);
document.querySelector("#clear-search").addEventListener("click", () => {
    searchInput.value = "";
    render();
    searchInput.focus();
});
document.querySelector("#cancel-edit").addEventListener("click", clearForm);
document.querySelector("#close-result").addEventListener("click", () => {
    resultPanel.hidden = true;
    selectedRollNumber = "";
    render();
});

render();