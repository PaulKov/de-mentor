param(
    [string]$InputFile = 'labs/flink-iceberg/data/orders.jsonl'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Push-Location $repoRoot
try {
    $resolvedInput = (Resolve-Path -LiteralPath $InputFile).Path
    Get-Content -LiteralPath $resolvedInput | & docker compose -f labs/flink-iceberg/compose.yaml exec -T kafka `
        /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic orders
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
