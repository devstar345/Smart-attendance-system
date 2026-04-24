function toggleMenu() {
            document.getElementById('sidebar').classList.toggle('active');
        }
function togleMenu() {
        const submenu = document.getElementById("submenu");
        const arrow = document.getElementById("arrow");

        if (submenu.style.display === "block") {
            submenu.style.display = "none";
            arrow.classList.remove("rotate");
        } else {
            submenu.style.display = "block";
            arrow.classList.add("rotate");
        }
    }
async function loadActiveLessons() {
    try {
        const res = await fetch('http://127.0.0.1:5000/student/active-lessons');
        const data = await res.json();

        const container = document.querySelector(".card.active-lessons-card");

        if (data.error) {
            container.innerHTML = `<p>${data.error}</p>`;
            return;
        }

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="no-lesson">
                    <h3>No active lesson</h3>
                    <p>Please wait for your lecturer to start a session.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = data.map(lesson => `
            
                <h2>Active lesson</h2>
                <h3>${lesson.unit_name}</h3>
                <p class="lesson-detail">Lecturer: ${lesson.lecturer_name}</p>
                <p class="lesson-status">Attendance: Open</p>
                <a href="/student/markAttendance?session_id=${lesson.session_id}" class="btn primary">
                    Mark Attendance
                </a>
            
        `).join("");

    } catch (err) {
        console.error(err);
    }
}

loadActiveLessons();
setInterval(loadActiveLessons, 5000);

async function loadStudentUnits() {
    try {
        const res = await fetch("/student/my-units");
        const units = await res.json();

        const container = document.querySelector(".units-card");

        // Keep title
        container.innerHTML = `
            <div class="card-title-row">
                <h2>My Units</h2>
            </div>
        `;

        units.forEach((unit, index) => {

            let rowClass = "unit-row";
            if (index === units.length - 1) {
                rowClass += " last-row";
            }

            // 🎨 color logic
            let color = "#55c061";
            if (unit.percentage < 50) color = "#ff4d4d";
            else if (unit.percentage < 75) color = "#ffa500";

            const row = `
                <div class="${rowClass}">
                    
                    <span>${unit.unit_name}</span>

                    <!-- 🔥 Circular Progress -->
                    <div class="progress-circle" 
                         data-percent="${unit.percentage}" 
                         style="--color:${color}">
                        <span>${unit.percentage}%</span>
                    </div>

                </div>
            `;

            container.innerHTML += row;
        });

        applyProgressCircles();

    } catch (err) {
        console.error("Error loading units:", err);
    }
}

window.addEventListener("DOMContentLoaded", loadStudentUnits);

function applyProgressCircles() {
    document.querySelectorAll(".progress-circle").forEach(circle => {
        const percent = circle.getAttribute("data-percent") || 0;
        circle.style.setProperty("--progress", percent + "%");
    });
}