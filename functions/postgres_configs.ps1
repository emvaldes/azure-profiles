#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function postgres_configs {
    ## Set the PostgreSQL server's fully qualified domain name (FQDN) as an environment variable.
    ## This allows other commands or scripts to reference the PostgreSQL host without hardcoding its value.
    $env:POSTGRES_HOST = $PostgresServer.FullyQualifiedDomainName ;
    try {
        ## Retrieve detailed information about the specified Azure PostgreSQL server using Azure CLI.
        ## The command fetches the PostgreSQL server details by name and resource group.
        ## The JSON output is then converted into a PowerShell object for easier manipulation.
        $Script:PostgresInfo = az postgres server show --name $PostgresServer.Name `
                                                       --resource-group $ResourceGroupName `
                             | ConvertFrom-Json ;
        if ( $Verbose ) {
            $MessageScope = "PostgreSQL Server configuration" ;
            if ( $PostgresInfo ) {
                ## Output the retrieved PostgreSQL server information to the console for verification.
                Write-Host "Listing ${MessageScope}: " `
                           -ForegroundColor Cyan ;
                $PostgresInfo ;
            } else {
                Write-Host "Unable to retrieve ${MessageScope}!" ;
                exit 0 ;
            } ;
        } ;
    }
    catch { exit 0 ; }
    finally {} ;
    ## return 0 ;
} ;
