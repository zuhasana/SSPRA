chrome.runtime.onInstalled.addListener(() => {
    chrome.tabs.create({ url: 'setup.html' });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    if (request.action === "OPEN_SETUP_PAGE") {
        chrome.tabs.create({ url: 'setup.html' });
        return;
    }

    // ✅ CALL FASTAPI
    if (request.action === "ANALYZE_PII") {
        fetch("http://localhost:8000/analyze", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ text: request.text })
        })
        .then(res => res.json())
        .then(data => sendResponse({ success: true, data }))
        .catch(err => sendResponse({ success: false, error: err.message }));

        return true;
    }

    // ✅ GROQ API
    if (request.action === "GENERATE_REPLY") {
        chrome.storage.local.get(['groq_api_key'], (result) => {

            fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${result.groq_api_key}`
                },
                body: JSON.stringify({
                    model: "llama-3.3-70b-versatile",
                    messages: [
                        { role: "system", content: "Professional assistant. Use placeholders exactly." },
                        { role: "user", content: `Reply to: ${request.text}` }
                    ]
                })
            })
            .then(r => r.json())
            .then(d => sendResponse({ success: true, data: d.choices[0].message.content }))
            .catch(e => sendResponse({ success: false, error: e.message }));
        });

        return true;
    }
});