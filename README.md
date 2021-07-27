# `aws_delete_vault`

This repository provides a script to delete all archives in an AWS S3 Glacier vault, a necessary step in preparing a vault for deletion.

## Installation

Clone the repository to your local filesystem, and install with `python setup.py install`

```bash
git clone
cd
python setup.py install
```

## Usage

For basic help and information, use the `-h` or `--help` flag

```bash
aws_delete_vault -h
aws_delete_vault --help
```

### Preparation

Before running the script, you will need to obtain an inventory of all archives in the vault. To do this using the AWS CLI, issue the command:

```bash
aws glacier initiate-job \
    --job-parameters '{"Type": "inventory-retrieval"}' \
    --account-id ACCOUNT_ID \
    --region REGION \
    --vault-name VAULT_NAME
```

- `ACCOUNT_ID` should be the numerical ID for the account
- `REGION` should be in the form (e.g.) `us-east-1`
- `VAULT_NAME` should be the human-readable name for the vault

If your vault is large or contains many archives, this job may take some time. To check progress using the AWS CLI, issue the command:

```bash
aws glacier list-jobs \
    --account-id ACCOUNT_ID \
    --region REGION \
    --vault-name YOUR_VAULT_NAME
```

This will return JSON formatted output of the form

```json
{
    "JobList": [
        {
            "JobId": "XXXXXXXXXXX",
            "Action": "InventoryRetrieval",
            "VaultARN": "XXXXXXXXXXX",
            "CreationDate": "XXXXXXXXXXX",
            "Completed": true,
            "StatusCode": "Succeeded",
            "StatusMessage": "Succeeded",
            "InventorySizeInBytes": NNNNNNNNNNNNNN,
            "CompletionDate": "XXXXXXXXXXX",
            "InventoryRetrievalParameters": {
                "Format": "JSON"
            }
        }
    ]
}
```

The key fields are `"Completed"` and `"StatusCode"`; when the job is complete, `"Completed"` will have value `true` and `"StatusCode"` will have value `"Succeeded"` as above. If this is the case, then you are ready to proceed using the script, which will require the value in the `"JobId"` field.

### Basic usage

To delete all archives in the vault using the information from the job indicated above, issue the command:

```bash
aws_delete_vault VAULT_NAME JOB_ID
```

This will first check that the job with ID `JOB_ID` is completed, then use its output to identify all outputs in `VAULT_NAME`, and delete them, one-by one

### Setting account ID and region name

The program will attempt to use your local AWS default settings for account ID and region name as configured with the AWS CLI `aws configure` command. If this information is not available, or you want to use options other than these defaults, you can use the arguments `--account_id` and `--region_name`, e.g.:

```bash
aws_delete_vault --account_id ACCOUNT_ID --region_name REGION_NAME VAULT_NAME JOB_ID
```

### Logging and advanced use

You can specify the path to a log file with the `-l`/`--logfile` arguments:

```bash
aws_delete_vault -l delete_archives.log VAULT_NAME JOB_ID
```

Verbose or debug-level output can be viewed in the terminal with the `-v`/`--verbose` or `--debug` arguments:

```bash
aws_delete_vault -v VAULT_NAME JOB_ID
aws_delete_vault --debug VAULT_NAME JOB_ID
```

To perform a dry-run that deletes no archives but confirms that the vault can be reached and archives identified, use the `--dry_run` argument, e.g.:

```bash
aws_delete_vault -v --dry_run VAULT_NAME JOB_ID
```