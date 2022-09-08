Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

param 
( 
        [Parameter(Mandatory=$True,Position=1)]
        [string]$servicefabricsdk_version
)

choco install service-fabric-sdk --version $servicefabricsdk_version -y