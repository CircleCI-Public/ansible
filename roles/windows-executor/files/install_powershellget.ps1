[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction Stop
Set-Variable -Name 'ConfirmPreference' -Value 'None' -Scope Global
Install-Package -Name PackageManagement -Force -Confirm:$false
Install-Package -Name PowershellGet -Force -Verbose -Confirm:$false
