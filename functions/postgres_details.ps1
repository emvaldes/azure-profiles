#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function az__postgres_details {
    try {
        # Key Differences in Returned Object:
        # Property (PowerShell)     Equivalent in az postgres server show
        # fullyQualifiedDomainName  .fullyQualifiedDomainName
        # Location                  .location
        # AdministratorLogin        .administratorLogin
        # Version                   .version
        # Sku.Name                  .sku.name
        # StorageProfile.StorageMB  .storageProfile.storageMB
        # SslEnforcement            .sslEnforcement (Deprecated in Flexible Server)
        # UserVisibleState          .userVisibleState
        ## Retrieve details of the specified Azure PostgreSQL server.
        $Script:PostgresServer = az postgres server show --name $Script:PostgresServerName `
                                                         --resource-group $Script:ResourceGroupName `
                                                         --subscription $Script:SubscriptionId `
                                                         --output json `
                               | ConvertFrom-Json ;
        if ( $PostgresServer -and $Verbose ) {
            $MessageScope = "PostgreSQL Server details" ;
            if ( $PostgresServer ) {
                ## Output the retrieved PostgreSQL server details to the console for verification.
                Write-Host "`nListing ${MessageScope}: " `
                           -ForegroundColor Cyan ;
                $PostgresServer ;
            } else {
                Write-Host "Unable to retrieve ${MessageScope}!" ;
                exit 0 ;
            } ;
        } ;
    }
    catch { exit 0 ; }
    finally {} ;
    ## Set the PostgreSQL server's fully qualified domain name (FQDN) as an environment variable.
    ## This allows other commands or scripts to reference the PostgreSQL host without hardcoding its value.
    $env:POSTGRES_HOST = $PostgresServer.fullyQualifiedDomainName ;
    ## return 0 ;
} ;

function ps__postgres_details {
    try {
        ## Retrieve details of the specified Azure PostgreSQL server.
        ## This command fetches the PostgreSQL server instance using its name, resource group, and subscription ID.
        $Script:PostgresServer = Get-AzPostgreSqlServer -Name $PostgresServerName `
                                                        -ResourceGroupName $ResourceGroupName `
                                                        -SubscriptionId $SubscriptionId ;
        if ( $PostgresServer -and $Verbose ) {
            $MessageScope = "PostgreSQL Server details" ;
            if ( $PostgresServer ) {
                ## Output the retrieved PostgreSQL server details to the console for verification.
                Write-Host "`nListing ${MessageScope}: " `
                           -ForegroundColor Cyan ;
                $PostgresServer ;
            } else {
                Write-Host "Unable to retrieve ${MessageScope}!" ;
                exit 0 ;
            } ;
        } ;
    }
    catch { exit 0 ; }
    finally {} ;
    ## Set the PostgreSQL server's fully qualified domain name (FQDN) as an environment variable.
    ## This allows other commands or scripts to reference the PostgreSQL host without hardcoding its value.
    $env:POSTGRES_HOST = $PostgresServer.FullyQualifiedDomainName ;
    ## return 0 ;
} ;
