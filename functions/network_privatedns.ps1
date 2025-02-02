#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function network_privatedns {
    ## List only private DNS zones in the specified resource group and filter for PostgreSQL
    $PrivateDnsZones = (
        az network private-dns zone list --resource-group $ResourceGroupName `
                                         --output json `
        | ConvertFrom-Json
    );
    $PrivateLink = "privatelink.postgres.database.azure.com" ;
    ## Filter for the specific Private Link used for PostgreSQL
    $TargetZone = $PrivateDnsZones | Where-Object {
        $_.name -eq $PrivateLink
    } ;
    if ( $TargetZone ) {
        if ( $Networking ) {
            Write-Host "`nListing Private DNS Zone: " `
                         -ForegroundColor Cyan ;
            $TargetZone ;
        } ;
    } else {
        Write-Warning "No Private DNS Zone found for ${PrivateLink} in ${ResourceGroupName}" ;
        exit 0 ;
    } ;
    $Script:PrivateDnsRecords = (
        az network private-dns record-set a list --zone-name $PrivateLink `
                                                 --resource-group $ResourceGroupName `
                                                 --output json `
        | ConvertFrom-Json
    ) ;
    $Script:TargetDNSRecord = $PrivateDNSRecords | Where-Object {
        $_.name -match $PostgresServer.Name -and `
        $_.name -notmatch "replica"
    } ;
    ## if ( $Verbose ) {
        Write-Host "`nListing Private DNS Record: " `
                   -ForegroundColor Cyan ;
        $TargetDNSRecord ;
        Write-Host "Found Private DNS Record: $( $TargetDNSRecord.name )" ;
        Write-Host "Private IP Address: $( $TargetDNSRecord.aRecords.ipv4Address )" ;
    ## } ;
    ## return 0 ;
} ;
