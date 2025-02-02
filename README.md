# Azure Profile Privileges

## Overview
The **profile-privileges.ps1** script provides an automated way to manage Azure authentication, retrieve user role assignments, and profile security configurations across Azure subscriptions and resource groups. This script is specifically designed to analyze **Azure login sessions, multi-tenancy profiles, PostgreSQL database configurations, Azure Function App settings, Key Vault secrets, network security settings, and role-based access control (RBAC) assignments**.

## Features
- **Azure Session Management**: Ensures authentication, handles multi-tenant logins, and maintains access tokens.
- **PostgreSQL Profiling**: Extracts database connection settings, firewall rules, and system configurations.
- **Azure Function App Environment Inspection**: Retrieves and analyzes application settings.
- **Azure Key Vault Secret Retrieval**: Lists and decrypts Key Vault secrets for evaluation.
- **Role-Based Access Control (RBAC) Analysis**: Evaluates user and service principal privileges across Azure subscriptions and resource groups.
- **Network Security Inspection**: Profiles security groups, private endpoints, private DNS, and network interfaces.
- **Multi-Format Output**: Provides structured results in JSON, table format, and human-readable logs.

## Prerequisites
Before running the script, ensure the following requirements are met:

### **System Requirements**
- **Operating System**: Windows/Linux/macOS with PowerShell 7+
- **Azure CLI**: Installed and authenticated (`az login` required)
- **Azure PowerShell Module**: Installed (`Install-Module -Name Az -AllowClobber -Force`)
- **Permissions**: Sufficient privileges to retrieve role assignments and access secrets

### **Required PowerShell Modules**
Run the following command to install necessary PowerShell modules:
```powershell
Install-Module -Name Az.Accounts, Az.Resources, Az.PostgreSQL, Az.KeyVault -Force -AllowClobber
```

## Installation
Clone the repository or download the script directly:
```bash
git clone https://github.com/emvaldes/azure-profiles.git
cd azure-profiles
```
Alternatively, download the script manually:
```bash
wget https://raw.githubusercontent.com/emvaldes/azure-profiles/refs/heads/master/profile-privileges.ps1
```

## Usage
The script supports multiple modes of operation with flexible parameters.

### **Command-Line Parameters**
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

### **Application Parameters**

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

#### **Example:**

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

#### **Requesting Support**

```powershell
.\profile-privileges.ps1 -Help ;
```

``` powershell
profile-privileges.ps1 [[-ProjectDomain] <String>] [[-Environment] <String>]
[[-ResourceGroup] <String>] [[-DatabaseName] <String>] [-KeyVault] [-Variables]
[-Networking] [-Firewalls] [-EndPoints] [-Listing] [-Inspect] [[-MaxDepth] <Int32>]
[-Verbose] [-Debug] [-Help] [<CommonParameters>]
```

## Output Formats
The script outputs data in multiple formats for analysis:
- **Human-readable tables** (default in PowerShell)
- **JSON format** (`ConvertTo-Json` for structured processing)
- **Standard logs** (written to the console and log files)

## Security Considerations
- **Secrets Handling**: The script retrieves sensitive information such as database credentials and Key Vault secrets. Ensure logs are not stored in unsecured locations.
- **RBAC Permissions**: Running the script requires appropriate privileges to access Azure resources and retrieve sensitive data.
- **Session Management**: Authentication tokens are managed internally to prevent unnecessary re-authentication.

## Troubleshooting
### **Common Issues & Fixes**
| Issue | Cause | Solution |
|-------|-------|----------|
| `Access Denied` error when retrieving secrets | Insufficient Key Vault permissions | Ensure you have `Key Vault Reader` or `Secrets Reader` role. |
| Empty role assignment list | User lacks assigned roles | Check using `az role assignment list --all`. |
| `az not found` | Azure CLI is not installed | Install Azure CLI from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli. |

## Contributions
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the [MIT License](LICENSE).

## Author
[**Eduardo Valdés**](https://github.com/emvaldes)
📧 Contact: [GitHub Issues](https://github.com/emvaldes/azure-profiles/issues)

---

🚀 **Ready to optimize your Azure security and resource management? Run `profile-privileges.ps1` today!** 🚀
