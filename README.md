# Azure Profiles - Inspecting Configurations

## Overview
The **profile-privileges.ps1** script provides an automated way to manage Azure authentication, retrieve user role assignments, and profile security configurations across Azure subscriptions and resource groups. This script is specifically designed to analyze **Azure login sessions, multi-tenancy profiles, PostgreSQL database configurations, Azure Function App settings, Key Vault secrets, network security settings, and role-based access control (RBAC) assignments**.

### Features
- **Azure Session Management**: Ensures authentication, handles multi-tenant logins, and maintains access tokens.
- **PostgreSQL Profiling**: Extracts database connection settings, firewall rules, and system configurations.
- **Azure Function App Environment Inspection**: Retrieves and analyzes application settings.
- **Azure Key Vault Secret Retrieval**: Lists and decrypts Key Vault secrets for evaluation.
- **Role-Based Access Control (RBAC) Analysis**: Evaluates user and service principal privileges across Azure subscriptions and resource groups.
- **Network Security Inspection**: Profiles security groups, private endpoints, private DNS, and network interfaces.
- **Multi-Format Output**: Provides structured results in JSON, table format, and human-readable logs.

### **System Requirements**
- **Operating System**: Windows/Linux/macOS with PowerShell 7+
- **Azure CLI**: Installed and authenticated (`az login` required)
- **Azure PowerShell Module**: Installed (`Install-Module -Name Az -AllowClobber -Force`)
- **Permissions**: Sufficient privileges to retrieve role assignments and access secrets

### **PowerShell Modules**
Run the following command to install necessary PowerShell modules:
```powershell
Install-Module -Name Az.Accounts, Az.Resources, Az.PostgreSQL, Az.KeyVault `
               -Force -AllowClobber ;
```

#### Installation
Clone the repository or download the script directly:
```bash
git clone https://github.com/emvaldes/azure-profiles.git
cd azure-profiles
```
Alternatively, download the script manually:
```bash
> usercontent="raw.githubusercontent.com/emvaldes" ;
> wget https://${usercontent}/azure-profiles/refs/heads/master/profile-privileges.ps1
```

#### NAME
    azure-profiles/profile-privileges.ps1

#### SYNOPSIS
  The script manages Azure login sessions/credentials, including multi-tenant profiles.
  It performs comprehensive profiling of PostgreSQL database servers, firewall rules,
  and system configurations. Additionally, it retrieves and decrypts Azure Key Vault
  secrets, extracts Azure FunctionApp environment settings, and securely loads database
  connection credentials into environment variables. The script also evaluates Azure
  account profiles, inspects role assignments, and analyzes network security groups,
  private endpoints, DNS records, and network interfaces.

#### DESCRIPTION
  This script automates Azure session management and multi-tenant authentication
  while extracting and analyzing cloud resources. It profiles PostgreSQL database
  configurations, retrieves and decrypts Azure Key Vault secrets, and extracts
  environment settings from Azure Function Apps.
  It also performs in-depth evaluations of Azure role assignments, firewall rules,
  and security configurations. Additionally, it inspects network security groups,
  private endpoints, DNS records, and network interfaces to provide a complete
  security and access profile of the Azure environment.

#### **Application Parameters**
The script supports multiple modes of operation with flexible parameters.

| Parameter | Alias | Description |
|-----------|-------|-------------|
| `-ProjectDomain` | `-p` | Target project-domain (e.g., project). |
| `-Environment` | `-e` | Target environment (e.g., dev, test, staging, prod). |
| `-ResourceGroup` | `-r` | Resource Group like: domain-${Environment}. |
| `-DatabaseName` | `-n` | PostgreSQL Database Name (e.g.: project_database). |
| `-KeyVault` | `-s` | Listing Azure KeyVault environment secrets. |
| `-Variables` | `-a` | Listing Azure FunctionAppp environment variables. |
| `-Networking` | `-a` | Display Infrastructure Networking information |
| `-Firewalls` | `-a` | Display Infrastructure Firewall configuration |
| `-EndPoints` | `-t` | Listing Azure Resource-Group Private End-Points. |
| `-Listing` | `-l` | Listing User-Groups and their Definitions. |
| `-Inspect` | `-i` | Profile Inspection to resolve role assignments listing. |
| `-MaxDepth` | `-m` | Defines JSON max levels of nested objects to be parsed. |
| `-Verbose` | `-v` | Activates the use of vervbosity-level in the script's output. |
| `-Debug` | `-d` | Activates the use of debug-level in the script's output. |
| `-Help` | `-h` | Provides built-in native script operational support . |

```powershell
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
```

#### **Example 1:**

```powershell
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
                         -MaxDepth 10
                         -Verbose
                         -Debug ;
```

#### **Request Support**

```powershell
.\profile-privileges.ps1 -Help ;
```

``` powershell
profile-privileges.ps1 [[-ProjectDomain] <String>] [[-Environment] <String>]
[[-ResourceGroup] <String>] [[-DatabaseName] <String>] [-KeyVault] [-Variables]
[-Networking] [-Firewalls] [-EndPoints] [-Listing] [-Inspect] [[-MaxDepth] <Int32>]
[-Verbose] [-Debug] [-Help] [<CommonParameters>]
```

#### RELATED LINKS
  https://github.com/emvaldes/azure-profiles

#### NOTES
  - Ensure that the Azure CLI (`az`) is installed and authenticated.

---

#### Program's Execution

``` console
> ./profile-privileges.ps1 -ProjectDomain 'domain' `
                           -Environment 'staging' `
                           -ResourceGroup domain-staging `
                           -DatabaseName domain-database `
                           -Listing `
                           -Inspect `
                           -KeyVault `
                           -Variables `
                           -Networking `
                           -Firewalls `
                           -EndPoints `
                           -Verbose `
                           -Debug ;

Input Parameters:
{
  "ProjectDomain": "domain",
  "Environment": "staging",
  "ResourceGroup": "domain-staging",
  "DatabaseName": "domain-database",
  "Listing": {
    "IsPresent": true
  },
  "Inspect": {
    "IsPresent": true
  },
  "KeyVault": {
    "IsPresent": true
  },
  "Variables": {
    "IsPresent": true
  },
  "Networking": {
    "IsPresent": true
  },
  "Firewalls": {
    "IsPresent": true
  },
  "EndPoints": {
    "IsPresent": true
  },
  "Verbose": {
    "IsPresent": true
  },
  "Debug": {
    "IsPresent": true
  }
}

Loading: functions/accesstoken_expiration.ps1
Loading: functions/connection_setttings.ps1
Loading: functions/environment_variables.ps1
Loading: functions/functionapp_settings.ps1
Loading: functions/invoke_restmethod.ps1
Loading: functions/keyvault_secrets.ps1
Loading: functions/listing_definitions.ps1
Loading: functions/listing_usergroups.ps1
Loading: functions/manage_accesstoken.ps1
Loading: functions/network_privatedns.ps1
Loading: functions/network_securitygroups.ps1
Loading: functions/postgres_configs.ps1
Loading: functions/postgres_details.ps1
Loading: functions/postgres_firewallrules.ps1
Loading: functions/postgres_interfaces.ps1
Loading: functions/private_endpoints_details.ps1
Loading: functions/private_endpoints_listing.ps1
Loading: functions/private_endpoints_matches.ps1
Loading: functions/profile_inspection.ps1
Loading: functions/testing_connectivity.ps1
Loading: functions/timezone_localoffset.ps1

Local Time Zone:	America/Creston ((UTC-07:00) Mountain Time (Creston))
Current Local Time:	01/01/2025 07:00:00
Current UTC Time:	01/01/2025 00:00:00
Local Time Offset:	-7 hours
```

``` console
No active Azure session found. Proceed to logging in ... To sign in,
use a web browser to open the page https://microsoft.com/devicelogin and enter
the code 000000000 to authenticate.
```

```console
Access Token (JSON) -> {
  "accessToken": "eyJ0eXAiOi...Oqyt7yiiPQ",
  "expiresOn": "2025-01-01 00:00:00.000000",
  "expires_on": 1735689600,
  "subscription": "9a389aa4-c9fe-4a59-80f8-bf454f4dae06",
  "tenant": "33888350-2082-40bb-88fa-a5e94d733f01",
  "tokenType": "Bearer"
}

Azure session is still active. Using existing session.
Available Remaining Time: 1 hours, 0 minutes, 0 seconds
```

```console
Listing Account information:
{
  "environmentName": "AzureCloud",
  "homeTenantId": "33888350-2082-40bb-88fa-a5e94d733f01",
  "id": "9edc6208-d5b1-4c58-a35b-ec241d032b28",
  "isDefault": true,
  "managedByTenants": [
  {
    "tenantId": "b06ad78d-4117-42d3-8c2b-bd73337bf208"
  }
  ],
  "name": "CONTOSO-COM-01",
  "state": "Enabled",
  "tenantDefaultDomain": "contoso.onmicrosoft.com",
  "tenantDisplayName": "CONTOSO",
  "tenantId": "33888350-2082-40bb-88fa-a5e94d733f01",
  "user": {
  "name": "user@domain.tld",
  "type": "user"
  }
}
```

```console
Filtered Resource Group: .........

{
  "id": "/subscriptions/9a389aa4-...-bf454f4dae06/resourceGroups/domain-staging",
  "name": "domain-staging",
  "type": "Microsoft.Resources/resourceGroups",
  "location": "eastus",
  "tags": {
    "zone": "EXTRANET",
    "entertainment_directors": [
      {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
        "businessPhones": [
          "123.456.7890"
        ],
        "displayName": "Johnnie Walker",
        "givenName": "Walker",
        "id": "00000000-0000-0000-0000-000000000000",
        "jobTitle": "Scotch Whisky Taster",
        "mail": "johnnie@walker.com",
        "mobilePhone": "123.456.7890",
        "officeLocation": "Johnnie Walker Princes Street (Edinburgh, Scotland)",
        "preferredLanguage": "Scottish Gaelic",
        "surname": "Johnnie",
        "userPrincipalName": "drunk-master",
        "status": "Uncertain"
      }
    ],
    "environment": "stagging",
    "security_compliance": "relaxed",
    "pii_data": "false",
    "business_connoisseurs": [
      {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
        "businessPhones": [
          "987.654.3210"
        ],
        "displayName": "Jack Daniels",
        "givenName": "Daniels",
        "id": "11111111-1111-1111-1111-111111111111",
        "jobTitle": "Whiskey Quality Analyst",
        "mail": "jack@daniels.com",
        "mobilePhone": "987.654.3210",
        "officeLocation": "Lynchburg, Tennessee",
        "preferredLanguage": "Southern Drawl",
        "surname": "Jack",
        "userPrincipalName": "bourbon-boss",
        "status": "Mellow"
      }
    ],
    "escid": "1234567890",
    "system": "universe",
    "support_group": "Drunks & Jokers",
    "technical_alchemists": [
      {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
        "businessPhones": [
          "456.123.7890"
        ],
        "displayName": "Captain Morgan",
        "givenName": "Morgan",
        "id": "22222222-2222-2222-2222-222222222222",
        "jobTitle": "Rum Formulation Engineer",
        "mail": "captain@morgan.com",
        "mobilePhone": "456.123.7890",
        "officeLocation": "The Caribbean",
        "preferredLanguage": "Pirate Speak",
        "surname": "Captain",
        "userPrincipalName": "yo-ho-ho",
        "status": "Adventurous"
      }
    ],
    "funding_source": "Imagination",
    "center": "Imagination",
    "legendary_fixers": [
      {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
        "businessPhones": [
          "789.321.4560"
        ],
        "displayName": "Jose Cuervo",
        "givenName": "Cuervo",
        "id": "33333333-3333-3333-3333-333333333333",
        "jobTitle": "Tequila Troubleshooter",
        "mail": "jose@cuervo.com",
        "mobilePhone": "789.321.4560",
        "officeLocation": "Tequila, Mexico",
        "preferredLanguage": "Spanglish",
        "surname": "Jose",
        "userPrincipalName": "agave-architect",
        "status": "Spirited"
      }
    ]
  },
  "properties": {
    "provisioningState": "Succeeded"
  }
}
```

#### Output Formats
The script outputs data in multiple formats for analysis:
- **Human-readable tables** (default in PowerShell)
- **JSON format** (`ConvertTo-Json` for structured processing)
- **Standard logs** (written to the console and log files)

#### Security Considerations
- **Secrets Handling**: The script retrieves sensitive information such as database credentials and Key Vault secrets. Ensure logs are not stored in unsecured locations.
- **RBAC Permissions**: Running the script requires appropriate privileges to access Azure resources and retrieve sensitive data.
- **Session Management**: Authentication tokens are managed internally to prevent unnecessary re-authentication.

### Troubleshooting

#### **Common Issues & Fixes**
| Issue | Cause | Solution |
|-------|-------|----------|
| `Access Denied` error when retrieving secrets | Insufficient Key Vault permissions | Ensure you have `Key Vault Reader` or `Secrets Reader` role. |
| Empty role assignment list | User lacks assigned roles | Check using `az role assignment list --all`. |
| `az not found` | Azure CLI is not installed | Install Azure CLI from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli. |

#### Logs and Error Handling
- Enable verbose mode for detailed logs: `$VerbosePreference = "Continue"`
- Error logs are stored in `error.log` for debugging.

---

### Contributions

#### How to Contribute

1. Fork the repository and create a feature branch.
2. Implement your feature or fix, ensuring tests pass.
3. Submit a pull request with a detailed description.

---

### License

This project is licensed under the [GNU General Public License](LICENSE).

#### Author
[**Eduardo Valdés**](https://github.com/emvaldes)
Contact: [GitHub Issues](https://github.com/emvaldes/azure-profiles/issues)
