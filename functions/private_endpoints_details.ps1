#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function private_endpoints_details {
    $Script:PostgresPrivateEndpoints = $PrivateEndpoints | Where-Object {
        $_.privateLinkServiceConnections[0].privateLinkServiceId -match $PostgresServer.Id -and
        $_.name -notmatch "replica"
    } ;
    if ( $Verbose ) {
        Write-Host "Listing PostgreSQL Private End-Points: " `
                   -ForegroundColor Cyan ;
        $PostgresPrivateEndpoints | Select-Object name, subnet, privateLinkServiceConnections | Format-List
    } ;
    ## return 0 ;
} ;
