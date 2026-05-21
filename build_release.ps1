param(
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReleaseName = "AtalhoMedico-v$Version"
$ReleaseDir = Join-Path $Root "release\$ReleaseName"
$ZipPath = Join-Path $Root "release\$ReleaseName.zip"

Set-Location $Root

python -m unittest discover -s tests -v

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "AtalhoMedico" `
    --icon "assets\atalho_medico.ico" `
    --add-data "atalho_medico\data\snippets.json;atalho_medico\data" `
    --hidden-import pythoncom `
    --hidden-import pywintypes `
    --hidden-import win32com `
    --hidden-import win32com.client `
    --hidden-import win32timezone `
    main.py

if (Test-Path $ReleaseDir) {
    Remove-Item $ReleaseDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

Copy-Item "dist\AtalhoMedico.exe" (Join-Path $ReleaseDir "AtalhoMedico.exe")
Copy-Item "README.md" (Join-Path $ReleaseDir "README.md")
Copy-Item "atalho_medico\data\snippets.json" (Join-Path $ReleaseDir "snippets_iniciais.json")

Get-FileHash (Join-Path $ReleaseDir "AtalhoMedico.exe") -Algorithm SHA256 |
    Format-List |
    Out-File (Join-Path $ReleaseDir "SHA256.txt") -Encoding utf8

@"
Atalho Medico v$Version

Como usar:
1. Execute AtalhoMedico.exe.
2. O aplicativo fica disponivel tambem na bandeja do Windows.
3. Ao fechar no X, escolha se deseja enviar para bandeja ou encerrar.

Dados do usuario:
- A biblioteca de atalhos e logs ficam em uma pasta local de dados do usuario.
- O arquivo snippets_iniciais.json e apenas uma copia da biblioteca inicial.

Observacao:
- O Windows pode exibir aviso de aplicativo desconhecido porque o executavel ainda nao e assinado digitalmente.
"@ | Out-File (Join-Path $ReleaseDir "LEIA-ME-RELEASE.txt") -Encoding utf8

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}
Compress-Archive -Path (Join-Path $ReleaseDir "*") -DestinationPath $ZipPath

Write-Host "Release criada em: $ReleaseDir"
Write-Host "ZIP criado em: $ZipPath"
