$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# Se non è definito, usa il DB del compose esposto su localhost.
if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/transactions"
}

$alembicPath = Join-Path $root ".venv/Scripts/alembic.exe"
if (-not (Test-Path $alembicPath)) {
    $alembicPath = "alembic"
}

Push-Location "services/transaction"
try {
    & $alembicPath upgrade head
} finally {
    Pop-Location
}
