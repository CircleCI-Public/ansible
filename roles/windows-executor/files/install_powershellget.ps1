[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

Install-PackageProvider -Name NuGet -Force
Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction Stop
Register-PSRepository -Default
Install-Module -Name PowerShellGet -RequiredVersion 2.2.5 -Force
Update-Module -Name PowerShellGet
