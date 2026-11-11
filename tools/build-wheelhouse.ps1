<#
.SYNOPSIS
  ONLINE machine: download every package this project needs into a folder ("wheelhouse")
  that can be copied to offline machines (USB stick, network share, Gitea release...).

.DESCRIPTION
  The Python version of filling Verdaccio's storage before going offline.
  [BEGINNER] A wheel (.whl) is a ready-to-install Python package, like the .tgz in npm's cache.
  [ADVANCED] Some wheels contain compiled code (pydantic_core, pymongo, MarkupSafe), so they
  only work on ONE operating system + CPU + Python version. That is why the target platform
  and Python version are parameters: the wheelhouse must match the OFFLINE machines, not this
  one. Run the script once per platform if the lab is mixed; one folder can hold them all.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\build-wheelhouse.ps1
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\build-wheelhouse.ps1 -Platform manylinux2014_x86_64 -Zip
#>
param(
  # Python version of the OFFLINE machines (major.minor).
  [string]$PythonVersion = "3.14",
  # Wheel platform tag: win_amd64 | manylinux2014_x86_64 | macosx_11_0_arm64 ...
  [string]$Platform = "win_amd64",
  [string]$Out = "wheelhouse",
  # Also write wheelhouse-<platform>-py<version>.zip, one file to copy.
  [switch]$Zip,
  # Python used to RUN pip here (any version works; it only downloads).
  [string]$Python = "python"
)
$ErrorActionPreference = "Stop"
# Run from the repo root, wherever the script was started from.
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "Downloading wheels for Python $PythonVersion on $Platform into $Out\"
# [BEGINNER] pip download = npm cache add: fetch packages (and everything they depend on)
# without installing them.
# [ADVANCED] --only-binary=:all: is REQUIRED with --platform/--python-version: pip cannot
# build source packages for another platform, so only finished wheels are accepted.
# [ADVANCED] --ignore-requires-python: Beanie 2.2.0 (the newest release) declares
# Requires-Python <3.14. It is pure Python and the whole test suite passes on 3.14, so the
# limit is ignored here AND in tools\install-offline.ps1.
& $Python -m pip download -r requirements-dev.txt -d $Out `
  --only-binary=:all: --platform $Platform --python-version $PythonVersion --implementation cp `
  --ignore-requires-python --disable-pip-version-check
if ($LASTEXITCODE -ne 0) { throw "pip download failed" }

# pip itself, as a wheel: lets tools\install-offline.ps1 repair a Python that has no pip.
& $Python -m pip download pip -d $Out --only-binary=:all: --no-deps --disable-pip-version-check
if ($LASTEXITCODE -ne 0) { throw "pip download pip failed" }

$count = (Get-ChildItem $Out -Filter *.whl).Count
Write-Host "$count wheels in $Out\"

if ($Zip) {
  $zipName = "wheelhouse-$Platform-py$PythonVersion.zip"
  Compress-Archive -Path "$Out\*" -DestinationPath $zipName -Force
  Write-Host "Wrote $zipName (copy it next to the repo on the offline machine and unzip it as $Out\)"
}
