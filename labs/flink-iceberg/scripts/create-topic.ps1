$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Push-Location $repoRoot
try {
    & docker compose -f labs/flink-iceberg/compose.yaml exec kafka `
        /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 `
        --create --if-not-exists --topic orders --partitions 1 --replication-factor 1
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
