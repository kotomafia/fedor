param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$dockerPaths = @(
    (Get-Command docker -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
    "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe",
    "${env:ProgramFiles(x86)}\Docker\Docker\resources\bin\docker.exe",
    "$env:LOCALAPPDATA\Programs\Docker\Docker\resources\bin\docker.exe"
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique -First 1

if (-not $dockerPaths) {
    Write-Host ""
    Write-Host "Docker не найден." -ForegroundColor Red
    Write-Host "  1. Установите Docker Desktop: https://www.docker.com/products/docker-desktop/"
    Write-Host "  2. Запустите Docker Desktop и дождитесь статуса Running"
    Write-Host "  3. Перезапустите Cursor (чтобы обновился PATH)"
    Write-Host ""
    exit 1
}

& $dockerPaths compose @ComposeArgs
exit $LASTEXITCODE
