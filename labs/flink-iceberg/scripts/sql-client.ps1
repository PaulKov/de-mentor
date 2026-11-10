$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Push-Location $repoRoot
try {
    & docker compose -f labs/flink-iceberg/compose.yaml exec flink-sql-client `
        /opt/flink/bin/sql-client.sh -i /workspace/labs/flink-iceberg/sql/01-catalogs.sql
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
