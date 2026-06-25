# sir9tui PowerShell module
# Place in: Documents\PowerShell\Modules\sir9tui\sir9tui.psm1

function sir9tui {
    [CmdletBinding()]
    param()

    $appDir = 'C:\Users\ai9\Desktop\neni9\sir9tui'
    $python = 'C:\Users\ai9\AppData\Local\Microsoft\WindowsApps\python3.exe'

    if (-not (Test-Path $appDir)) {
        Write-Error "sir9tui not found at $appDir"
        return
    }

    Push-Location $appDir
    try {
        & $python app.py
    } finally {
        Pop-Location
    }
}

Export-ModuleMember -Function sir9tui
