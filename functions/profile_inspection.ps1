#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function profile_inspection {
    if ( $Inspect ) {
        ## Retrieve role assignments for the Resource-Group within a specific Azure subscription.
        ## The JSON output is converted into a PowerShell object for structured data handling.
        Write-Host "`nInspecting Resource-Group Role-Assignment: `n" `
                   -ForegroundColor Cyan ;
        $RoleAssignments = az role assignment list --resource-group $ResourceGroupName `
                     | ConvertFrom-Json ;
        $ResolvedRoles = $RoleAssignments | ForEach-Object {
            $ResolvedPrincipalName = $_.principalName
            $ResolvedCreatedBy = $_.createdBy
            try {
                ## If property looks like a GUID, resolve it
                if ( $ResolvedPrincipalName -match "^[0-9a-fA-F-]{36}$" ) {
                    if ( $_.PrincipalType -eq "User" ) {
                        $ResolvedPrincipalName = az ad user show --id $ResolvedPrincipalName `
                                                                 --query "displayName" `
                                                                 --output tsv 2>$null
                    } elseif ( $_.PrincipalType -eq "ServicePrincipal" ) {
                        $ResolvedPrincipalName = az ad sp show --id $ResolvedPrincipalName `
                                                               --query "displayName" `
                                                               --output tsv 2>$null
                    } elseif ( $_.PrincipalType -eq "Group" ) {
                        $ResolvedPrincipalName = az ad group show --group $ResolvedPrincipalName `
                                                                  --query "displayName" `
                                                                  --output tsv 2>$null
                    } ;
                } ;
                if ( $_.PrincipalType -notmatch "ServicePrincipal" ) {
                    if ( $ResolvedPrincipalName -match "^[0-9a-fA-F-]{36}$" ) {
                        $ResolvedPrincipalName = az ad user show --id $ResolvedPrincipalName `
                                                                 --query "displayName" `
                                                                 --output tsv 2>$null ;
                    } ;
                    if ( $ResolvedCreatedBy -match "^[0-9a-fA-F-]{36}$" ) {
                        $ResolvedCreatedBy = az ad user show --id $ResolvedCreatedBy `
                                                             --query "displayName" `
                                                             --output tsv 2>$null
                    } ;
                } ;
                [PSCustomObject]@{
                    Name               = $_.name
                    PrincipalID        = $_.principalId
                    PrincipalName      = $ResolvedPrincipalName
                    PrincipalType      = $_.principalType
                    RoleDefinitionName = $_.roleDefinitionName
                    CreatedBy          = $ResolvedCreatedBy
                    UpdatedOn          = $_.updatedOn
                }
            }
            catch {
                ## If an error occurs (resource not found), keep the original principalName (UUID)
                Write-Host "Warning: Could not resolve createdBy for $_.createdBy" -ForegroundColor Yellow
            }
            finally {} ;
        } ;
        # Print the resolved role assignments
        $ResolvedRoles | ConvertTo-Json ;
        Write-Host "`nListing Active Directory Member Groups: `n" `
                   -ForegroundColor Cyan ;
        ## Retrieve the list of Azure AD groups that the currently authenticated user is a member of.
        ## The `--id` parameter specifies the user identifier (email or UPN).
        ## The output is formatted as a table for better readability.
        az ad user get-member-groups --id $AzureProfile.user.name `
                                     --output table ;
    } ;
    ## return 0 ;
} ;
