#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function environment_variables {
    ## Define an array of required environment variable keys related to PostgreSQL configuration.
    ## These keys are essential for database connection settings and will be used to verify or set environment variables.
    $Script:RequiredKeys = @(
        "POSTGRES_HOST",
        "POSTGRES_DATABASE",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_PORT"
    ) ;
    ## Iterate over the list of required PostgreSQL-related environment variable keys.
    ForEach ( $Key in $RequiredKeys ) {
        ## Retrieve the corresponding value from the Function App's application settings.
        $Value = ( $AppSettingsJson | Where-Object { $_.name -eq $Key } ).value ;
        ## Check if the value exists and is not empty.
        if ( $Value -and $Value -ne "" ) {
            ## Correctly assign the value to the corresponding environment variable.
            Set-Item -Path "Env:\$Key" -Value $Value ;
        } ;
    } ;
    Write-Host "Listing Environment variables: `n" -ForegroundColor Cyan ;
    foreach ( $Key in $Script:RequiredKeys ) {
        $Value = [System.Environment]::GetEnvironmentVariable( $Key ) ;
        if ( -not [string]::IsNullOrEmpty( $Value ) ) {
            Write-Host "`$env:${Key} = '${Value}' ;" ;
        } else {
            Write-Host "`$env:${Key} is missing." ;
            exit 0 ;
        } ;
    } ;
    ## return 0 ;
} ;
