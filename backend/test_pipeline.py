import requests

# 1. Login
login = requests.post("http://127.0.0.1:8000/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = login.json()["access_token"]
print("✅ Login OK")

# 2. Test pipeline
headers = {"Authorization": f"Bearer {token}"}

with open(r"C:\Users\ASUS\Downloads\cv1.pdf", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/applications/",
        headers=headers,
        data={
            "job_title": "Software Engineer",
            "company": "Google",
            "jd_text": "We are looking for a software engineer with Python, FastAPI, and SQL experience. You will build scalable backend services.",
        },
        files={"resume_pdf": ("cv1.pdf", f, "application/pdf")}
    )

print("Status:", response.status_code)
print("Response:", response.json())