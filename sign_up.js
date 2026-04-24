async function getFingerprintData() {
    const fp = await FingerprintJS.load();
    const result = await fp.get();

    return {
        visitorId: result.visitorId,
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screenResolution: `${screen.width}x${screen.height}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        deviceMemory: navigator.deviceMemory || "unknown",
        hardwareConcurrency: navigator.hardwareConcurrency || "unknown"
    };
}
const form = document.getElementById("register");

form.addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        // STEP 1: Register user
        const response = await fetch("/student/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log(result);

        // STEP 2: If registration successful → run fingerprint
        if (result.success) {

    const userId = result.data.user_id;
    console.log("User ID:", userId);

    const deviceData = await getFingerprintData();
    deviceData.user_id = userId;

    const deviceResponse = await fetch("/student/devices/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(deviceData)
    });

    const deviceResult = await deviceResponse.json();
    console.log(deviceResult);

    // ✅ SUCCESS CHECK FOR DEVICE SAVE
    if (deviceResult.success) {
        console.log("Device fingerprint saved successfully");

        // 🔁 Redirect to login page
         window.location.href = '/student/login';
    } else {
        console.error("Device save failed:", deviceResult.message);
    }
}
    } catch (error) {
        console.error("Error:", error);
    }
});