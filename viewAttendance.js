const params = new URLSearchParams(window.location.search);
const assignmentId = params.get("assignment_id");

window.addEventListener("DOMContentLoaded", () => {
    if (assignmentId) {
        loadSessions(assignmentId);
    }
});


// -------------------------------------
// 1. LOAD SESSIONS
// -------------------------------------
async function loadSessions(assignmentId) {
    try {
        const res = await fetch(`/staff/session/sessions/${assignmentId}`);
        const sessions = await res.json();

        const select = document.getElementById("sessionSelect");
        select.innerHTML = "";

        sessions.forEach((s, index) => {
    const option = document.createElement("option");

    option.value = s.session_id;
    option.textContent = s.session_name;

    if (index === 0) option.selected = true;

    select.appendChild(option);
});

        // 🔥 Load first session automatically
        if (sessions.length > 0) {
            loadAttendance(sessions[0].session_id);
        } else {
            document.getElementById("attendanceContainer").innerHTML =
                "<p>No sessions found for this unit.</p>";
        }

    } catch (err) {
        console.error("Error loading sessions:", err);
    }
}


// -------------------------------------
// 2. SESSION CHANGE
// -------------------------------------
document.getElementById("sessionSelect")
    .addEventListener("change", function () {
        loadAttendance(this.value);
    });


// -------------------------------------
// 3. LOAD ATTENDANCE
// -------------------------------------
async function loadAttendance(sessionId) {
    try {
        const res = await fetch(`/staff/session/attendance/${sessionId}`);
        const data = await res.json();

        const container = document.getElementById("attendanceContainer");
        container.innerHTML = "";

        // 🧠 Unit info
        if (data.length > 0) {
            document.getElementById("unitCode").textContent = data[0].unit_code;
            document.getElementById("unitName").textContent = data[0].unit_name;
        }

        // 🚀 Render students
        data.forEach((student, index) => {

            const isPresent = student.status === "present";

            const row = `
                <div class="student-row ${isPresent ? 'blue-bg' : 'purple-bg'}">

                    <span class="index">${index + 1}</span>

                    <div class="details">
                        <span class="reg-no">${student.reg_no}</span>
                        <span class="name">${student.student_name}</span>
                    </div>

                    <input 
                        type="checkbox"
                        class="attendance-checkbox"
                        data-student-id="${student.student_id}"
                        data-session-id="${student.session_id}"
                        ${isPresent ? 'checked' : ''}
                    >
                </div>
            `;

            container.innerHTML += row;
        });

        // 🔥 Attach checkbox events AFTER rendering
        attachAttendanceEvents();

    } catch (err) {
        console.error("Error loading attendance:", err);
    }
}


// -------------------------------------
// 4. MARK ATTENDANCE (NEW ADDED LOGIC)
// -------------------------------------
function attachAttendanceEvents() {
    document.querySelectorAll(".attendance-checkbox").forEach(cb => {
        cb.addEventListener("change", async function () {

            const studentId = this.dataset.studentId;
            const sessionId = this.dataset.sessionId;

            try {
                const res = await fetch("/staff/session/mark-attendance", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        student_id: studentId,
                        session_id: sessionId
                    })
                });

                const result = await res.json();
                console.log(result);

                // 🔥 refresh UI after update
                loadAttendance(sessionId);

            } catch (err) {
                console.error("Attendance update failed:", err);
            }
        });
    });
}
document.getElementById("downloadUnitReportBtn")
    .addEventListener("click", function () {

        const params = new URLSearchParams(window.location.search);
        const assignmentId = params.get("assignment_id");

        if (!assignmentId) {
            alert("Assignment ID not found in URL");
            return;
        }

        window.open(
            `/staff/session/download-unit-report/${assignmentId}`,
            "_blank"
        );
    });