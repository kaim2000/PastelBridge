# PowerShell script for testing HTTPS API with self-signed certificate

# Option 1: Using Invoke-RestMethod with SkipCertificateCheck (PowerShell 7+)
$headers = @{
    "X-API-Key" = "cc522a73-5a85-40f8-802d-02ba6560caf5"
}

# For PowerShell 7+ (recommended)
try {
    $response = Invoke-RestMethod -Uri "https://localhost:8000/api/ping" `
        -Headers $headers `
        -Method Get `
        -SkipCertificateCheck
    
    Write-Host "Success! Response:" -ForegroundColor Green
    $response | ConvertTo-Json
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# Option 2: Using .NET HttpClient (works in all PowerShell versions)
Write-Host "`nOption 2: Using .NET HttpClient..." -ForegroundColor Yellow

# Ignore SSL certificate validation for this session
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Make the request
$uri = "https://localhost:8000/api/ping"
$webRequest = [System.Net.WebRequest]::Create($uri)
$webRequest.Headers.Add("X-API-Key", "cc522a73-5a85-40f8-802d-02ba6560caf5")
$webRequest.Method = "GET"

try {
    $response = $webRequest.GetResponse()
    $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
    $content = $reader.ReadToEnd()
    
    Write-Host "Success! Response:" -ForegroundColor Green
    $content | ConvertFrom-Json | ConvertTo-Json
    
    $reader.Close()
    $response.Close()
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# Option 3: Test with HTTP first (if you need to disable HTTPS temporarily)
Write-Host "`nTo test with HTTP instead, you can temporarily disable SSL in your .env file" -ForegroundColor Yellow
Write-Host "Set ssl_cert_file= and ssl_key_file= (empty values) and restart the service" -ForegroundColor Yellow 