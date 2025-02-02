#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function listing_usergroups {
    try {
        ## Retrieve the list of Azure AD groups that the currently authenticated user is a member of.
        ## The `--id` parameter specifies the user identifier (email or UPN).
        ## The output is retrieved in JSON format and converted into a PowerShell object for easier manipulation.
        $Script:UserGroups = az ad user get-member-groups --id $AzureProfile.user.name `
                                                          --output json 2>&1 `
                           | Out-String `
                           | ConvertFrom-Json ;
        if ( $UserGroups ) {
            if ( $Verbose ) {
                Write-Host "`nListing Active Directory User-Role's Groups: `n" `
                           -ForegroundColor Cyan ;
            } ;
            ## Iterate through each Azure AD group that the user is a member of.
            $UserGroups | ForEach-Object {
                try {
                    ## Retrieve all role assignments for the current group.
                    ## The `--assignee` parameter specifies the group ID.
                    ## The JSON output is converted into a PowerShell object and formatted as a table for readability.
                    $Script:RoleAssignments = az role assignment list --assignee $_.id --all `
                                            | Out-String ;
                    ## Check if the output contains an error message
                    if ( $RoleAssignments -match "error" -or `
                         $RoleAssignments -match "Cannot find user or service principal"
                       ) {
                        Write-Host "Cannot find user or service principal in graph database for Group ID: $( $_.id )" `
                                   -ForegroundColor Yellow ;
                    } else {
                        if ( $Verbose ) {
                            ## Output a message indicating which group's roles are being checked.
                            Write-Host "Checking roles for group: $( $_.displayName ) (ID: $( $_.id ))" ;
                            ## If no error, parse the output and format the table
                            $RoleAssignments | ConvertFrom-Json | Format-Table roleDefinitionName, scope ;
                        } ;
                    } ;
                }
                catch {
                    Write-Host "Error retrieving role assignments for Group ID: $( $_.id )" `
                               -ForegroundColor Red ;
                }
                finally {} ;
            } ;
        } else {
          Write-Host "No Active Directory User-Role Groups found!" `
                     -ForegroundColor Yellow ;
          exit 0 ;
        } ;
    }
    catch {
        Write-Host "An unexpected error occurred while retrieving user groups." `
                   -ForegroundColor Red ;
        exit 0 ;
    }
    finally {
        if ( $Verbose ) {
            Write-Host "`nCompleted Azure AD Role Check." ;
        } ;
    } ;
    ## return 0 ;
} ;
