#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function postgres_interfaces {
    $Script:PostgresNICs = az network nic list --resource-group $ResourceGroupName `
                         | ConvertFrom-Json `
                         | Where-Object {
                               $_.name -match "pgsql-postgres_server"
                           } ;
    ## if ( $Verbose ) {
        Write-Host "Listing Network Private End-Points: `n" `
                   -ForegroundColor Cyan ;
        $PostgresNICs | ForEach-Object {
            Write-Host "$( $_.ipConfigurations.privateIPAddress )`t$( $_.name )" ;
        } ;
    ## } ;
    ## return 0 ;
};
