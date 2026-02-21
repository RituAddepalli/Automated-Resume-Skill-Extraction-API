import io
import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    """Check health endpoint."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"Resume Skill Matcher API" in res.data

def test_analyze_endpoint(client):
    """Test the /analyze endpoint with a dummy PDF."""
    # Create a minimal PDF in memory
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    pdf_bytes = io.BytesIO()
    c = canvas.Canvas(pdf_bytes, pagesize=letter)
    c.drawString(100, 750, "Python, SQL, Flask")  # include some skills
    c.save()
    pdf_bytes.seek(0)

    data = {
        "file": (pdf_bytes, "dummy_resume.pdf"),
        "job_skills": "python,sql,flask,aws"
    }

    res = client.post("/analyze", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    json_data = res.get_json()
    assert "matched_skills" in json_data
    assert "python" in json_data["matched_skills"]