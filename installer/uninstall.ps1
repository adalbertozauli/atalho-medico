$ErrorActionPreference = "SilentlyContinue"

$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\AtalhoMedico"
$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Atalho Médico"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Atalho Médico.lnk"
$RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\AtalhoMedico"

Get-Process -Name "AtalhoMedico" | Stop-Process -Force

Remove-Item $DesktopShortcut -Force
Remove-Item $StartMenuDir -Recurse -Force
Remove-Item $RegPath -Recurse -Force
Remove-Item $InstallDir -Recurse -Force

Write-Host "Atalho Médico foi desinstalado."
