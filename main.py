from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
from report_bot import run_report, submit_otp

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In-memory store
session_data = {}

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/run-report", response_class=JSONResponse)
async def run_report_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    id_number: str = Form(...),
    first_name: str = Form(...),
    surname: str = Form(...),
):
    session_id = "default"
    session_data[session_id] = {
        "username": username,
        "password": password,
        "id_number": id_number,
        "first_name": first_name,
        "surname": surname,
    }
    asyncio.create_task(run_report(session_id, session_data))
    return {"status": "OTP Required", "message": "Enter OTP at /otp"}

@app.get("/otp", response_class=HTMLResponse)
async def otp_get(request: Request):
    return templates.TemplateResponse("otp.html", {"request": request})

@app.post("/otp", response_class=JSONResponse)
async def otp_post(otp_code: str = Form(...)):
    session_id = "default"
    result = await submit_otp(session_id, otp_code, session_data)
    return JSONResponse(result)
