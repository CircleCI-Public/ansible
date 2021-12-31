#!powershell

# Disables IE ESC

function Disable-IEESC {
    $AdminKey = "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37EF-4b3f-8CFC-4F3A74704073}"
    $UserKey = "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A8-37EF-4b3f-8CFC-4F3A74704073}"
    Set-ItemProperty -Path $AdminKey -Name "IsInstalled" -Value 0
    Set-ItemProperty -Path $UserKey -Name "IsInstalled" -Value 0

    $explorer = Get-Process Explorer -ErrorAction SilentlyContinue
    if ($explorer) {
        # try gracefully first
        $explorer.CloseMainWindow()
        # kill after five seconds
        Sleep 5
        if (!$explorer.HasExited) {
            $explorer | Stop-Process -Force
        }
        Write-Host "IE Enhanced Security Configuration (ESC) has been disabled."
    } else {
        Write-Host "Explorer is currently not running"
    }

}

Disable-IEESC