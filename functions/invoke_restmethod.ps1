#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function invoke_restmethod__deprecated {
    $AzureDomain = "management.azure.com" ;
    $URI = "https://${AzureDomain}/subscriptions/${SubscriptionId}/resourcegroups?api-version=2021-04-01" ;
    ## Example: Use AccessToken for an API request
    $Headers = @{ "Authorization" = "Bearer ${AccessToken}" }
    # Write-Host "DEBUG: AccessToken -> $( $Headers | ConvertTo-Json )" -ForegroundColor Yellow
    $Response = Invoke-RestMethod -Uri $URI `
                                  -Headers $Headers `
                                  -Method Get ;
    ## Filter the response to get only the resource group you are interested in
    $FilteredResourceGroup = $Response.value | Where-Object { $_.name -eq $ResourceGroupName } ;
    if ($FilteredResourceGroup) {
        Write-Host "`nFiltered Resource Group: " `
                   -ForegroundColor Cyan ;
        $FilteredResourceGroup | ConvertTo-Json ;
    } else {
        Write-Host "Resource group '${ResourceGroupName}' not found." `
                   -ForegroundColor Red ;
    } ;
    # return 0 ;
} ;

function invoke_restmethod {
    Write-Host "`nFiltered Resource Group: " `
               -ForegroundColor Cyan -NoNewLine ;
    ## Azure Management sub-domain
    $AzureManagement = "https://management.azure.com" ;
    $MicrosoftGraph = "https://graph.microsoft.com" ;
    ## Set API endpoint
    $Uri = "${AzureManagement}/subscriptions/${SubscriptionId}/resourcegroups?api-version=2021-04-01"
    ## Ensure correct access tokens
    $AccessTokenARM = az account get-access-token --resource $AzureManagement `
                                                  --query accessToken `
                                                  --output tsv ;
    $AccessTokenGraph = az account get-access-token --resource $MicrosoftGraph `
                                                    --query accessToken `
                                                    --output tsv ;
    ## Set Authorization headers
    $HeadersARM = @{ "Authorization" = "Bearer ${AccessTokenARM}" }
    $HeadersGraph = @{ "Authorization" = "Bearer ${AccessTokenGraph}" }
    ## Retrieve resource groups
    $Response = Invoke-RestMethod -Uri $Uri `
                                  -Headers $HeadersARM `
                                  -Method Get ;
    ## Filter for the specific resource group
    $FilteredResourceGroup = $Response.value | Where-Object {
        $_.name -eq $ResourceGroupName
    } ;
    if ( -not $FilteredResourceGroup ) {
        Write-Host "Resource group '${ResourceGroupName}' not found." `
                   -ForegroundColor Red ;
        return ;
    } ;
    ## Tags to be expanded
    $TagsToExpand = @(
        "technical_poc",
        "security_steward",
        "business_steward",
        "technical_steward"
    ) ;
    ## Process each tag if it exists
    foreach ( $Tag in $TagsToExpand ) {
        if ( $FilteredResourceGroup.tags.PSObject.Properties.Name -contains $Tag ) {
            $Entries = $FilteredResourceGroup.tags.$Tag -split "," | ForEach-Object {
                $_.Trim() ;
            } ;
            $ExpandedEntries = @() ;
            $GraphURL = "${MicrosoftGraph}/v1.0/users/" ;
            $NotFound = New-Object PSObject -Property ( [ordered]@{
                "displayName" = "Not Found" ;
                "id" = "" ;
                "mail" = "" ;
                "status" = "Unknown"
            } ) ;
            foreach ( $Entry in $Entries ) {
                ## Determine if entry is an email or UUID
                if ( $Entry -match "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$" ) {
                    $GraphUri = "${GraphURL}${Entry}" ;
                } elseif ( $Entry -match "^[0-9a-fA-F-]{36}$" ) {
                    $GraphUri = "${GraphURL}${Entry}" ;
                } else {
                    ## Unknown format, return standard structure
                    $ExpandedEntries += ( $NotFound.PSObject.Copy() | ForEach-Object {
                        $_.mail = $Entry; $_ ;
                    } ) ;
                    continue ;
                } ;
                ## Query Microsoft Graph API for full user profile
                $UserResponse = az rest --method get `
                                        --uri $GraphUri `
                                        --headers "Authorization=Bearer ${AccessTokenGraph}" `
                                        --output json 2>&1 ;
                ## Check if response contains an error or is valid JSON
                if ( $UserResponse -match '"code": "Request_ResourceNotFound"' ) {
                    Write-Host "User not found: $Entry" `
                               -ForegroundColor Yellow ;
                    $ExpandedEntries += ( $NotFound.PSObject.Copy() | ForEach-Object {
                        $_.mail = $Entry; $_ ;
                    } ) ;
                }
                elseif ( $UserResponse -match "^{" ) {
                    ## Check if response starts with '{' (valid JSON)
                    try {
                        $UserInfo = $UserResponse | ConvertFrom-Json
                        if ( $UserInfo ) {
                            ## Ensure status is always included while keeping the full profile
                            $UserStatus = if ( $UserInfo.PSObject.Properties.Name -contains "accountEnabled" ) {
                                            if ( $UserInfo.accountEnabled ) { "Active" }
                                            else { "Inactive" } ;
                                          }
                                          elseif ( $UserInfo.userPrincipalName ) { "Active" }
                                          else { "Unknown" } ;
                            ## Append "status" to the full profile and store it
                            $UserInfo | Add-Member -MemberType NoteProperty `
                                                   -Name "status" `
                                                   -Value $UserStatus `
                                                   -Force ;
                            $ExpandedEntries += $UserInfo ;
                        } else {} ;
                    }
                    catch {
                        Write-Host "Error parsing JSON response for ${Entry}" `
                                   -ForegroundColor Red ;
                        $ExpandedEntries += ( $NotFound.PSObject.Copy() | ForEach-Object {
                            $_.mail = $Entry; $_ ;
                        } ) ;
                    }
                    finally {} ;
                }
                else {
                    Write-Host "." -NoNewLine ;
                    # Write-Host "Unexpected error for $Entry" -ForegroundColor Red
                    $ExpandedEntries += ( $NotFound.PSObject.Copy() | ForEach-Object {
                        $_.mail = $Entry; $_ ;
                    } ) ;
                } ;
            } ;
            ## Replace the original tag value with expanded full user profile entries
            $FilteredResourceGroup.tags.$Tag = $ExpandedEntries ;
        } else {} ;
    } ;
    ## Unified JSON conversion logic
    if ($PSVersionTable.PSVersion.Major -lt 6) {
        ## PowerShell 5: Convert multi-level elements into compressed string JSON to prevent truncation
        foreach ( $key in $FilteredResourceGroup.tags.Keys ) {
            if ( $FilteredResourceGroup.tags.$key -is [System.Collections.IEnumerable] -and `
                 $FilteredResourceGroup.tags.$key -isnot [string]
               ) {
                $FilteredResourceGroup.tags.$key = (
                    $FilteredResourceGroup.tags.$key | ConvertTo-Json -Compress
                ) ;
            } else {} ;
        } ;
        $JsonOutput = $FilteredResourceGroup `
                    | ConvertTo-Json ;
    } else {
        ## PowerShell 7+: Handle JSON properly using -Depth
        $JsonOutput = $FilteredResourceGroup `
                    | ConvertTo-Json -Depth $MaxDepth ;
    } ;

    ## Save and display output
    Write-Host "`n" ;
    $JsonOutput ;
    # return 0 ;
} ;
