param(
    [Parameter(Mandatory=$true)] [string]$nim_nip,
    [Parameter(Mandatory=$true)] [string]$password,
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

Write-Host "Checking account for user: $nim_nip against $BaseUrl"

$loginBody = @{ nim_nip = $nim_nip; password = $password } | ConvertTo-Json

try {
    $loginResp = Invoke-RestMethod -Uri "$BaseUrl/auth/login" -Method Post -Body $loginBody -ContentType 'application/json'
} catch {
    Write-Host "Login failed:" -ForegroundColor Red
    if ($_.Exception.Response) { Write-Host ($_.Exception.Response.Content.ReadAsStringAsync().Result) }
    exit 1
}

$token = $loginResp.access_token
Write-Host "Login successful. Token (first 80):" $token.Substring(0,[Math]::Min(80,$token.Length))

# Call /auth/me to verify token and get user info
try {
    $me = Invoke-RestMethod -Uri "$BaseUrl/auth/me" -Method Get -Headers @{ Authorization = "Bearer $token" }
    Write-Host "\nUser info from /auth/me:" -ForegroundColor Green
    $me | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "Failed to call /auth/me:" -ForegroundColor Red
    if ($_.Exception.Response) { Write-Host ($_.Exception.Response.Content.ReadAsStringAsync().Result) }
    exit 1
}

# Summary
Write-Host "\nSummary:" -ForegroundColor Cyan
Write-Host "- nim_nip :" $me.nim_nip
Write-Host "- nama    :" $me.nama
Write-Host "- role    :" $me.role
Write-Host "- prodi   :" $me.prodi

Write-Host "\nAccount check completed successfully." -ForegroundColor Green
