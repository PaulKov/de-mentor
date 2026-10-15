param(
    [string]$InputFile = 'labs/flink-iceberg/data/orders.jsonl'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Push-Location $repoRoot
try {
    $resolvedInput = (Resolve-Path -LiteralPath $InputFile).Path
    Get-Content -LiteralPath $resolvedInput | ForEach-Object {
        $line = $_
        $event = $line | ConvertFrom-Json
        if ($event.order_id -eq 'o-late-001') {
            # Let the 5-second source idle timeout advance the watermark first.
            Start-Sleep -Seconds 6
        }
        $line
    } | & docker compose -f labs/flink-iceberg/compose.yaml exec -T kafka `
        /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka:29092 --topic orders
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
