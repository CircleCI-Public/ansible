if( -not ( get-command Install-ChocolateyPackage -erroraction silentlycontinue ) ) {
    Write-Host "Importing chocolateyInstaller.psm1..."
    Import-Module C:\ProgramData\chocolatey\helpers\chocolateyInstaller.psm1
}

$ErrorActionPreference = "Stop"

$packageName = 'nvm'
$nodePath = "$env:SystemDrive\Program Files\nodejs"
$nvmPath = Join-Path $env:ProgramData $packageName
$NvmSettingsFile = Join-Path $nvmPath "settings.txt"

if (Test-Path $nodePath) {
    Remove-Item -Path $nodePath -Recurse -Force
} else {
    Write-Host "The path does not exist: $nodePath"
}

function install-nvm {
    param($Version)
    Invoke-WebRequest -UseBasicParsing "https://github.com/coreybutler/nvm-windows/releases/download/$Version/nvm-noinstall.zip" -o install-nvm.zip
}

install-nvm -Version $Version

Expand-Archive -Path "install-nvm.zip" -DestinationPath $nvmPath -Force

$NvmSettingsDict = [ordered]@{}
if (Test-Path $NvmSettingsFile) {
  $NvmSettings = Get-Content $NvmSettingsFile
  $NvmSettings | Foreach-Object { $NvmSettingsDict.add($_.split(':', 2)[0], $_.split(':', 2)[1]) }
  Write-Output "Detected existing settings file"
  $NvmSettingsDict.GetEnumerator() | ForEach-Object { "$($_.Name): $($_.Value)" } | Write-Verbose
}
if (!($NvmSettingsDict['root'])) { $NvmSettingsDict['root'] = $nvmPath }
if (!($NvmSettingsDict['path'])) { $NvmSettingsDict['path'] = $nodePath }
if (!($NvmSettingsDict['arch'])) { $NvmSettingsDict['arch'] = $OsBits }
if (!($NvmSettingsDict['proxy'])) { $NvmSettingsDict['proxy'] = "none" }

$NvmSettingsDict.GetEnumerator() | ForEach-Object { "$($_.Name): $($_.Value)" } | Write-Verbose
$NvmSettingsDict.GetEnumerator() | ForEach-Object { "$($_.Name): $($_.Value)" } | Out-File "$NvmSettingsFile" -Force -Encoding ascii

Install-ChocolateyEnvironmentVariable -VariableName "NVM_HOME" -VariableValue "$nvmPath" -VariableType Machine;
Install-ChocolateyEnvironmentVariable -VariableName "NVM_SYMLINK" -VariableValue "$nodePath" -VariableType Machine;

Install-ChocolateyPath -PathToInstall "%NVM_HOME%" -PathType Machine;
Install-ChocolateyPath -PathToInstall "%NVM_SYMLINK%" -PathType Machine;
