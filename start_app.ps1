# PowerShell 启动脚本
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "Starting Streamlit application..." -ForegroundColor Green
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host "App file: app.py" -ForegroundColor Cyan

if (-not (Test-Path "app.py")) {
    Write-Host "Error: app.py not found in current directory!" -ForegroundColor Red
    exit 1
}

streamlit run app.py --server.port 8511

