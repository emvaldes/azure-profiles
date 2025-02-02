#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function accesstoken_expiration__faulty {
    ## Manually set the expected token scope since Azure CLI does not return it
    $Script:TokenScope = "https://management.azure.com/" ;
    ## Write-Host "DEBUG: Token Scope -> $TokenScope" -ForegroundColor Magenta ;
    $Script:AccessTokenJson = az account get-access-token --resource $TokenScope `
                                                          --output json 2>$null `
                            | ConvertFrom-Json ;
    if ( $Debug ) {
        ## Debugging: Print the full token JSON
        Write-Host "Access Token (JSON) -> $( $AccessTokenJson | ConvertTo-Json )`n" `
                   -ForegroundColor Yellow ;
    } else {} ;
    ## Extract and store the access token
    $Script:AccessToken = $AccessTokenJson.accessToken ;
    ## Extracting the Access Token Expiration from JSON (removes milliseconds)
    $TokenExpirationString = $AccessTokenJson.expiresOn -replace "\.\d+$", "" ;
    $Script:TokenExpiration = [DateTime]::ParseExact(
        $TokenExpirationString, "yyyy-MM-dd HH:mm:ss", $null
    ) ;
    ## return 0 ;
} ;

function accesstoken_expiration {
    ## Manually set the expected token scope since Azure CLI does not return it
    $Script:TokenScope = "https://management.azure.com/" ;
    ## Write-Host "DEBUG: Token Scope -> $TokenScope" -ForegroundColor Magenta ;
    $Script:AccessTokenJson = az account get-access-token --resource $TokenScope `
                                                          --output json 2>$null `
                            | ConvertFrom-Json ;
    ## Validate JSON response
    if ( -not $AccessTokenJson ) {
        Write-Verbose "Failed to retrieve access token JSON." ;
        return ;
    } ;
    if ( $Debug ) {
        ## Debugging: Print the full token JSON
        Write-Host "Access Token (JSON) -> $( $AccessTokenJson | ConvertTo-Json )`n" `
                   -ForegroundColor Yellow ;
    } else {} ;
    ## Extract and store the access token
    $Script:AccessToken = $AccessTokenJson.accessToken ;
    ## Check if "expiresOn" exists
    if ( -not $AccessTokenJson.PSObject.Properties.Name -contains "expiresOn" ) {
        Write-Verbose "'expiresOn' field is missing from the JSON output." ;
        return ;
    } ;
    ## Extracting the Access Token Expiration from JSON (removes milliseconds)
    $TokenExpirationString = $AccessTokenJson.expiresOn -replace "\.\d+$", "" ;
    if ( -not $TokenExpirationString ) {
        Write-Verbose "Token expiration string is empty." ;
        return ;
    } ;
    ## Convert to DateTime
    try {
        $Script:TokenExpiration = [DateTime]::ParseExact(
            $TokenExpirationString, "yyyy-MM-dd HH:mm:ss", $null
        ) ;
    } catch {
        Write-Verbose "Failed to parse expiration date: '$TokenExpirationString'" ;
        return ;
    } finally {} ;
    ## return 0 ;
} ;
