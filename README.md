# BE - Back-End (EAGS Team 11)

Deskripsi singkat: Back-end untuk "Project Essay Automated Grading System (EAGS)" yang menyediakan API untuk otentikasi, manajemen course, assignments, submissions, dan grading.

**Fitur utama**
- **Autentikasi**: registrasi dan login dengan password yang di-hash, JWT untuk otorisasi.
- **Manajemen Course & Assignment**: endpoint untuk membuat dan mengelola course, enroll, dan assignment.
- **Submission & Grading**: upload submission dan mekanisme grading.
- **Dokumentasi API**: tersedia di Swagger UI (`/docs`).

**Tech stack**
- **Framework**: FastAPI
- **Database**: SQLAlchemy (ORM)
- **Auth**: JWT (python-jose) dan `passlib` (bcrypt)

**Persyaratan**
- Python 3.9+ (disarankan)
- Dependencies ada pada `requirements.txt`.

**Setup (PowerShell)**

1. Buat virtual environment dan install dependencies:

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
# copy example to .env and edit secrets
copy .env.example .env

2. Atur variabel lingkungan (contoh `.env` atau set di environment):

- `SECRET_KEY` : kunci rahasia JWT (jangan hardcode di repo)
- `DATABASE_URL` : connection string ke database (contoh: `sqlite:///./test.db` atau `postgresql://user:pass@host/db`)

Contoh singkat (PowerShell):

```pwsh
$env:SECRET_KEY = "ganti_dengan_rahasia_aman"
$env:DATABASE_URL = "sqlite:///./dev.db"
```

3. Jalankan server development:

```pwsh
uvicorn app.main:app --reload
```

Buka dokumentasi API di: `http://127.0.0.1:8000/docs`

BE - EAGS Team 11