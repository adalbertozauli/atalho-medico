param(
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$InstallerRoot = Join-Path $Root "release\installer-$Version-$Stamp"
$SetupPath = Join-Path $InstallerRoot "AtalhoMedicoSetup-v$Version.exe"

Set-Location $Root

if (-not (Test-Path "dist\AtalhoMedico.exe")) {
    .\build_release.ps1 -Version $Version
}

New-Item -ItemType Directory -Path $InstallerRoot | Out-Null

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "AtalhoMedicoSetup" `
    --icon "assets\atalho_medico.ico" `
    --add-binary "dist\AtalhoMedico.exe;." `
    --add-data "README.md;." `
    installer_main.py

Copy-Item "dist\AtalhoMedicoSetup.exe" $SetupPath

Get-FileHash $SetupPath -Algorithm SHA256 |
    Format-List |
    Out-File (Join-Path $InstallerRoot "AtalhoMedicoSetup-v$Version-SHA256.txt") -Encoding utf8

Write-Host "Instalador criado em: $SetupPath"
