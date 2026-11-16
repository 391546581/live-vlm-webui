param(
    [string]$Model = "qwen2.5vl:7b",
    [int]$Port = 8090,
    [switch]$LocalhostHttp
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Create .venv and install the project first. See README.md Native Windows setup."
}

$env:PYTHONUTF8 = "1"
$env:NO_PROXY = (@($env:NO_PROXY, "localhost", "127.0.0.1", "::1") |
    Where-Object { $_ }) -join ","
$env:no_proxy = $env:NO_PROXY

$arguments = @(
    "-m", "live_vlm_webui.server",
    "--host", "127.0.0.1",
    "--port", "$Port",
    "--api-base", "http://127.0.0.1:11434/v1",
    "--model", $Model
)
if ($LocalhostHttp) {
    $arguments += "--localhost-http"
}
& $python @arguments
exit $LASTEXITCODE
