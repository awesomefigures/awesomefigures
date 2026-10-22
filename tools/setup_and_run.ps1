#Requires -Version 5.1
<#
.SYNOPSIS
    Prepare the Conda environment, test the library, render all notebooks and build Sphinx.
.EXAMPLE
    .\tools\setup_and_run.ps1
.EXAMPLE
    .\tools\setup_and_run.ps1 -Serve
.EXAMPLE
    .\tools\setup_and_run.ps1 -CommitOutputs -Push
#>
[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z][A-Za-z0-9_-]*$')]
    [string]$EnvName = "awesomefigures",

    [ValidateRange(1, 3600)]
    [int]$NotebookTimeout = 300,

    [switch]$SkipNotebooks,
    [switch]$Serve,

    [ValidateRange(1024, 65535)]
    [int]$Port = 8765,

    [switch]$CommitOutputs,
    [switch]$Push
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    Write-Host ""
    Write-Host ("> " + $Command + " " + ($Arguments -join " ")) -ForegroundColor Cyan
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command failed with exit code $LASTEXITCODE."
    }
}

function Invoke-InEnvironment {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    $argsForConda = @("run", "--no-capture-output", "-n", $EnvName, "python") + $Arguments
    Invoke-Checked -Command "conda" -Arguments $argsForConda
}

if ($Push -and -not $CommitOutputs) {
    throw "-Push requires -CommitOutputs. Nothing is pushed by default."
}

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "Conda is unavailable. Install Miniforge/Miniconda, initialize PowerShell with conda init powershell, then reopen the shell."
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$OriginalLocation = (Get-Location).Path
$PreviousExecutionMode = [Environment]::GetEnvironmentVariable(
    "AWESOMEFIGURES_NB_EXECUTION", "Process"
)

try {
    Set-Location $RepoRoot
    Write-Host "Repository: $RepoRoot" -ForegroundColor Green
    Write-Host "Conda environment: $EnvName" -ForegroundColor Green

    $envListText = (& conda env list --json | Out-String)
    if ($LASTEXITCODE -ne 0) {
        throw "Could not query Conda environments."
    }
    $envList = $envListText | ConvertFrom-Json
    $exists = @($envList.envs | Where-Object {
        (Split-Path -Path $_ -Leaf) -eq $EnvName
    }).Count -gt 0

    if ($exists) {
        Write-Host "Updating existing Conda environment..." -ForegroundColor Yellow
        Invoke-Checked -Command "conda" -Arguments @(
            "env", "update", "--name", $EnvName,
            "--file", "environment.yml", "--prune"
        )
    }
    else {
        Write-Host "Creating Conda environment..." -ForegroundColor Yellow
        Invoke-Checked -Command "conda" -Arguments @(
            "env", "create", "--name", $EnvName, "--file", "environment.yml"
        )
    }

    # Single source of truth: requirements.txt uses pyproject.toml extras.
    Invoke-InEnvironment -Arguments @("-m", "pip", "install", "-r", "requirements.txt")
    Invoke-InEnvironment -Arguments @("-m", "pip", "check")
    Invoke-InEnvironment -Arguments @("-c",
        "import awesomefigures as af; print('awesomefigures', af.__version__)")

    Write-Host ""
    Write-Host "=== PYTEST ===" -ForegroundColor Green
    Invoke-InEnvironment -Arguments @("-m", "pytest", "-q")

    if (-not $SkipNotebooks) {
        Write-Host "=== ENSURE ACCESSIBILITY PANELS ===" -ForegroundColor Green
        Invoke-InEnvironment -Arguments @("tools/enrich_notebooks.py")
        Write-Host ""
        Write-Host "=== EXECUTE AND SAVE ALL NOTEBOOKS ===" -ForegroundColor Green
        Invoke-InEnvironment -Arguments @(
            "tools/execute_notebooks.py", "--timeout", "$NotebookTimeout"
        )

        Write-Host ""
        Write-Host "=== VERIFY EMBEDDED FIGURES ===" -ForegroundColor Green
        Invoke-InEnvironment -Arguments @("tools/verify_notebooks.py")
    }
    else {
        Write-Warning "Notebook execution skipped; only existing notebook outputs will be used."
    }

    Write-Host ""
    Write-Host "=== BUILD SPHINX ===" -ForegroundColor Green
    # Notebook outputs are saved already; avoid running them twice.
    $env:AWESOMEFIGURES_NB_EXECUTION = "off"
    Invoke-InEnvironment -Arguments @(
        "-m", "sphinx", "-W", "-b", "html",
        "docs/source", "docs/_build/html"
    )

    $IndexHtml = Join-Path $RepoRoot "docs/_build/html/index.html"
    $StudioHtml = Join-Path $RepoRoot "docs/_build/html/studio.html"
    $NotebookHtml = Join-Path $RepoRoot "docs/_build/html/notebooks/index.html"
    foreach ($file in @($IndexHtml, $StudioHtml, $NotebookHtml)) {
        if (-not (Test-Path -Path $file -PathType Leaf)) {
            throw "Sphinx completed but a required page is missing: $file"
        }
    }

    if ($CommitOutputs) {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            throw "Git is required for -CommitOutputs."
        }
        Write-Host ""
        Write-Host "=== COMMIT NOTEBOOK OUTPUTS ===" -ForegroundColor Green
        Invoke-Checked -Command "git" -Arguments @(
            "add", "--", "docs/source/notebooks/*.ipynb"
        )
        # Do not commit unrelated staged project changes.
        & git diff --cached --quiet -- "docs/source/notebooks"
        $diffCode = $LASTEXITCODE
        if ($diffCode -eq 1) {
            Invoke-Checked -Command "git" -Arguments @(
                "commit", "-m", "Update executed notebook figures",
                "--", "docs/source/notebooks"
            )
        }
        elseif ($diffCode -ne 0) {
            throw "git diff failed with exit code $diffCode."
        }
        else {
            Write-Host "Notebook outputs already committed."
        }

        if ($Push) {
            Write-Host ""
            Write-Host "=== PUSH ===" -ForegroundColor Green
            Invoke-Checked -Command "git" -Arguments @("push")
        }
    }

    Write-Host ""
    Write-Host "COMPLETE" -ForegroundColor Green
    Write-Host "Saved notebook outputs: docs/source/notebooks/*.ipynb"
    Write-Host "Sphinx homepage:        $IndexHtml"
    Write-Host "Palette Studio:         $StudioHtml"
    Write-Host "Notebook cookbook:      $NotebookHtml"
    Write-Host "To publish online: select GitHub Actions in Settings > Pages, then run the pages workflow."

    if ($Serve) {
        Write-Host ""
        Write-Host "Serving locally at http://localhost:$Port/ (Ctrl+C to stop)." -ForegroundColor Green
        Start-Process "http://localhost:$Port/"
        Invoke-InEnvironment -Arguments @(
            "-m", "http.server", "$Port", "--bind", "127.0.0.1",
            "--directory", "docs/_build/html"
        )
    }
}
finally {
    [Environment]::SetEnvironmentVariable(
        "AWESOMEFIGURES_NB_EXECUTION", $PreviousExecutionMode, "Process"
    )
    Set-Location $OriginalLocation
}
