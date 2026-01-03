$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

param(
    [switch]$Build
)

if ($Build) {
    docker compose up --build
} else {
    docker compose up
}
