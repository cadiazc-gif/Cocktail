$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$cloudflared = Join-Path $root "tools\cloudflared.exe"
if (-not (Test-Path $cloudflared)) {
  Write-Host "No encuentro tools\\cloudflared.exe" -ForegroundColor Red
  Write-Host "Instala cloudflared y vuelve a ejecutar este script." -ForegroundColor Yellow
  Write-Host "Descarga oficial: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/" -ForegroundColor Yellow
  exit 1
}

Write-Host "Creando URL publica temporal con Cloudflare Quick Tunnel..." -ForegroundColor Cyan
Write-Host "Asegurate de tener la app corriendo en http://127.0.0.1:8000/" -ForegroundColor Yellow
& $cloudflared tunnel --url http://127.0.0.1:8000
