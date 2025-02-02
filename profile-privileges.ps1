#!/usr/bin/env pwsh

<#
.SYNOPSIS
    The script manages Azure login sessions/credentials, including multi-tenant profiles.
    It performs comprehensive profiling of PostgreSQL database servers, firewall rules,
    and system configurations. Additionally, it retrieves and decrypts Azure Key Vault
    secrets, extracts Azure FunctionApp environment settings, and securely loads database
    connection credentials into environment variables. The script also evaluates Azure
    account profiles, inspects role assignments, and analyzes network security groups,
    private endpoints, DNS records, and network interfaces.

.DESCRIPTION
    This script automates Azure session management and multi-tenant authentication
    while extracting and analyzing cloud resources. It profiles PostgreSQL database
    configurations, retrieves and decrypts Azure Key Vault secrets, and extracts
    environment settings from Azure Function Apps.
    It also performs in-depth evaluations of Azure role assignments, firewall rules,
    and security configurations. Additionally, it inspects network security groups,
    private endpoints, DNS records, and network interfaces to provide a complete
    security and access profile of the Azure environment.

.PARAMETER ProjectDomain
    Target project-domain (e.g., project, etc.). Alias = p
.PARAMETER Environment
    Target environment (e.g., dev, test, staging, prod). Alias = p
.PARAMETER ResourceGroup
    Resource Group like: domain-${Environment}. Alias = r
.PARAMETER DatabaseName
    PostgreSQL Database Name (e.g.: project_database). Alias = n
.PARAMETER KeyVault
    Listing Azure KeyVault environment secrets. Alias = s
.PARAMETER Variables
    Listing Azure FunctionAppp environment variables. Alias = a
.PARAMETER Networking
    Display Infrastructure Networking information. Alias = w
.PARAMETER Firewalls
    Display Infrastructure Firewall configuration. Alias = f
.PARAMETER EndPoints
    Listing Azure Resource-Group Private End-Points. Alias = t
.PARAMETER Listing
    Listing User-Groups and their Definitions. Alias = l
.PARAMETER Inspect
    Profile Inspection to resolve role assignments listing. Alias = s
.PARAMETER MaxDepth
    Defines JSON max levels of nested objects to be parsed. Alias = m
.PARAMETER Verbose
    Activates the use of vervbosity-level in the script's output. Alias = v
.PARAMETER Debug
    Activates the use of debug-level in the script's output. Alias = d
.PARAMETER Help
    Provides built-in native script operational support. Alias = h

.EXAMPLE
    ## Example 1:
    .\profile-privileges.ps1 -ProjectDomain "project"
                             -Environment "staging"
                             -ResourceGroup "domain-data-hub-staging"
                             -DatabaseName "project_database"
                             -KeyVault
                             -Variables
                             -Networking
                             -Firewalls
                             -EndPoints
                             -Listing
                             -Inspect
                             -Verbose
                             -Debug ;
  ## Example 1:
    .\profile-privileges.ps1 -Help ;

.NOTES
    - Ensure that the Azure CLI (`az`) is installed and authenticated.

.LINK
    https://github.com/emvaldes/database-queries
#>

# ## Input parameter(s):
param (
    [ValidateNotNullOrEmpty()][Alias("p")]
    [string]$ProjectDomain,
    [ValidateNotNullOrEmpty()][Alias("e")]
    [string]$Environment,
    [ValidateNotNullOrEmpty()][Alias("r")]
    [string]$ResourceGroup,
    [ValidateNotNullOrEmpty()][Alias("n")]
    [string]$DatabaseName,
    [ValidateNotNullOrEmpty()][Alias("s")]
    [switch]$KeyVault,
    [ValidateNotNullOrEmpty()][Alias("a")]
    [switch]$Variables,
    [ValidateNotNullOrEmpty()][Alias("w")]
    [switch]$Networking,
    [ValidateNotNullOrEmpty()][Alias("f")]
    [switch]$Firewalls,
    [ValidateNotNullOrEmpty()][Alias("t")]
    [switch]$EndPoints,
    [ValidateNotNullOrEmpty()][Alias("l")]
    [switch]$Listing,
    [ValidateNotNullOrEmpty()][Alias("i")]
    [switch]$Inspect,
    [Alias("m")]
    [int]$MaxDepth = 20,
    [Alias("v")]
    [switch]$Verbose,
    [Alias("d")]
    [switch]$Debug,
    [Alias("h")]
    [switch]$Help
)

## Display help message if -Help or -? is used
if ( $Help ) {
    Get-Help $PSCommandPath -Detailed ;
    exit ;
} ;

## Ensuring the durability for run-time input parameters
$Script:PSBoundParameters = $PSBoundParameters ;
if ( $Debug ) {
    Write-Host "`nInput Parameters: " -ForegroundColor Cyan ;
    $Script:PSBoundParameters | ConvertTo-Json ;
} ;

$PSVersionTable["System"] = ( $PSVersionTable.OS -split "\s" )[0] ;

## Retrieve script execution details as an object
$ScriptInfo = [PSCustomObject]@{
    FullPath    = $MyInvocation.MyCommand.Path
    Directory   = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
    FileName    = [System.IO.Path]::GetFileName( $MyInvocation.MyCommand.Path )
    BaseName    = [System.IO.Path]::GetFileNameWithoutExtension( $MyInvocation.MyCommand.Path )
    BaseConfig  = Join-Path -Path ( Split-Path -Path $MyInvocation.MyCommand.Path -Parent ) `
                            -ChildPath ( [System.IO.Path]::GetFileNameWithoutExtension( $MyInvocation.MyCommand.Path ) )
} ;

Write-Host ;

## Loading all functions in the functions directory
Get-ChildItem -Path "functions" -Filter "*.ps1" | ForEach-Object {
    if ( $Debug ) {
        ## Retain the folder name and everything after it
        $SourceFile = $_.FullName -replace "^.+?functions[\\/]", "functions/" ;
        Write-Host "Loading: $( $SourceFile )" ;
    } ;
    ## Sourcing project's function
    . $_.FullName ;
} ;

## -----------------------------------------------------------------------------

$Script:ProjectDomain = $ProjectDomain ;  ## "project"
$Script:Environment   = $Environment ;    ## "staging"

## Define the Azure Resource Group where all resources are hosted
$Script:ResourceGroupName = $ResourceGroup ;  ## "domain-data-hub-${Environment}"

## Define the name of the Azure Key Vault, used for securely storing secrets
$Script:VaultName = "${ProjectDomain}${Environment}-keyvault" ;

## Define the PostgreSQL server name
$Script:PostgresServerName = "${ProjectDomain}${Environment}-pgsql" ;

## Define the PostgreSQL Server database
$Script:PostgresDatabaseName = $DatabaseName ;  ## "project_database"
$env:POSTGRES_DATABASE = $PostgresDatabaseName ;

## Define the Function App name, which likely hosts Azure Functions for processing tasks
$Script:FunctionAppName = "${ProjectDomain}${Environment}-functionapp" ;

manage_accesstoken | Out-Host ;

## -----------------------------------------------------------------------------

if ( $Verbose ) {
    ## Write-Host "`nUsing Access Token: ${AccessToken}" ;
    Write-Host "`nListing Account information: " `
               -ForegroundColor Cyan ;
    $AzureProfile | ConvertTo-Json ;
} ;

if ( $Debug ) { invoke_restmethod | Out-Host ; };

## -----------------------------------------------------------------------------

az__postgres_details | Out-Host ;
postgres_configs | Out-Host ;

##### Key-Vault :
az__keyvault_secrets | Out-Host ;

##### Function-App & Environment :
functionapp_settings | Out-Host ;

connection_setttings | Out-Host ;
environment_variables | Out-Host ;

profile_inspection | Out-Host ;

##### Listing User-Groups & Definitions:
if ( $Listing ) {
    listing_usergroups | Out-Host ;
    listing_definitions | Out-Host ;
} ;

##### Networking configurations:

# nslookup ${env:POSTGRES_HOST} ;
# dig ${env:POSTGRES_HOST} ;

testing_connectivity | Out-Host ;

if ( $Networking ) {
    network_securitygroups | Out-Host ;
} ;

if ( $EndPoints ) {
    private_endpoints_listing | Out-Host ;
    private_endpoints_matches | Out-Host ;
    private_endpoints_details | Out-Host ;
} ;

postgres_interfaces | Out-Host ;
network_privatedns | Out-Host ;

postgres_firewallrules | Out-Host ;

## -----------------------------------------------------------------------------

try {
    $env:POSTGRES_SSLMODE = "require" ;
    $POSTGRES_RESPONSE = (
        psql --host="$( $env:POSTGRES_HOST )" `
             --port=$env:POSTGRES_PORT `
             --dbname="$( $env:POSTGRES_DATABASE )" `
             --username="$( $env:POSTGRES_USER )" `
             --no-password `
             --quiet `
             --command="SELECT 1 ;" 2>$null
    ) ;
    ## Handle different psql exit codes
    switch ($LASTEXITCODE) {
        0 {   ## Success (Query executed correctly
              Write-Host "Success: Connection and query executed successfully!" ;
          }
        1 {   ## Fatal Error (e.g., syntax error, connection issues)
              Write-Error "Fatal Error: Check your database connection parameters and syntax." ;
          }
        2 {   ## Connection Failure (e.g., cannot reach database)
              Write-Error "Connection Failure. The database server is unreachable." ;
              Write-Host "Ensure you are on the right network ( VPN, Private Endpoint, firewall rules, etc. )." ;
          }
        3 {   ## Authentication Failure (wrong user/password)
              Write-Warning "Authentication Failure: Incorrect username or password." ;
          }
        default {
            ## Other	Unknown Error
            Write-Host "Unknown Error: psql exited with code ${LASTEXITCODE}" ;
        }
    } ;
}
catch {
    Write-Host "Unexpected error occurred: $_" ;
} finally {
    Write-Host "`nCompleted psql execution." ;
} ;

## -----------------------------------------------------------------------------

Write-Host ;
