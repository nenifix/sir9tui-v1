# sir9tui PowerShell module — Built by Nenifix
# Place in: Documents\PowerShell\Modules\sir9tui\sir9tui.psm1
# Portable: uses the repo's own python (portable bundle) or system python3.

function sir9tui {
    [CmdletBinding()]
    param()

    # Prefer a bundled portable python in the same folder tree.
    $here = $PSScriptRoot
    $candidates = @(
        (Join-Path $here 'python.exe'),
        (Join-Path (Split-Path $here -Parent) 'python.exe'),
        (Get-Command python3 -ErrorAction SilentlyContinue).Source,
        (Get-Command python -ErrorAction SilentlyContinue).Source
    )

    $py = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
    if (-not $py) {
        Write-Error "sir9tui needs a Python interpreter. Install Python 3.11+ from python.org"
        return
    }

    Push-Location (Split-Path $here -Parent)  # repo root: Desktop/neni9/sir9tui
    try {
        & $py -m sir9tui.main
    } finally {
        Pop-Location
    }
}

Export-ModuleMember -Function sir9tui
