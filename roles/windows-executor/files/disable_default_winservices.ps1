    
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

    function Disable-InternetExplorerWelcomeScreen {
        $AdminKey = "HKLM:\Software\Policies\Microsoft\Internet Explorer\Main"
        New-Item -Path $AdminKey -Value 1 -Force
        Set-ItemProperty -Path $AdminKey -Name "DisableFirstRunCustomize" -Value 1 -Force
        Write-Host "Disabled IE Welcome screen"
    }

    function Disable-UserAccessControl {
        Write-Host "Diabling User Access Control (UAC)"
        Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Type DWord -Value "0x0"
        Write-Host "User Access Control (UAC) has been disabled."
    }
    
    function Enable-LongPaths {
        Set-Itemproperty "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value "1" -Force
        Write-Host "Long Paths have been enabled."
    }
    
    function Enable-DotNet35 {
        Install-WindowsFeature Net-Framework-Core
        Get-WindowsFeature -Name Net-Framework-Core
        Write-Host ".NET Framework 3.5 has been enabled."
    }
    
    function Disable-NetworkWizard {
        New-Item -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Network\NewNetworkWindowOff" -Force
        Write-Host "Network Wizard Window has been disabled."
    }

    function Disable-PasswordComplexity {
        Install-Module MSOnline
        Get-MsolUser | Set-MsolUser -StrongPasswordRequired $false
    }

    

    switch ($args[0]) {
        Disable-IEESC {
            Write-Host "Called Disable-IEESC()"
        }
        Disable-InternetExplorerWelcomeScreen {
            Write-Host "Called Disable-InternetExplorerWelcomeScreen()"
        }
        Disable-UserAccessControl {
            Write-Host "Called Disable-UserAccessControl()"
        }
        Enable-LongPaths {
            Write-Host "Called Enable-LongPaths()"
        }
        Enable-DotNet35 {
            Write-Host "Called Enable-DotNet35()"
        }
        Disable-NetworkWizard {
            Write-Host "Called Disable-NetworkWizard()"
        }
        Disable-PasswordComplexity {
            Write-Host "Called Disable-PasswordComplexity()"
        }
    }

    

