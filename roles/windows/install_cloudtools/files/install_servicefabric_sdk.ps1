Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
$servicefabricsdk_version = $args[1]
choco install service-fabric-sdk --version $servicefabricsdk_version -y --force
