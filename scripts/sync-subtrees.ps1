param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('pull', 'push')]
    [string]$Direction = 'pull',

    [Parameter(Mandatory = $false)]
    [ValidateSet('bot', 'api', 'api/ml', 'all')]
    [string]$Only = 'all'
)

$ErrorActionPreference = 'Stop'

# Порядок важен:
#   pull: сначала листья (bot, api/ml), затем api (он содержит ml как файлы).
#   push: то же — сначала api/ml → fedor-ml, затем api → fedor-api,
#         чтобы fedor-api не получил устаревший ml из api-subtree.
$pairs = @(
    @{ prefix = 'bot';    remote = 'fedor-bot' },
    @{ prefix = 'api/ml'; remote = 'fedor-ml'  },
    @{ prefix = 'api';    remote = 'fedor-api' }
)

if ($Only -ne 'all') {
    $pairs = $pairs | Where-Object { $_.prefix -eq $Only }
}

foreach ($p in $pairs) {
    $prefix = $p.prefix
    $remote = $p.remote
    Write-Host ""
    Write-Host "=== $Direction $prefix <-> $remote/main ===" -ForegroundColor Cyan

    if ($Direction -eq 'pull') {
        git subtree pull --prefix=$prefix $remote main --squash
    } else {
        git subtree push --prefix=$prefix $remote main
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Ошибка при $Direction для $prefix" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host ""
Write-Host "Готово." -ForegroundColor Green
