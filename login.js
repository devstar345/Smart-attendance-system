const registerBtn = document.getElementById('register-btn');
registerBtn.addEventListener('click', () => {
  window.location.href = '/student/register';
});
document.getElementById("reg_no").addEventListener("input", function() {
    this.value = this.value.toUpperCase();
});

const password = document.getElementById("password");
const toggle = document.getElementById("togglePassword");
const eyeOpen = document.getElementById("eyeOpen");
const eyeClosed = document.getElementById("eyeClosed");

toggle.addEventListener("click", () => {
    const isHidden = password.type === "password";

    password.type = isHidden ? "text" : "password";

    // switch icons
    eyeOpen.style.display = isHidden ? "none" : "block";
    eyeClosed.style.display = isHidden ? "block" : "none";
});

const form = document.getElementById("login_info");

form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        // =========================
        // STEP 1: Fingerprint
        // =========================
        const fp = await FingerprintJS.load();
        const result = await fp.get();

        const visitorId = result.visitorId;

        console.log("Visitor ID:", visitorId);

        // =========================
        // STEP 2: LOGIN REQUEST
        // =========================
        const response = await fetch("/student/login/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify({
                reg_no: data.reg_no,
                password: data.password,
                visitorId: visitorId
            })
        });

        const resultData = await response.json();

        console.log("STATUS:", response.status);
        console.log("RESPONSE:", resultData);

        // =========================
        // STEP 3: HANDLE RESPONSE
        // =========================

        // ✅ SUCCESS LOGIN
        if (response.ok && resultData.success === true) {

            window.location.href = "/student/dashboard";
        }

        // ❌ DEVICE NOT RECOGNISED
        else if (response.status === 403) {

            alert(resultData.message || "Device not recognised");

            console.log("Ask lecturer to restore device");
        }

        // ❌ OTHER ERRORS
        else {

            alert(resultData.message || "Login failed");
        }

    } catch (error) {
        console.error("Login error:", error);
        alert("Network error. Try again.");
    }
});