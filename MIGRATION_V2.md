# Azure ML SDK v2 Migration

This version migrates from Azure ML SDK v1 (`azureml-core`) to Azure ML SDK v2 (`azure-ai-ml`) while maintaining the exact same API.

## What Changed Under the Hood

- **Dependency**: `azureml-core` → `azure-ai-ml`
- **Authentication**: Now uses `DefaultAzureCredential` from Azure Identity
- **Core Objects**: `Workspace` → `MLClient`, `Run` → `Job` (wrapped for compatibility)

## What Stayed the Same

- **CLI Interface**: All commands and options remain identical
- **Function Signatures**: All Python APIs unchanged
- **Configuration**: Existing config files continue to work

## Authentication Setup

The new SDK requires explicit authentication. Before using the tool, ensure you're authenticated:

```bash
# Option 1: Azure CLI (recommended)
az login

# Option 2: Environment variables
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret" 
export AZURE_TENANT_ID="your-tenant-id"

# Option 3: Use managed identity (on Azure VMs)
# No setup required - works automatically
```

## Known Limitations

1. **File Listing**: V2 SDK has more limited file discovery compared to v1. The tool now:
   - Lists available log files from the job
   - Includes common output paths
   - May not find all files that v1 could access

2. **Download Behavior**: File downloads use different strategies:
   - Log files downloaded directly via URLs
   - Other files downloaded via job outputs
   - Some files may create placeholder content if not accessible

## Troubleshooting

### Authentication Errors
```
DefaultAzureCredential failed to retrieve a token
```
**Solution**: Run `az login` or set up environment variables as shown above.

### File Not Found
```
No files found in run "run-id" matching "path"
```
**Solution**: The v2 SDK has limited file access. Try:
- Downloading all files first: `--source-aml-path` (omit this flag)
- Using common log paths: `user_logs`, `azureml-logs`

## Migration Checklist

For existing users upgrading:

- [ ] No code changes required
- [ ] Ensure authentication is set up (`az login`)
- [ ] Test your workflows with a few runs
- [ ] Report any issues with file access

## Rollback

If you need to use the v1 SDK, install the previous version:

```bash
uv tool install --python "<3.13" --from azure-tools==0.1.2 aml
```