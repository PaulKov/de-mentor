$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Push-Location $repoRoot
try {
    & docker compose -f labs/flink-iceberg/compose.yaml up -d --build --wait
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & docker compose -f labs/flink-iceberg/compose.yaml ps
} finally {
    Pop-Location
}
