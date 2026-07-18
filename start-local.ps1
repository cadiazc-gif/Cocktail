$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Levantando Cocktail Bar Manager en http://127.0.0.1:8000/" -ForegroundColor Cyan
python .\server.py
