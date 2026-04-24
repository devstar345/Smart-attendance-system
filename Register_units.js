console.log("Register Units JS Loaded");
async function loadUnits() {
    const res = await fetch("/api/units"); // your endpoint (uses session course_id)
    const data = await res.json();

    const container = document.querySelector(".unit-list");
    container.innerHTML = "";

    data.data.forEach(unit => {
        const unitHTML = `
            <div class="unit-item">
                <div class="unit-info">
                    <span class="unit-code">${unit.unit_code}</span>
                    <span class="unit-name">${unit.name}</span>
                </div>
                <input type="checkbox" class="unit-checkbox" value="${unit.unit_id}">
            </div>
        `;

        container.innerHTML += unitHTML;
    });
}
window.addEventListener("DOMContentLoaded", async () => {
    try {
        await loadUnits();
    } catch (error) {
        console.error("Failed to load units:", error);
    }
});
function getSelectedUnits() {
    const checkboxes = document.querySelectorAll(".unit-checkbox:checked");

    return Array.from(checkboxes).map(cb => parseInt(cb.value));
}
async function registerUnits() {
    const unit_ids = getSelectedUnits();

    if (unit_ids.length === 0) {
        alert("Please select at least one unit");
        return;
    }

    try {
        const res = await fetch("/api/enroll", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                unit_ids: unit_ids
            })
        });

        const data = await res.json();

        if (data.success) {
            alert("Units registered successfully!");
            loadUnits(); // optional refresh
        } else {
            alert(data.message);
        }

    } catch (error) {
        console.error("Enrollment error:", error);
    }
}