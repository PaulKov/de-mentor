param(
    [switch]$Recreate
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Push-Location $repoRoot
try {
    if ($Recreate) {
        & docker compose -f labs/flink-iceberg/compose.yaml exec kafka `
            /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:29092 `
            --delete --if-exists --topic orders
        if ($LASTEXITCODE -ne 0) { throw 'Could not delete topic orders' }

        $deadline = (Get-Date).AddSeconds(15)
        do {
            Start-Sleep -Milliseconds 500
            $topics = & docker compose -f labs/flink-iceberg/compose.yaml exec -T kafka `
                /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:29092 --list
            if ($LASTEXITCODE -ne 0) { throw 'Could not list Kafka topics' }
        } while (($topics -contains 'orders') -and (Get-Date) -lt $deadline)
        if ($topics -contains 'orders') { throw 'Timed out waiting for topic orders to be deleted' }
    }

    & docker compose -f labs/flink-iceberg/compose.yaml exec kafka `
        /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:29092 `
        --create --if-not-exists --topic orders --partitions 1 --replication-factor 1
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
