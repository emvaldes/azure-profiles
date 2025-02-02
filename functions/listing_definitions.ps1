#!/usr/bin/env pwsh

## -----------------------------------------------------------------------------

function listing_definitions__legacy {
        $Script:RoleScope = "Azure Contributor Light" ;
        ## Retrieve the role definition details for the specified Azure role: "Azure Contributor Light".
        ## The command fetches role details based on its name.
        ## The JSON output is converted into a PowerShell object for structured manipulation.
        ## The `Select-Object -ExpandProperty permissions` extracts and displays only the permissions associated with the role.
        $Script:RoleDefinitionList = az role definition list --name $RoleScope `
                            | ConvertFrom-Json `
                            | Select-Object -ExpandProperty permissions ;
        if ( $Verbose ) {
            if ( $RoleDefinitionList ) {
                Write-Host "`nListing ${RoleScope} role definitions: " `
                           -ForegroundColor Cyan ;
                $RoleDefinitionList | ConvertTo-Json ;
            } ;
        } ;
    ## return 0 ;
} ;

function listing_definitions {
    $Script:RoleScope = "Azure Contributor Light"

    ## Retrieve role definition details
    $RoleDefinitionJson = az role definition list --name "$Script:RoleScope" --output json

    # ## Debug: Check raw JSON output
    # if ($Verbose) {
    #     Write-Host "Raw JSON Output:" -ForegroundColor Yellow ;
    #     $RoleDefinitionJson | ConvertTo-Json ;
    # }

    ## Convert JSON to PowerShell Object
    $RoleDefinitionList = $RoleDefinitionJson | ConvertFrom-Json

    ## Ensure the expected structure exists
    if ($RoleDefinitionList -and $RoleDefinitionList.Count -gt 0) {
        ## Check if the first object has a 'permissions' property
        if ($RoleDefinitionList[0].PSObject.Properties.Name -contains "permissions") {
            $Script:RoleDefinitionList = $RoleDefinitionList | Select-Object -ExpandProperty permissions
        }
        else {
            Write-Host "Warning: 'permissions' property not found in role definition output." -ForegroundColor Red
            $Script:RoleDefinitionList = @()  # Empty array to prevent errors
        }
    }
    else {
        Write-Host "No role definition found for '$Script:RoleScope'." -ForegroundColor Red
        $Script:RoleDefinitionList = @()
    }

    ## Display the role definition if verbose mode is enabled
    if ($Verbose -and $Script:RoleDefinitionList) {
        Write-Host "`nListing ${Script:RoleScope} role definitions: " -ForegroundColor Cyan
        $Script:RoleDefinitionList | ConvertTo-Json -Depth 3
    }
}
