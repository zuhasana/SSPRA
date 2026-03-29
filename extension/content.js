let selectedText = "";
let localVault = {};
let maskedData = "";

document.addEventListener("mouseup", (e) => {
    const t = window.getSelection().toString().trim();
    if (t.length > 5) {
        selectedText = t;
        renderShieldIcon(e.pageX, e.pageY);
    }
});

function renderShieldIcon(x, y) {
    let icon = document.getElementById("s-icon") || document.createElement("div");
    icon.id = "s-icon";
    icon.innerHTML = "🛡️";
    icon.style.left = `${x + 5}px`;
    icon.style.top = `${y + 5}px`;
    icon.style.display = "block";
    document.body.appendChild(icon);

    icon.onclick = () => {
        icon.style.display = "none";
        // Check if setup is done
        chrome.storage.local.get(['setup_done', 'groq_api_key'], (settings) => {
    console.log("SETTINGS:", settings);

    if (!settings.setup_done || !settings.groq_api_key) {
        chrome.runtime.sendMessage({ action: "OPEN_SETUP_PAGE" });
    } else {
        runPrivacyMasking(settings.devMode);
    }
});
    };
}

function runPrivacyMasking(isDevMode) {
    if (document.getElementById("s-panel")) document.getElementById("s-panel").remove();

    injectUI();

    const statusBtn = document.getElementById("s-mask-btn");
    statusBtn.innerText = "Analyzing Privacy...";

    chrome.runtime.sendMessage({ action: "ANALYZE_PII", text: selectedText }, (res) => {
        if (res?.success) {
            localVault = res.data.entity_map;
            maskedData = res.data.masked_text;

            // ✅ ALWAYS SHOW MASKED FIRST
            document.getElementById("s-preview").innerText = maskedData;
            document.getElementById("s-mask-box").style.display = "block";

            statusBtn.innerText = "Privacy Masked ✓";

        } else {
            alert("Privacy Engine Offline.\nRun AUTO_START.bat");
            statusBtn.innerText = "Engine Offline";
        }
    });
}
function generateFinalReply(textToProcess) {
    const btn = document.getElementById("s-generate");
    btn.innerText = "Generating...";

    chrome.runtime.sendMessage({ action: "GENERATE_REPLY", text: textToProcess }, (res) => {
        if (res?.success) {
            let finalReply = res.data;

            for (let placeholder in localVault) {
                finalReply = finalReply.replaceAll(placeholder, localVault[placeholder]);
            }

            document.getElementById("s-result").innerText = finalReply;
            document.getElementById("s-res-box").style.display = "block";

            btn.innerText = "Done ✓";
        }
    });
}

function injectUI() {
    const panel = document.createElement("div");
    panel.id = "s-panel";

    panel.innerHTML = `
        <div id="s-header">
            SSERA Pro 
            <span id="s-close">×</span>
        </div>

        <div id="s-body">
            <button id="s-mask-btn">Initiating...</button>

            <div id="s-mask-box" style="display:none;">
                <div class="s-label">🔒 MASKED PREVIEW:</div>
                <div id="s-preview"></div>

                <button id="s-generate">Generate Reply</button>
            </div>

            <div id="s-res-box" style="display:none;">
                <div class="s-label">✅ FINAL REPLY:</div>
                <div id="s-result"></div>

                <button id="s-copy">Copy Reply</button>
            </div>
        </div>
    `;

    document.body.appendChild(panel);

    // Close
    document.getElementById("s-close").onclick = () => panel.remove();

    // Generate button
    document.getElementById("s-generate").onclick = () => {
        generateFinalReply(maskedData);
    };

    // Copy
    document.getElementById("s-copy").onclick = () => {
        navigator.clipboard.writeText(document.getElementById("s-result").innerText);
        alert("Copied!");
    };

    // ✅ Enable Drag
    makeDraggable(panel);
}
function makeDraggable(panel) {
    const header = panel.querySelector("#s-header");

    let offsetX = 0, offsetY = 0, isDragging = false;

    header.onmousedown = (e) => {
        isDragging = true;
        offsetX = e.clientX - panel.offsetLeft;
        offsetY = e.clientY - panel.offsetTop;
    };

    document.onmousemove = (e) => {
        if (!isDragging) return;

        panel.style.left = (e.clientX - offsetX) + "px";
        panel.style.top = (e.clientY - offsetY) + "px";
        panel.style.right = "auto";
        panel.style.bottom = "auto";
    };

    document.onmouseup = () => {
        isDragging = false;
    };
}