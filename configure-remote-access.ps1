# Configure Remote Access for Pastel Bridge API
# Run this script as Administrator

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator. Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

Write-Host "=== Configuring Remote Access for Pastel Bridge API ===" -ForegroundColor Cyan

# DuckDNS Configuration Instructions
Write-Host "`n=== DuckDNS Setup ===" -ForegroundColor Cyan
Write-Host "Your DuckDNS domain will be: pastelbridge.duckdns.org" -ForegroundColor Green
Write-Host "This will automatically update when your IP changes!" -ForegroundColor Yellow
Write-Host "`nMake sure DuckDNS client is running and configured with:" -ForegroundColor White
Write-Host "  - Domain: pastelbridge (or your chosen name)" -ForegroundColor Gray
Write-Host "  - Token: Your DuckDNS token from https://duckdns.org" -ForegroundColor Gray
Write-Host "  - Refresh: 5 minutes" -ForegroundColor Gray
Write-Host "  - Notifications: YES" -ForegroundColor Gray

# 1. Get current PC's network information
Write-Host "`nYour PC's Network Information:" -ForegroundColor Yellow
$ipconfig = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}
$ipconfig | ForEach-Object {
    Write-Host "  Interface: $($_.InterfaceAlias)"
    Write-Host "  IP Address: $($_.IPAddress)" -ForegroundColor Green
}

# Get the most likely LAN IP (usually 192.168.x.x or 10.x.x.x)
$lanIP = $ipconfig | Where-Object {$_.IPAddress -match "^(192\.168\.|10\.)" } | Select-Object -First 1 -ExpandProperty IPAddress
if ($lanIP) {
    Write-Host "`nYour LAN IP (for MacBook to connect): $lanIP" -ForegroundColor Green
}

# 2. Configure firewall rules
Write-Host "`nConfiguring Firewall Rules..." -ForegroundColor Yellow

# Remove existing rule
Remove-NetFirewallRule -DisplayName "Pastel Bridge API" -ErrorAction SilentlyContinue

# Production server IP
$productionIP = "13.247.230.43"

# Create firewall rule for production
try {
    New-NetFirewallRule -DisplayName "Pastel Bridge API - Production" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 8000 `
        -Action Allow `
        -RemoteAddress $productionIP `
        -ErrorAction Stop | Out-Null
    
    Write-Host "✓ Firewall rule created for Production: $productionIP" -ForegroundColor Green
} catch {
    Write-Error "Failed to create firewall rule for production: $_"
}

# Create firewall rule for local network (for MacBook development)
try {
    New-NetFirewallRule -DisplayName "Pastel Bridge API - Local Network" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 8000 `
        -Action Allow `
        -RemoteAddress "192.168.0.0/16","10.0.0.0/8","172.16.0.0/12" `
        -ErrorAction Stop | Out-Null
    
    Write-Host "✓ Firewall rule created for Local Network (includes your MacBook)" -ForegroundColor Green
} catch {
    Write-Error "Failed to create firewall rule for local network: $_"
}

# 3. Update .env file
Write-Host "`nUpdating .env configuration..." -ForegroundColor Yellow

$envPath = "C:\PastelBridge\.env"
$envContent = Get-Content $envPath -Raw

# Find current ALLOWED_IPS line
if ($envContent -match 'ALLOWED_IPS=(.*)') {
    $currentIPs = $matches[1]
    Write-Host "Current ALLOWED_IPS: $currentIPs" -ForegroundColor Gray
    
    # Prepare new IP list (keep existing + add new)
    $newIPs = "127.0.0.1,::1,$productionIP"
    
    # Add local network subnet for development
    if ($lanIP) {
        $subnet = $lanIP -replace '\.\d+$', '.0/24'
        Write-Host "`nTo allow your entire local network (including MacBook):" -ForegroundColor Yellow
        Write-Host "Add this subnet to ALLOWED_IPS: $subnet" -ForegroundColor Cyan
    }
    
    Write-Host "`nRECOMMENDED: Update your .env file manually:" -ForegroundColor Yellow
    Write-Host "ALLOWED_IPS=$newIPs" -ForegroundColor Green
    Write-Host "Or for development, you can temporarily use:" -ForegroundColor Yellow
    Write-Host "ALLOWED_IPS=" -ForegroundColor Green -NoNewline
    Write-Host " (empty = allow all - NOT for production!)" -ForegroundColor Red
}

# 4. Instructions for MacBook
Write-Host "`n=== Instructions for Your MacBook ===" -ForegroundColor Cyan
Write-Host "1. On your MacBook, find your IP address:" -ForegroundColor White
Write-Host "   Open Terminal and run: ifconfig | grep 'inet '" -ForegroundColor Green
Write-Host "   Look for an IP like 192.168.x.x or 10.x.x.x" -ForegroundColor Gray
Write-Host "`n2. Test connection from MacBook:" -ForegroundColor White
Write-Host "   curl -k https://$lanIP:8000/api/ping -H 'X-API-Key: cc522a73-5a85-40f8-802d-02ba6560caf5'" -ForegroundColor Green
Write-Host "`n3. If you know your MacBook's IP, add it to .env:" -ForegroundColor White
Write-Host "   ALLOWED_IPS=127.0.0.1,::1,$productionIP,YOUR_MACBOOK_IP" -ForegroundColor Green

# 5. Service restart reminder
Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Edit C:\PastelBridge\.env to update ALLOWED_IPS" -ForegroundColor White
Write-Host "2. Restart the service:" -ForegroundColor White
Write-Host "   nssm restart PastelBridgeAPI" -ForegroundColor Green
Write-Host "3. Test from your MacBook using the IP: $lanIP" -ForegroundColor White

# Show current firewall rules
Write-Host "`n=== Current Firewall Rules ===" -ForegroundColor Cyan
Get-NetFirewallRule -DisplayName "Pastel Bridge API*" | Select-Object DisplayName, Enabled, Direction, Action | Format-Table 