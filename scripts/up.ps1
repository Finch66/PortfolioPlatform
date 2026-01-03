param(
    [switch]$Build
)

 $ErrorActionPreference = "Stop"
 $root = Split-Path -Parent $PSScriptRoot
 Set-Location $root

if ($Build) {
    docker compose up --build
} else {
    docker compose up
}
