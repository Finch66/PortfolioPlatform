$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

cd services/transaction
$pytestPath = Join-Path $root ".venv/Scripts/pytest.exe"
if (-not (Test-Path $pytestPath)) {
    $pytestPath = "pytest"
}
& $pytestPath
