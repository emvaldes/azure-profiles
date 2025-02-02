#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function az__keyvault_secrets {
    try {
        # Key Differences in the Returned Object
        # PowerShell (Get-AzKeyVaultSecret)             Az CLI (az keyvault secret list)
        # Returns an array of secret objects            Returns an array of JSON objects
        # Contains SecretValue (SecureString)           Does NOT return secret values directly
        # Use Get-AzKeyVaultSecret -Name to get values  Must use az keyvault secret show separately to get values
        ## Retrieve all secrets stored in the specified Azure Key Vault.
        $Script:Secrets = az keyvault secret list --vault-name $VaultName `
                                                  --query "[].name" `
                        | ConvertFrom-Json ;
        $MessageScope = "Azure Key-Vault '${VaultName}' secrets" ;
        if ( $Secrets ) {
            if ( $KeyVault ) {
                Write-Host "Listing ${MessageScope}: " `
                           -ForegroundColor Cyan ;
                ## Iterate through each secret in the Key Vault.
                foreach ( $SecretName in $Script:Secrets ) {
                    ## Fetch the latest version of the secret.
                    $SecretVersion = az keyvault secret list-versions --vault-name $VaultName `
                                                                      --name $SecretName `
                                                                      --query "[0].id" `
                                                                      --output tsv ;
                    ## Retrieve the latest value of the secret in plain text format.
                    $SecretValue = az keyvault secret show --vault-name $VaultName `
                                                           --name $SecretName `
                                                           --query "value" `
                                                           --output tsv ;
                    ## Output the secret name along with its retrieved value for verification.
                    Write-Host "`nSecret: ${SecretName}`n Value: ${SecretValue}" ;
                } ;
                Write-Host ;
            } ;
        } else {
            Write-Host "Unable to retrieve ${MessageScope}!" ;
            exit 0 ;
        } ;
    }
    catch { exit 0 ; }
    finally {} ;
    ## return 0 ;
} ;

function ps__keyvault_secrets {
    try {
        ## Retrieve all secrets stored in the specified Azure Key Vault.
        $Script:Secrets = Get-AzKeyVaultSecret -VaultName $VaultName ;
        $MessageScope = "Azure Key-Vault '${VaultName}' secrets" ;
        if ( $Secrets ) {
            if ( $KeyVault ) {
                Write-Host "Listing ${MessageScope}: " `
                           -ForegroundColor Cyan ;
                ## Iterate through each secret in the Key Vault.
                $Secrets | ForEach-Object {
                    ## Extract the secret name from the retrieved secret object.
                    $SecretName = $_ | Select-Object -ExpandProperty Name ;
                    ## Fetching the latest version of the secret.
                    ## Retrieve the latest value of the secret in plain text format.
                    ## Legacy implementation: Lacks of versioning control.
                    ## $LatestVersion = Get-AzKeyVaultSecret -VaultName $VaultName `
                    ##                                       -Name $SecretName `
                    ##                                       -AsPlainText ;
                    $SecretVersion = (
                        Get-AzKeyVaultSecret -VaultName $VaultName `
                                             -Name $SecretName `
                                             -IncludeVersions `
                        | Sort-Object -Property Created -Descending `
                        | Select-Object -First 1
                    ).Version ;
                    $SecretValue = Get-AzKeyVaultSecret -VaultName $VaultName `
                                                        -Name $SecretName `
                                                        -Version $SecretVersion `
                                                        -AsPlaintext ;
                    ## Output the secret name along with its retrieved value for verification.
                    Write-Host "`nSecret: ${SecretName}`n Value: ${SecretValue}" ;
                } ;
                Write-Host ;
            } ;
        } else {
            Write-Host "Unable to retrieve ${MessageScope}!" ;
            exit 0 ;
        } ;
    }
    catch { exit 0 ; }
    finally {} ;
    ## return 0 ;
} ;
