#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function private_endpoints_matches {
    $Script:MatchingEndpoint = $PrivateEndpoints | Where-Object { $_.privateLinkServiceConnections[0].privateLinkServiceId -eq $PostgresServer.Id } ;
    if ( $Verbose ) {
        Write-Host "`nMatching Private Endpoint: " `
                     -ForegroundColor Cyan ;
        $MatchingEndpoint | Format-Table name, subnet.id ;
    } ;
    ## return 0 ;
} ;
