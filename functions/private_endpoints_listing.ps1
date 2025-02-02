#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function private_endpoints_listing {
    ## Retrieve all private endpoints in the resource group
    $Script:PrivateEndpoints = az network private-endpoint list --resource-group $ResourceGroupName `
                             | ConvertFrom-Json ;
    ## Filter private endpoints that match the Postgres server
    $FilteredEndpoints = $Script:PrivateEndpoints | Where-Object {
        $_.privateLinkServiceConnections.privateLinkServiceId -eq $PostgresServer.Id ;
    } ;
    ## Display results if Verbose mode is enabled
    if ($Verbose) {
        Write-Host "Private End-Points listing: `n" `
                   -ForegroundColor Cyan ;
        ## Format the output to show only relevant details
        $FilteredEndpoints | ForEach-Object {
            [PSCustomObject]@{
                Name       = $_.name
                FQDN       = ( $_.customDnsConfigs | Select-Object -ExpandProperty fqdn ) -join ", "
                IPAddress  = ( $_.customDnsConfigs | Select-Object -ExpandProperty ipAddresses ) -join ", "
                Subnet     = $_.subnet.id
            }
        } | ConvertTo-Json ;
    } ;
    ## return 0 ;
} ;
