param(
    [string]$VenvName = ".venv",
    [switch]$Recreate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{ Cmd = "py"; PrefixArgs = @("-3") }
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{ Cmd = "python"; PrefixArgs = @() }
    }

    throw "Python not found. Please install Python 3.10+ and ensure py or python is in PATH."
}

function Invoke-Checked {
    param(
        [string]$Cmd,
        [string[]]$CommandArgs,
        [string]$Step
    )

    Write-Host "[STEP] $Step"
    & $Cmd @CommandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Failed at step: $Step"
    }
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$requirementsFile = Join-Path $root "requirements.txt"
if (-not (Test-Path $requirementsFile)) {
    throw "requirements.txt not found at $requirementsFile"
}

$py = Get-PythonCommand
$venvPath = Join-Path $root $VenvName

if ($Recreate -and (Test-Path $venvPath)) {
    Write-Host "[STEP] Removing existing venv: $venvPath"
    Remove-Item -Path $venvPath -Recurse -Force
}

if (-not (Test-Path $venvPath)) {
    Invoke-Checked -Cmd $py.Cmd -CommandArgs ($py.PrefixArgs + @("-m", "venv", $VenvName)) -Step "Create virtual environment"
} else {
    Write-Host "[STEP] venv already exists: $venvPath"
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "venv python not found at $venvPython"
}

Invoke-Checked -Cmd $venvPython -CommandArgs @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel") -Step "Upgrade pip tooling"
Invoke-Checked -Cmd $venvPython -CommandArgs @("-m", "pip", "install", "-r", $requirementsFile) -Step "Install project dependencies"

$envFile = Join-Path $root ".env"
$envExampleFile = Join-Path $root ".env.example"
if (-not (Test-Path $envFile) -and (Test-Path $envExampleFile)) {
    Copy-Item -Path $envExampleFile -Destination $envFile
    Write-Host "[STEP] Created .env from .env.example"
}

Write-Host ""
Write-Host "Setup completed successfully."
Write-Host "Activate venv: .\\$VenvName\\Scripts\\Activate.ps1"
Write-Host "Run CLI:      python scripts\\shioaji_cli.py --help"
