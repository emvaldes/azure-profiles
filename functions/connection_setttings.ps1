#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function connection_setttings {
    $MessageScope = "PostgreSQL Connection String" ;
    try {
        $Script:ConnectionString = $AppSettingsJson | Where-Object {
            $_.name -match "POSTGRES_URL" -and `
            $_.Value -match "jdbc:postgresql://"
        } ;
        ## $Script:ConnectionString ;
        if ( $ConnectionString ) {
            Write-Host "Found ${MessageScope}: `n" -ForegroundColor Cyan ;
            $ConnectionString.Value ;
            ## Extract the port using regex
            if ( $ConnectionString -match ":(\d+)/" ) {
                $PostgresPort = $matches[1] ;
                ## Set as environment variable
                ${env:POSTGRES_PORT} = $PostgresPort ;
                ## Write-Host "Extracted PostgreSQL Port: ${PostgresPort}" ;
            } else {
                Write-Host "No port found in C${MessageScope}!" ;
                exit 0 ;
            } ;
        } else {
            Write-Host "${MessageScope} not found!" ;
            exit 0 ;
        } ;
    }
    catch {
        Write-Host "Unable to identify ${MessageScope}!" ;
        exit 0 ;
    }
    finally {} ;
    Write-Host "PostgreSQL Port: $( ${env:POSTGRES_PORT} )`n" ;
    ## return 0 ;
} ;
