param(
    [switch]$RemoveVolumes
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Push-Location $repoRoot
try {
    $composeArgs = @('-f', 'labs/flink-iceberg/compose.yaml', 'down')
    if ($RemoveVolumes) {
        $answer = Read-Host 'This permanently deletes SeaweedFS objects, Lakekeeper and Hive Metastore metadata, Nessie refs, Kafka data, and checkpoints. Type DELETE to continue'
        if ($answer -cne 'DELETE') {
            Write-Host 'Reset cancelled. Volumes were preserved.'
            exit 1
        }
        $composeArgs += '--volumes'
    }
    & docker compose @composeArgs
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
