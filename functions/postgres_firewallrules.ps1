#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function postgres_firewallrules {
    $Script:FirewallRules = az postgres server firewall-rule list --server-name $PostgresServer.Name --resource-group $ResourceGroupName | ConvertFrom-Json ;
    if ( $Verbose ) {
        Write-Host "`nPostgreSQL Firewall rules: " `
                   -ForegroundColor Cyan ;
        $FirewallRules | Format-Table name, startIpAddress, endIpAddress ;
    } ;
    ## return 0 ;
} ;
