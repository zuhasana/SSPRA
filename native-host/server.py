import os
import json
import warnings
import re
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
import os
from fastapi import HTTPException



warnings.filterwarnings("ignore")

app = FastAPI()

# Enable connection from other laptops on the network
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# INITIALIZE PRESIDIO WITH YOUR EXACT RECOGNIZERS
# =====================================================
analyzer = AnalyzerEngine(default_score_threshold=0.6)

# 1. UNIQUE IDENTIFIERS
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="AADHAR", patterns=[Pattern("aadhar", r"\b\d{4}\s\d{4}\s\d{4}\b", 0.95)], context=["aadhar", "uid"]))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PAN", patterns=[Pattern("pan", r"\b[A-Z]{5}\d{4}[A-Z]\b", 0.95)], context=["pan", "tax"]))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PASSPORT", patterns=[Pattern("passport", r"\b[A-Z][0-9]{7}\b", 0.95)], context=["passport"]))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="EMPLOYEE_ID", patterns=[Pattern("emp", r"\bEMP\d{3,6}\b", 0.9)], context=["employee", "emp"]))

# 2. FINANCIAL DATA
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="BANK_ACCOUNT", patterns=[Pattern("account", r"\b\d{9,18}\b", 0.85)], context=["account", "bank"]))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="IFSC", patterns=[Pattern("ifsc", r"\b[A-Z]{4}0[A-Z0-9]{6}\b", 0.95)], context=["ifsc", "bank"]))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="CREDIT_CARD", patterns=[Pattern("card", r"\b(?:\d[ -]*?){13,16}\b", 0.95)], context=["credit", "card", "debit"]))
money_regex = r"(?:₹|Rs\.?)\s?\d{1,3}(?:,\d{2})*(?:,\d{3})|\b\d{1,3}(?:,\d{2})+(?:,\d{3})\b"
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="MONEY", patterns=[Pattern("money", money_regex, 0.9)], context=["salary", "revenue", "amount", "profit"]))

# 3. ACCESS CREDENTIALS
password_regex = r"(?i)(?:password|pwd|passcode)\s*[:=]\s*([A-Za-z0-9@#$%^&*!]{8,25})"
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PASSWORD", patterns=[Pattern("password", password_regex, 0.99)]))
email_regex = r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="LOGIN_ID", patterns=[Pattern("email", email_regex, 0.95)], context=["login", "email", "username"]))
api_regex = r"\b[A-Za-z0-9]{32,45}\b"
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="API_KEY", patterns=[Pattern("api", api_regex, 0.9)], context=["api", "token", "secret"]))

# 4. CORPORATE DATA
org_regex = r"\b[A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)*\s(?:Solutions|Technologies|Systems|Labs|Corp|Ltd|Pvt\.?\s*Ltd\.?)"
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="ORGANIZATION", patterns=[Pattern("org", org_regex, 0.9)], context=["company", "organization"]))
project_regex = r"\b(Project|Deal)\s[A-Z][A-Za-z]+\b"
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PROJECT", patterns=[Pattern("project", project_regex, 0.9)]))

# 5. CONTACT / DIGITAL FOOTPRINT
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PHONE_NUMBER", patterns=[Pattern("phone", r"\b[6-9]\d{4}\s?\d{5}\b", 0.95)], context=["phone", "contact", "mobile"]))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="IP_ADDRESS", patterns=[Pattern("ip", r"\b(?:\d{1,3}\.){3}\d{1,3}\b", 0.95)]))
analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="MAC_ADDRESS", patterns=[Pattern("mac", r"\b([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b", 0.95)]))

class AnalyzeRequest(BaseModel):
    text: str

# =====================================================
# YOUR EXACT MASKING ENGINE LOGIC
# =====================================================
def mask_text_logic(text):
    results = analyzer.analyze(text=text, language="en")

    # Remove overlapping detections
    results = sorted(results, key=lambda x: (x.start, x.end))
    filtered = []
    last_end = -1
    for r in results:
        if r.start >= last_end:
            filtered.append(r)
            last_end = r.end

    masked_text = text
    entity_map = {}

    # Sort backwards to avoid index shifting
    for i, r in enumerate(sorted(filtered, key=lambda x: x.start, reverse=True)):
        value = text[r.start:r.end]
        label = r.entity_type
        placeholder = f"[{label}_{i}]"
        entity_map[placeholder] = value
        masked_text = (
            masked_text[:r.start] +
            placeholder +
            masked_text[r.end:]
        )
    return masked_text, entity_map

# =====================================================
# ENDPOINTS
# =====================================================

@app.get("/")
async def home():
    return {"status": "SSERA Server Online", "demo_url": "/store"}

@app.get("/store", response_class=HTMLResponse)
async def get_store():
    # This page allows Laptop B to download the extension
    return """
    <html>
    <head><title>SSERA Web Store</title></head>
    <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #f4f4f4;">
        <div style="background: white; padding: 40px; border-radius: 10px; width: 400px; margin: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <h1>🛡️ SSERA Pro</h1>
            <p>Smart Secure Email Reply Assistant</p>
            <button onclick="location.href='/download'" style="background: black; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Add to Chrome</button>
        </div>
    </body>
    </html>
    """

import os

@app.get("/download")
async def download():
    file_path = "extension.zip"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="extension.zip not found")

    return FileResponse(file_path, filename="extension.zip")

@app.get("/engine")
async def download_engine():
    file_path = "native-host.zip"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="privacy-engine.zip not found")

    return FileResponse(file_path, filename="native-host.zip")

@app.post("/analyze")
async def analyze_api(req: AnalyzeRequest):
    try:
        masked, mapping = mask_text_logic(req.text)
        return {"masked_text": masked, "entity_map": mapping}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # host="0.0.0.0" is required so Laptop B can see the server
    uvicorn.run(app, host="0.0.0.0", port=8000)