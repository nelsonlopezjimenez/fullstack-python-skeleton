<#
.SYNOPSIS
  OFFLINE machine: create .venv and install everything from the wheelhouse folder.
  No internet is used: pip is told --no-index (never contact PyPI).

.DESCRIPTION
  Steps (each one prints what it does):
    1. find Python 3.13 (the py launcher first, then python on the PATH)
    2. create .venv (the Python version of node_modules)
    3. make sure .venv has pip; if not, install pip from the wheel in the wheelhouse
    4. install requirements-dev.txt from the wheelhouse only
    5. copy .env.example to .env if there is no .env yet

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\install-offline.ps1
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\install-offline.ps1 -Wheelhouse D:\wheelhouse
#>
param(
  [string]$Wheelhouse = "wheelhouse",
  [string]$PythonVersion = "3.13"
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$Wheelhouse = (Resolve-Path $Wheelhouse).Path

# [ADVANCED] Runs a program only to see whether it succeeds, hiding its output. In Windows
# PowerShell 5.1 a redirected stderr line counts as an error, and with "Stop" above it would
# end the script, so the preference is relaxed here only.
function Test-Command([string]$Exe, [string[]]$Arguments) {
  $saved = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try { & $Exe @Arguments *> $null; return ($LASTEXITCODE -eq 0) }
  catch { return $false }
  finally { $ErrorActionPreference = $saved }
}

# --- 1. Find Python --------------------------------------------------------------------------
# [BEGINNER] On Windows, "py" is the Python launcher installed by the python.org installer.
# `py -0p` lists every Python on the machine; `py -3.13` picks that version.
$pyExe = $null
$pyArgs = @()
$versionCheck = "import sys; sys.exit(0 if f'{sys.version_info[0]}.{sys.version_info[1]}' == '$PythonVersion' else 1)"
if ((Get-Command py -ErrorAction SilentlyContinue) -and (Test-Command py @("-$PythonVersion", "--version"))) {
  $pyExe = "py"; $pyArgs = @("-$PythonVersion")
} elseif ((Get-Command python -ErrorAction SilentlyContinue) -and (Test-Command python @("-c", $versionCheck))) {
  $pyExe = "python"
}
if (-not $pyExe) {
  throw "Python $PythonVersion not found. Install it with the python.org installer (it works offline), see instructions\offline-setup.md"
}
Write-Host "1. Using Python: $pyExe $pyArgs"

# --- 2. Create the virtual environment ------------------------------------------------------
if (-not (Test-Path .venv\Scripts\python.exe)) {
  Write-Host "2. Creating .venv"
  # [ADVANCED] venv calls ensurepip, which installs the pip wheel that ships INSIDE Python,
  # so this step needs no internet either. Some builds remove ensurepip; then step 3 repairs it.
  if (-not (Test-Command $pyExe ($pyArgs + @("-m", "venv", ".venv")))) {
    Write-Host "   venv with pip failed; creating it without pip"
    & $pyExe @pyArgs -m venv --without-pip .venv
    if ($LASTEXITCODE -ne 0) { throw "could not create .venv" }
  }
} else {
  Write-Host "2. .venv already exists"
}
$venvPython = (Resolve-Path .venv\Scripts\python.exe).Path

# --- 3. Make sure pip works ------------------------------------------------------------------
if (-not (Test-Command $venvPython @("-m", "pip", "--version"))) {
  Write-Host "3. No pip in .venv: installing it from the wheelhouse"
  $pipWheel = Get-ChildItem $Wheelhouse -Filter "pip-*.whl" | Select-Object -First 1
  if (-not $pipWheel) { throw "no pip-*.whl in $Wheelhouse (tools\build-wheelhouse.ps1 adds one)" }
  # [ADVANCED] A wheel is a zip file, and Python can import code straight out of a zip. With
  # the wheel on PYTHONPATH, `python -m pip` runs pip FROM the wheel and installs that same
  # wheel into .venv: pip installs itself. (On Windows pip insists on the `-m pip` form when
  # it installs pip, so the shorter "python pip.whl/pip install ..." trick is refused.)
  $env:PYTHONPATH = $pipWheel.FullName
  try { & $venvPython -m pip install --no-index $pipWheel.FullName }
  finally { Remove-Item Env:PYTHONPATH }
  if ($LASTEXITCODE -ne 0) { throw "could not install pip from $($pipWheel.Name)" }
} else {
  Write-Host "3. pip is available"
}

# --- 4. Install the project's packages -------------------------------------------------------
Write-Host "4. Installing requirements-dev.txt from $Wheelhouse (no internet)"
# [BEGINNER] --no-index: never contact PyPI. --find-links: look for wheels in this folder.
# This is `npm install --offline` with the cache in a folder you can see.
& $venvPython -m pip install --no-index --find-links $Wheelhouse -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "pip install failed (is the wheelhouse for this Python version and platform?)" }

# --- 5. Settings -----------------------------------------------------------------------------
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "5. Created .env from .env.example (set JWT_SECRET)"
} else {
  Write-Host "5. .env already exists"
}

Write-Host ""
Write-Host "Done. Next:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python -m pytest"
Write-Host "  python -m uvicorn app.main:app --reload --port 8000"
