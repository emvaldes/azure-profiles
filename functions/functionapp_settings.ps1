#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function functionapp_settings {
    try {
        ## Retrieve the application settings of the specified Azure Function App.
        ## This command fetches all configuration settings for the Function App using Azure CLI.
        ## The JSON output is then converted into a PowerShell object for easier manipulation.
        $Script:AppSettingsJson = az functionapp config appsettings list --name $FunctionAppName `
                                                                         --resource-group $ResourceGroupName `
                                | ConvertFrom-Json ;
        $MessageScope = "Function-App environment variables" ;
        if ( $AppSettingsJson ) {
            if ( $Variables ) {
                Write-Host "Listing ${MessageScope}: " `
                           -ForegroundColor Cyan ;
                ## Output the first application setting from the retrieved configuration settings.
                ## This is likely used to verify that the settings were successfully retrieved.
                $AppSettingsJson ;
            } ;
        } else {
            Write-Host "Unable to retrieve ${MessageScope}!" ;
            exit 0 ;
        } ;
    }
    catch { exit 0 ; }
    finally {} ;
    ## return 0 ;
} ;
