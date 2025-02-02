#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function manage_accesstoken {
    ## Capture Date in Current Local-Time
    $Script:CurrentLocalTime = ( Get-Date ) ;
    if ( $Debug ) {
        timezone_localoffset ;
        Write-Host ;
    } else {} ;
    ## Disabling the condition for forced-login
    $ForcedLogin = $false ;
    try {
        $AzureProfileInfo = az account show 2>&1 | Out-String ;
        if ( $AzureProfileInfo -match "Please run 'az login'" ) {
            Write-Host "No active Azure session found. Proceed to logging in ..." `
                       -ForegroundColor Red ;
            $ForcedLogin = $true ;
        } else {} ;
    }
    catch {
        Write-Host "Unable to identify Azure Account Information!" `
                   -ForegroundColor Red ;
        $ForcedLogin = $true ;
    }
    finally {
        if ( $ForcedLogin ) {
            $null = az login --use-device-code ;
            $ForcedLogin = $false ;
        } else {} ;
        accesstoken_expiration ;
    } ;
    try {
        ## Comparing Token-Expiration and Current Local-Time
        if ( $TokenExpiration -lt $CurrentLocalTime ) {
            Write-Host "Azure session expired. Logging in again..." `
                       -ForegroundColor Red ;
            $null = az login --use-device-code ;
            accesstoken_expiration ;
        } else {
            Write-Host "Azure session is still active. Using existing session." `
                       -ForegroundColor Green ;
        }
        ## Calculate the time difference
        $TimeRemaining = $TokenExpiration - $CurrentLocalTime ;
        $HoursRemaining = [math]::Floor( $TimeRemaining.TotalHours ) ;
        $MinutesRemaining = [math]::Floor( $TimeRemaining.TotalMinutes % 60 ) ;
        $SecondsRemaining = [math]::Floor( $TimeRemaining.TotalSeconds % 60 ) ;
        # Write-Host "Token Expiration ( Local ): ${TokenExpiration}" `
        #            -ForegroundColor Yellow ;
        Write-Host "Available Remaining Time: ${HoursRemaining} hours, ${MinutesRemaining} minutes, ${SecondsRemaining} seconds" `
                   -ForegroundColor Green ;
    }
    catch {
        Write-Host "Could not parse token expiration time. Aborting execution!" `
                   -ForegroundColor Red ;
        exit 0 ;
    }
    finally{
        ## Refresh account info after login
        $AzureProfileInfo = az account show 2>$null ;
        if ( $AzureProfileInfo -match "error" ) {
            Write-Host "Failed to retrieve account information. Please ensure you're logged in." `
                       -ForegroundColor Red ;
            exit 0 ;
        } else {
            $Script:AzureProfile = $AzureProfileInfo `
                                 | ConvertFrom-Json ;
            # $AzureProfile | ConvertTo-Json ;
            $Script:SubscriptionId = $AzureProfile.id ;
            # $SubscriptionId ;
        } ;
        ## Set the active Azure subscription
        # Update-AzConfig -DefaultSubscriptionForLogin $Script:SubscriptionId 2>$null ;
        az account set --subscription $Script:SubscriptionId 2>$null ;
        ## Check if an Azure PowerShell session is already active
        $AzContext = Get-AzContext ;
        if ( ( -not $AzContext.Tenant.Id ) -or `
             ( $AzContext.Tenant.Id -ne $AzureProfile.tenantId )
           ) {
            ## No active session or incorrect tenant → Authenticate
            Write-Host "`nNo active Azure session detected or incorrect tenant. Connecting..." `
                       -ForegroundColor Cyan ;
            Connect-AzAccount -TenantId $AzureProfile.tenantId ;
        } else {
            # ## Everything is fine → No need to authenticate
            # Write-Host "`nAzure session is already active for the correct tenant. Skipping authentication." `
            #            -ForegroundColor Green ;
        } ;
    } ;
    ## return 0 ;
} ;
