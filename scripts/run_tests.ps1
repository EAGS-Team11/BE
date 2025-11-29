# run_tests.ps1 - automated endpoint tests for local API
Write-Host "Starting automated endpoint tests..."

# Login mahasiswa
$mahBody = @{ nim_nip = '20230001'; password = 'TestPass123' } | ConvertTo-Json
$mahResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/auth/login" -Method Post -Body $mahBody -ContentType 'application/json'
$MAH_TOKEN = $mahResp.access_token
Write-Host "[MAHASISWA TOKEN]" $MAH_TOKEN.Substring(0,20) '...'

# Login dosen
$dosenBody = @{ nim_nip = '19900001'; password = 'DosenPass123' } | ConvertTo-Json
$dosenResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/auth/login" -Method Post -Body $dosenBody -ContentType 'application/json'
$DOSEN_TOKEN = $dosenResp.access_token
Write-Host "[DOSEN TOKEN]" $DOSEN_TOKEN.Substring(0,20) '...'

# Create course as dosen
$courseBody = @{ kode_course = 'CS-SWAG'; nama_course = 'Swagger Test Course'; access_code = 'SWAG123' } | ConvertTo-Json
$courseResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/course/" -Method Post -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" } -Body $courseBody -ContentType 'application/json'
Write-Host "[COURSE]" ($courseResp | ConvertTo-Json -Depth 2)

# Join course as mahasiswa
$joinBody = @{ id_course = $courseResp.id_course } | ConvertTo-Json
$joinResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/course/join" -Method Post -Headers @{ Authorization = "Bearer $MAH_TOKEN" } -Body $joinBody -ContentType 'application/json'
Write-Host "[JOIN]" ($joinResp | ConvertTo-Json -Depth 2)

# Create assignment as dosen
$assignmentBody = @{ id_course = $courseResp.id_course; judul = 'Swagger Test Assignment'; deskripsi = 'Testing assignment creation'; deadline = '2025-12-31T23:59:59' } | ConvertTo-Json
$assignmentResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/assignment/" -Method Post -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" } -Body $assignmentBody -ContentType 'application/json'
Write-Host "[ASSIGNMENT]" ($assignmentResp | ConvertTo-Json -Depth 2)

# Submit assignment as mahasiswa
$submissionBody = @{ id_assignment = $assignmentResp.id_assignment; jawaban = 'Ini jawaban test via Swagger automation. Isi essay pendek untuk test.' } | ConvertTo-Json
$submissionResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/submission/" -Method Post -Headers @{ Authorization = "Bearer $MAH_TOKEN" } -Body $submissionBody -ContentType 'application/json'
Write-Host "[SUBMISSION]" ($submissionResp | ConvertTo-Json -Depth 2)

# Predict (no save) as dosen
$predictBody = @{ id_submission = $submissionResp.id_submission; keywords = @('AI','ethics') } | ConvertTo-Json
$predictResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict/predict" -Method Post -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" } -Body $predictBody -ContentType 'application/json'
Write-Host "[PREDICT]" ($predictResp | ConvertTo-Json -Depth 3)

# Grade (save) as dosen
$gradeResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict/grade" -Method Post -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" } -Body $predictBody -ContentType 'application/json'
Write-Host "[GRADE SAVED]" ($gradeResp | ConvertTo-Json -Depth 3)

# Get grading
$getGrade = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict/grade/$($submissionResp.id_submission)" -Method Get -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" }
Write-Host "[GET GRADE]" ($getGrade | ConvertTo-Json -Depth 3)

# Upload text
$uploadBody = @{ title = 'Upload Test'; content = 'This is a test upload content from automation.' } | ConvertTo-Json
$uploadResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/upload/text" -Method Post -Body $uploadBody -ContentType 'application/json'
Write-Host "[UPLOAD TEXT]" ($uploadResp | ConvertTo-Json -Depth 2)

Write-Host 'ALL TESTS COMPLETED'
