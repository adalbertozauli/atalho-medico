$ErrorActionPreference = "Stop"

$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\AtalhoMedico"
$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Atalho Médico"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "Atalho Médico.lnk"
$ExePath = Join-Path $InstallDir "AtalhoMedico.exe"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $StartMenuDir | Out-Null

Copy-Item (Join-Path $SourceDir "AtalhoMedico.exe") $ExePath -Force
Copy-Item (Join-Path $SourceDir "README.md") (Join-Path $InstallDir "README.md") -Force
Copy-Item (Join-Path $SourceDir "uninstall.ps1") (Join-Path $InstallDir "uninstall.ps1") -Force

$UninstallCmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$InstallDir\uninstall.ps1`""
$UninstallShortcut = Join-Path $StartMenuDir "Desinstalar Atalho Médico.lnk"
$StartShortcut = Join-Path $StartMenuDir "Atalho Médico.lnk"

$Shell = New-Object -ComObject WScript.Shell

$Shortcut = $Shell.CreateShortcut($StartShortcut)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = $ExePath
$Shortcut.Save()

$Shortcut = $Shell.CreateShortcut($DesktopShortcut)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = $ExePath
$Shortcut.Save()

$Shortcut = $Shell.CreateShortcut($UninstallShortcut)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$InstallDir\uninstall.ps1`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Save()

$RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\AtalhoMedico"
New-Item -Path $RegPath -Force | Out-Null
Set-ItemProperty -Path $RegPath -Name "DisplayName" -Value "Atalho Médico"
Set-ItemProperty -Path $RegPath -Name "DisplayVersion" -Value "0.1.0"
Set-ItemProperty -Path $RegPath -Name "Publisher" -Value "Atalho Médico"
Set-ItemProperty -Path $RegPath -Name "InstallLocation" -Value $InstallDir
Set-ItemProperty -Path $RegPath -Name "DisplayIcon" -Value $ExePath
Set-ItemProperty -Path $RegPath -Name "UninstallString" -Value $UninstallCmd

Start-Process -FilePath $ExePath
