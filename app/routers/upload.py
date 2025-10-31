from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
import io
from PyPDF2 import PdfReader

router = APIRouter(tags=["upload"])

# ---- Upload teks via JSON ----
class EssayUpload(BaseModel):
    title: str
    content: str

@router.post("/text")
def upload_essay(essay: EssayUpload):
    word_count = len(essay.content.split())
    char_count = len(essay.content)
    return {
        "title": essay.title,
        "word_count": word_count,
        "char_count": char_count
    }

# ---- Upload file (txt atau pdf) ----
@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    content = await file.read()
    
    if filename.lower().endswith(".pdf"):
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        word_count = len(text.split())
    else:
        # txt / lain
        text = content.decode()
        word_count = len(text.split())

    return {
        "filename": filename,
        "word_count": word_count
    }