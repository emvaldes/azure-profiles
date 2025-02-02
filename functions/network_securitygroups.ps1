#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function network_securitygroups {
    $Script:NetworkSecurityGroups = (
        az network nsg list --resource-group $ResourceGroupName `
        | ConvertFrom-Json
    ) ;
    if ( $Verbose ) {
        Write-Host "`nListing Network Security Groups: " `
                   -ForegroundColor Cyan ;
        $NetworkSecurityGroups | Format-Table name, location ;
    } ;
    ## return 0 ;
} ;
