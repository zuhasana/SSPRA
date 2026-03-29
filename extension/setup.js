document.addEventListener("DOMContentLoaded", () => {

    const step1 = document.getElementById("step1");
    const step2 = document.getElementById("step2");
    const step3 = document.getElementById("step3");

    const status = document.getElementById("status");
    const verifyBtn = document.getElementById("btn-verify");
    const progressBar = document.getElementById("fill");

    // ✅ STEP 1 → STEP 2
    document.getElementById("btn-accept").onclick = () => {
        step1.classList.remove("active");
        step2.classList.add("active");

        // Animate progress bar
        let progress = 0;
        let interval = setInterval(() => {
            progress += 20;
            progressBar.style.width = progress + "%";
            if (progress >= 100) clearInterval(interval);
        }, 400);

        // Show verify button after delay
        setTimeout(() => {
            verifyBtn.style.display = "block";
        }, 2500);
    };

    // ✅ VERIFY SERVER
    verifyBtn.onclick = () => {
        status.innerText = "Checking Privacy Engine...";

        fetch("http://127.0.0.1:8000/")
            .then(res => res.json())
            .then(() => {
                status.innerText = "✅ Connected successfully!";

                step2.classList.remove("active");
                step3.classList.add("active");
            })
            .catch(() => {
                status.innerText = "❌ Privacy Engine not running. Please start it and try again.";
            });
    };

    // ✅ FINISH SETUP
    document.getElementById("btn-finish").onclick = () => {
    const key = document.getElementById("groq-key").value.trim();

    if (!key.startsWith("gsk_")) {
        alert("Enter valid Groq API Key");
        return;
    }

    chrome.storage.local.set({
        groq_api_key: key,
        setup_done: true,
        devMode: false
    }, () => {
        console.log("SETUP SAVED ✅");

        alert("Setup complete! Now refresh page.");

        window.close();
    });
};

});
document.getElementById("download-btn").onclick = () => {
    window.open("https://drive.google.com/file/d/1cS-6zQUtDHVyV6z4YgHiJGyV6zW7zn8L/view?usp=sharing");
};
document.getElementById("btn-later").onclick = () => {
    window.close();
};