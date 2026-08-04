# sir9tui launcher — PowerShell. Built by Nenifix.
Set-Location $PSScriptRoot
$py = Get-Command python3 -ErrorAction SilentlyContinue
if ($py) { & python3 -m sir9tui.main } else { & python -m sir9tui.main }
