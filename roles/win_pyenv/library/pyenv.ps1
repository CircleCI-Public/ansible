#!powershell


$spec = @{
    options = @{
        versions = @{ type = "list"; elements = "str"; required = $true }
        default = @{ type = "str";  required = $false }
    }
    supports_check_mode = $false
}

$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)

$versions = $module.Params.versions
$default = $module.Params.default


foreach ($version in $versions)
{
    $process = start-process pyenv install $version -windowstyle Hidden -PassThru
    $handle = $process.Handle
    $process.WaitForExit();


    if ($process.ExitCode -ne 0) {
        $msg = "Problem installing Python version: '$version'"
        $module.FailJson($msg, $_)
        Write-Warning $msg
    }
}

if ($default) {
    $process = start-process pyenv global $default -windowstyle Hidden -PassThru
    $handle = $process.Handle
    $process.WaitForExit();

    if ($process.ExitCode -ne 0) {
        $msg = "Problem setting default python"
        $module.FailJson($msg, $_)
        Write-Warning $msg
    }
}

$proc = start-process pyenv rehash -windowstyle Hidden -PassThru
$han = $proc.Handle
$proc.WaitForExit();


    if ($proc.ExitCode -ne 0) {
        $msg = "Problem running pyenv rehash"
        $module.FailJson($msg, $_)
        Write-Warning $msg
    }

$module.Result.changed = $true
$module.ExitJson()
