# -*- coding: utf-8 -*-
"""parser.py

Provides the CLI parser for aws_delete_vault
"""

import sys

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path

import boto3


# Process command-line for ncbi_cds_from_protein script
def parse_cmdline(args=None):
    """Parse command-line arguments for script."""
    # Try to get the current user's AWS account ID from the environment
    try:
        account_id = boto3.client("sts").get_caller_identity().get("Account")
    except Exception:
        account_id = None

    # Try to get the current user's default AWS region
    region_name = boto3.session.Session().region_name

    parser = ArgumentParser(
        prog="aws_delete_vault", formatter_class=ArgumentDefaultsHelpFormatter
    )

    # Add compulsory arguments
    parser.add_argument(
        action="store",
        dest="vault_name",
        default=None,
        help="name of Glacier vault",
        type=str,
    )
    parser.add_argument(
        action="store",
        dest="job_id",
        default=None,
        help="job ID of archive inventory retrieval",
        type=str,
    )

    # Add options
    parser.add_argument(
        "--account_id",
        dest="account_id",
        action="store",
        default=account_id,
        help="AWS account ID (numeric)",
        type=str,
    )
    parser.add_argument(
        "--region_name",
        dest="region_name",
        action="store",
        default=region_name,
        type=str,
        help="AWS region name (XX-XXXX-X)",
    )
    parser.add_argument(
        "-l",
        "--logfile",
        dest="logfile",
        action="store",
        default=None,
        type=Path,
        help="path to logfile",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="report verbosely",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="report debug-level information",
    )
    parser.add_argument(
        "--disabletqdm",
        dest="disabletqdm",
        action="store_true",
        default=False,
        help="disable progress bar (for testing)",
    )
    parser.add_argument(
        "--dry_run",
        dest="dry_run",
        action="store_true",
        default=False,
        help="dry run (do not delete archives)",
    )

    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    else:
        args = map(str, args)  # Ensure that args look like what we get from CLI
    return parser.parse_args(args)
