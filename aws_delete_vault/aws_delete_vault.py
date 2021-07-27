# -*- coding:utf-8 -*-
"""aws_delete_vault.

Provides entry points for deleting all archives within an
AWS S3 Glacier vault.

The script will ask for confirmation before deleting any archives,
by default, following the process:

0. The user must first retrieve an inventory of all archives in the
   vault, using the AWS CLI.

aws glacier initiate-job \
    --job-parameters '{"Type": "inventory-retrieval"}' \
    --account-id ACCOUNT_ID \
    --region REGION \
    --vault-name VAULT_NAME

This can take some time, and may be best run before using the script,
depending on the dataset.

To check whether the job is complete and/or obtain the job ID, use:

aws glacier list-jobs \
    --account-id ACCOUNT_ID \
    --region REGION \
    --vault-name YOUR_VAULT_NAME

This will return a job ID, which can be used as input to this program,
which will:

1. Recover an inventory of all archives in the vault, given a job ID,
   an AWS region, an account ID, and a vault name:

aws glacier get-job-output \
    --account-id YOUR_ACCOUNT_ID \
    --region YOUR_REGION \
    --vault-name YOUR_VAULT_NAME \
    --job-id YOUR_JOB_ID \
    ./output.json

2. Load in the JSON output from the previous step, and report summary
   information about the archives contained in the vault.

3. Delete every archive in the vault, using the AWS CLI:

ws glacier delete-archive \
    --archive-id=${archive_id} \
    --vault-name ${AWS_VAULT_NAME} \
    --account-id ${AWS_ACCOUNT_ID} \
    --region ${AWS_REGION}
"""

import json
import logging
import sys

import boto3

from tqdm import tqdm

from aws_delete_vault import __version__
from aws_delete_vault.logger import config_logger
from aws_delete_vault.parser import parse_cmdline


def get_vault(account_id, region_name, vault_name):
    """Return Glacier Vault for account."""
    logger = logging.getLogger(__name__)
    logger.info(
        "Connecting to Glacier vault %s in region %s, as %s.",
        vault_name,
        region_name,
        account_id,
    )

    glacier = boto3.resource("glacier", region_name=region_name)
    vault = glacier.Vault(account_id, vault_name)
    logger.info("Successfully connected to vault %s", vault.vault_name)

    return vault


def check_job_complete(vault, job_id):
    """Return Job object if inventory retrieval job is complete."""
    logger = logging.getLogger(__name__)
    logger.info("Checking for completion of job %s...", job_id[:8])

    # Get completed jobs
    if job_id in (_.id for _ in vault.jobs.filter()):
        logger.info("Found completed job %s...", job_id[:8])
        return [_ for _ in vault.jobs.filter() if _.id == job_id][0]
    else:
        logger.error("Job not complete (exiting)")
        return False


def run_main(argv=None):
    """Run main process for aws_delete_vault."""
    # Parse command-line if no namespace provided
    if argv is None:
        args = parse_cmdline()
    elif isinstance(argv, list):
        args = parse_cmdline(argv)
    else:
        args = argv

    # Catch execution with no arguments
    if len(sys.argv) == 1:
        sys.stderr.write("aws_delete_vault " + "version: {0}\n".format(__version__))
        return 0

    # Configure logging
    config_logger(args)
    logger = logging.getLogger(__name__)
    logger.info("Parsing command-line arguments.")

    # Connect to vault
    vault = get_vault(args.account_id, args.region_name, args.vault_name)

    # Is the inventory retrival job complete? If not, exit
    job = check_job_complete(vault, args.job_id)
    if not job:
        sys.exit(1)

    # Get job output
    logger.info("Retrieving job output.")
    job_output = job.get_output()
    logger.debug("Job output:\n%s", job_output)

    logger.info("Parsing job output.")
    job_data = json.loads(job_output["body"].read())
    logger.info("Vault ARN: %s", job_data["VaultARN"])
    logger.info("Inventory Date: %s", job_data["InventoryDate"])
    logger.info("Archive count: %s", len(job_data["ArchiveList"]))

    # Instantiate Glacier client
    client = boto3.client("glacier", region_name=args.region_name)

    # Delete each archive in the archive list
    if args.dry_run:
        logger.info("--dry_run argument passed, no archives will be deleted")
    for archive in tqdm(job_data["ArchiveList"], desc="Deleting archives"):
        archive_id = archive["ArchiveId"]
        if not args.dry_run:
            logger.debug("Deleting archive %s", archive_id)
            client.delete_archive(args.vault_name, archive_id)

    # Report exit
    logger.info("Finished deleting archives.")
    sys.exit(0)
