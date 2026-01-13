$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Starting Docker containers..." -ForegroundColor Cyan
docker compose up -d --build

Write-Host "Applying migrations..." -ForegroundColor Cyan
& "$root\\scripts\\migrate.ps1"

$frontendPath = Join-Path $root "frontend"
$npmCmd = $null
$npmCommand = Get-Command npm -ErrorAction SilentlyContinue
if ($npmCommand) {
    $npmCmd = $npmCommand.Source
}
if (-not $npmCmd) {
    $npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($npmCommand) {
        $npmCmd = $npmCommand.Source
    }
}
if (-not $npmCmd) {
    $defaultNpm = Join-Path $env:ProgramFiles "nodejs\\npm.cmd"
    if (Test-Path $defaultNpm) {
        $npmCmd = $defaultNpm
    }
}
if (-not $npmCmd -and $env:ProgramFiles -and (Test-Path "$env:ProgramFiles (x86)\\nodejs\\npm.cmd")) {
    $npmCmd = "$env:ProgramFiles (x86)\\nodejs\\npm.cmd"
}
if (-not $npmCmd) {
    throw "npm not found in PATH. Close/reopen PowerShell after installing Node, then retry."
}

$nodeCmd = $null
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCommand) {
    $nodeCmd = $nodeCommand.Source
}
if (-not $nodeCmd) {
    $defaultNode = Join-Path $env:ProgramFiles "nodejs\\node.exe"
    if (Test-Path $defaultNode) {
        $nodeCmd = $defaultNode
    }
}
if (-not $nodeCmd -and $env:ProgramFiles -and (Test-Path "$env:ProgramFiles (x86)\\nodejs\\node.exe")) {
    $nodeCmd = "$env:ProgramFiles (x86)\\nodejs\\node.exe"
}
if ($nodeCmd) {
    $nodeDir = Split-Path -Parent $nodeCmd
    $env:PATH = "$nodeDir;$env:PATH"
}
if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    Push-Location $frontendPath
    try {
        & $npmCmd install
    } finally {
        Pop-Location
    }
}

Write-Host "Starting frontend dev server..." -ForegroundColor Cyan
$escapedNpm = $npmCmd.Replace("'", "''")
$escapedFrontend = $frontendPath.Replace("'", "''")
$command = "cd '$escapedFrontend'; & '$escapedNpm' run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $command

Write-Host ""
Write-Host "Backend: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green

Start-Process "http://localhost:5173"
