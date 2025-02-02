#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function timezone_localoffset {
    $Script:LocalTimeZone = [System.TimeZoneInfo]::Local ;
    $Script:CurrentUTC = ( Get-Date ).ToUniversalTime() ;
    $Script:LocalOffset = $LocalTimeZone.BaseUtcOffset ;
    ## Debug Output
    if ( $Debug ) {
        Write-Host "`nLocal Time Zone:`t" -NoNewLine -ForegroundColor Cyan ;
        Write-Host "$( $LocalTimeZone.Id ) ($( $LocalTimeZone.DisplayName ))" ;
        Write-Host "Current Local Time:`t" -NoNewLine -ForegroundColor Cyan ;
        Write-Host "${CurrentLocalTime}" ;
        Write-Host "Current UTC Time:`t" -NoNewLine -ForegroundColor Cyan ;
        Write-Host "${CurrentUTC}" ;
        Write-Host "Local Time Offset:`t" -NoNewLine -ForegroundColor Cyan ;
        Write-Host "$( $LocalOffset.TotalHours ) hours" ;
    } else {} ;
    ## Validate the time zone offset
    if ( $LocalOffset -eq $null -or `
         $LocalOffset.TotalHours -eq $null
       ) {
        Write-Warning "Unable to determine Local Time Zone offset! Defaulting to UTC." `
                      -ForegroundColor Red ;
    } elseif ( [Math]::Abs( ( $CurrentLocalTime - $CurrentUTC ).TotalHours - $LocalOffset.TotalHours ) -gt 1 ) {
        Write-Warning "Possible mismatch between System Time and expected Local Time!" `
                      -ForegroundColor Red ;
    } else {} ;
    ## return 0 ;
} ;
