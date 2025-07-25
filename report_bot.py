
from playwright.async_api import async_playwright
import asyncio
import os

SESSIONS = {}

async def run_report(session_id, session_data):
    SESSIONS[session_id] = {
        "state": "waiting_for_otp",
        "browser": None,
        "context": None,
        "page": None,
        "otp": None,
        "result": None,
        "data": session_data
    }

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    SESSIONS[session_id]["browser"] = browser
    SESSIONS[session_id]["context"] = context
    SESSIONS[session_id]["page"] = page

    await page.goto("https://s3.bureausuite.co.za/login.php")
    await page.fill('input[name="usercode"]', session_data["username"])
    await page.fill('input[name="password"]', session_data["password"])
    await page.click('input[value="Bureau Login"]')

    print("[!] Waiting for OTP submission via /otp...")

async def submit_otp(session_id, otp_code, session_data):
    session = SESSIONS.get(session_id)
    if not session:
        return {"status": "error", "message": "No active session"}

    page = session["page"]
    await page.fill('input[placeholder="Enter your authentication code here."]', otp_code)
    await page.click('input[value="Log in"]')

    try:
        await page.wait_for_selector('text=ENQUIRIES', timeout=10000)
    except:
        return {"status": "error", "message": "Login or OTP failed"}

    await page.hover('text=ENQUIRIES')
    await page.hover('text=INDIVIDUAL ENQUIRIES')
    await page.click('text=CREDIT ENQUIRY')

    await page.wait_for_selector('input[name="ctl00$MainContent$txtIdNumber"]', timeout=10000)
    await page.fill('input[name="ctl00$MainContent$txtIdNumber"]', session_data["id_number"])
    await page.fill('input[name="ctl00$MainContent$txtFirstname"]', session_data["first_name"])
    await page.fill('input[name="ctl00$MainContent$txtSurname"]', session_data["surname"])
    await page.fill('input[name="ctl00$MainContent$txtEnquiryReference"]', "CONSUMER")
    await page.select_option('select[name="ctl00$MainContent$ddlPurpose"]', label="Free Credit Report")
    await page.click('input[name="ctl00$MainContent$btnDoEnquiry"]')

    await page.wait_for_selector('text=Credit Enquiry Result', timeout=15000)
    score = await page.inner_text('//td[text()="Credit Score:"]/following-sibling::td')
    name = await page.inner_text('//td[text()="Input Names:"]/following-sibling::td')
    id_number = await page.inner_text('//td[text()="Input ID Number:"]/following-sibling::td')

    await session["browser"].close()
    return {
        "status": "success",
        "credit_score": score,
        "name": name.strip(),
        "id_number": id_number.strip()
    }
