#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function testing_connectivity {
    Write-Host "`nTesting Network Connectivity: `n" `
               -ForegroundColor Cyan ;
    nc -zv ${env:POSTGRES_HOST} ${env:POSTGRES_PORT} | Out-Null ;
    $TcpClient = New-Object System.Net.Sockets.TcpClient ;
    try {
        $TcpClient.Connect( ${env:POSTGRES_HOST}, [int]${env:POSTGRES_PORT} ) ;
        if ( $TcpClient.Connected ) {
            Write-Host "`nConnected to PostgreSQL on port ${env:POSTGRES_PORT}!" ;
        } else {
            Write-Host "Connection to PostgreSQL on port ${env:POSTGRES_PORT} failed." ;
        } ;
    } catch {
        Write-Host "Connection to PostgreSQL failed: $_" ;
    } finally {
        $TcpClient.Close() ;
    } ;
    ## return 0 ;
} ;
