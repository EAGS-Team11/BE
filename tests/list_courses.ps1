# tests/list_courses.ps1

param(
    [string]$nim_nip = "11221058",
    [string]$password = "Dp061203",
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

Write-Host "Fetching all courses..." -ForegroundColor Cyan

# Login terlebih dahulu
$loginBody = @{ nim_nip = $nim_nip; password = $password } | ConvertTo-Json

try {
    $loginResp = Invoke-RestMethod -Uri "$BaseUrl/auth/login" -Method Post -Body $loginBody -ContentType 'application/json'
    $token = $loginResp.access_token
    Write-Host "Login successful." -ForegroundColor Green
} catch {
    Write-Host "Login failed:" -ForegroundColor Red
    if ($_.Exception.Response) { Write-Host ($_.Exception.Response.Content.ReadAsStringAsync().Result) }
    exit 1
}

# Fetch semua courses
try {
    $courses = Invoke-RestMethod -Uri "$BaseUrl/course/" -Method Get -Headers @{ Authorization = "Bearer $token" }
    
    if ($courses.Count -eq 0) {
        Write-Host "Tidak ada course." -ForegroundColor Yellow
    } else {
        Write-Host "`nDaftar Course:" -ForegroundColor Green
        $courses | ForEach-Object {
            Write-Host "---"
            Write-Host "ID       : $($_.id_course)"
            Write-Host "Kode     : $($_.kode_course)"
            Write-Host "Nama     : $($_.nama_course)"
            Write-Host "Dosen    : $($_.id_dosen)"
            Write-Host "Access   : $($_.access_code)"
            Write-Host "Dibuat   : $($_.created_at)"
        }
    }
} catch {
    Write-Host "Failed to fetch courses:" -ForegroundColor Red
    if ($_.Exception.Response) { Write-Host ($_.Exception.Response.Content.ReadAsStringAsync().Result) }
    exit 1
}
