# [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Set-ExecutionPolicy -ExecutionPolicy Unrestricted
# Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction Stop
Install-PackageProvider -Name NuGet -Force
Install-Module PowerShellGet -Force -AllowClobber -Confirm:$false
# Set-Variable -Name 'ConfirmPreference' -Value 'None' -Scope Global
#Install-Package -Name PackageManagement -Force 
#Install-Package -Name PowershellGet -Force -Verbose 
