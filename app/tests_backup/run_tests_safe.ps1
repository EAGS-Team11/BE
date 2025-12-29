# tests/run_tests_safe.ps1

# run_tests_safe.ps1 - safer automated endpoint tests with try/catch
function TryCall($scriptblock){
    try{
        & $scriptblock
    } catch {
        Write-Host "ERROR:" $_.Exception.Message
        if ($_.Exception.Response) {
            $content = $_.Exception.Response.Content.ReadAsStringAsync().Result
            Write-Host "RESPONSE_CONTENT:" $content
        }
    }
}

Write-Host "Starting safe tests..."

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

# Create course
Write-Host "--> Create course"
TryCall { $courseBody = @{ kode_course = 'CS-SAFE'; nama_course = 'Safe Course'; access_code = 'SAFE123' } | ConvertTo-Json; $courseResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/course/" -Method Post -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" } -Body $courseBody -ContentType 'application/json'; Write-Host ($courseResp | ConvertTo-Json -Depth 2) }

# Join course
Write-Host "--> Join course"
TryCall { $joinBody = @{ id_course = $courseResp.id_course } | ConvertTo-Json; $joinResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/course/join" -Method Post -Headers @{ Authorization = "Bearer $MAH_TOKEN" } -Body $joinBody -ContentType 'application/json'; Write-Host ($joinResp | ConvertTo-Json -Depth 2) }

# Create assignment
Write-Host "--> Create assignment"
TryCall { $assignmentBody = @{ id_course = $courseResp.id_course; judul = 'Safe Assignment'; deskripsi = 'Safe test'; deadline = '2025-12-31T23:59:59' } | ConvertTo-Json; $assignmentResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/assignment/" -Method Post -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" } -Body $assignmentBody -ContentType 'application/json'; Write-Host ($assignmentResp | ConvertTo-Json -Depth 2) }

# Submit
Write-Host "--> Submit assignment"
TryCall { $submissionBody = @{ id_assignment = $assignmentResp.id_assignment; jawaban = 'Safe automated submission content for testing.' } | ConvertTo-Json; $submissionResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/submission/" -Method Post -Headers @{ Authorization = "Bearer $MAH_TOKEN" } -Body $submissionBody -ContentType 'application/json'; Write-Host ($submissionResp | ConvertTo-Json -Depth 2) }

# Predict
Write-Host "--> Predict"
TryCall { $predictBody = @{ id_submission = $submissionResp.id_submission; keywords = @('AI','ethics') } | ConvertTo-Json; $predictResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict/predict" -Method Post -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" } -Body $predictBody -ContentType 'application/json'; Write-Host ($predictResp | ConvertTo-Json -Depth 3) }

# Grade
Write-Host "--> Grade (save)"
TryCall { $gradeResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict/grade" -Method Post -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" } -Body $predictBody -ContentType 'application/json'; Write-Host ($gradeResp | ConvertTo-Json -Depth 3) }

# Get grade
Write-Host "--> Get grade"
TryCall { $getGrade = Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict/grade/$($submissionResp.id_submission)" -Method Get -Headers @{ Authorization = "Bearer $DOSEN_TOKEN" }; Write-Host ($getGrade | ConvertTo-Json -Depth 3) }

# Upload text
Write-Host "--> Upload text"
TryCall { $uploadBody = @{ title = 'Safe Upload'; content = 'Upload text test content.' } | ConvertTo-Json; $uploadResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/upload/text" -Method Post -Body $uploadBody -ContentType 'application/json'; Write-Host ($uploadResp | ConvertTo-Json -Depth 2) }

Write-Host 'SAFE TESTS COMPLETED'
