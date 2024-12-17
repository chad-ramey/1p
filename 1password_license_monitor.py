"""
Script: 1password_license_monitor - Monitor 1Password License Usage and Send Alerts

Description:
This script monitors 1Password license usage by fetching all users from the 1Password Teams account 
using the 1Password CLI (`op`). It filters users with states "ACTIVE" or "RECOVERY_STARTED" to determine 
the number of used licenses and compares it against a predefined total. Alerts are sent to a Slack channel 
via a webhook if license usage exceeds the allocated limit.

Functions:
- fetch_users: Fetches all users using the 1Password CLI (`op user list`).
- count_active_licenses: Counts users with an "ACTIVE" or "RECOVERY_STARTED" state.
- send_slack_notification: Sends a summary or alert message to a Slack channel via webhook.
- main: Main function to fetch user data, calculate license usage, and trigger Slack notifications.

Usage:
1. Install the 1Password CLI (`op`) on your system or GitHub Actions runner.
2. Set the following environment variables:
   - `OP_SERVICE_ACCOUNT_TOKEN`: 1Password Service Account Token for CLI authentication.
   - `SLACK_WEBHOOK_URL`: Webhook URL for Slack alerts.
3. Run the script in a Python environment or via GitHub Actions.

Notes:
- Ensure the 1Password CLI is properly authenticated using the Service Account Token.
- Adjust the `TOTAL_LICENSES` variable to reflect your organization's license allocation.
- A Slack alert will be triggered if the number of used licenses exceeds the total allocated.

Author: Chad Ramey  
Date: December 17, 2024
"""

import csv
import json
import os
import subprocess
import requests

# Constants
TOTAL_LICENSES = 3000  # Total allocated licenses
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # Slack Webhook for notifications

def fetch_users():
    """
    Fetch all users using the 1Password CLI.

    Returns:
        List of users with their details in JSON format.
    """
    try:
        print("Fetching list of users from 1Password...")
        result = subprocess.run(
            ["op", "user", "list", "--format", "json"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        users = json.loads(result.stdout)
        return users
    except subprocess.CalledProcessError as e:
        print(f"Error running 'op' command: {e.stderr}")
        return []

def count_active_licenses(users):
    """
    Count the number of active licenses.

    Args:
        users (list): List of user objects from 1Password.

    Returns:
        int: Count of users in 'ACTIVE' or 'RECOVERY_STARTED' states.
    """
    active_states = {"ACTIVE", "RECOVERY_STARTED"}
    return sum(1 for user in users if user.get("state") in active_states)

def send_slack_notification(used_licenses, total_licenses):
    """
    Send a notification to Slack summarizing license usage or alerting for overage.

    Args:
        used_licenses (int): Number of used licenses.
        total_licenses (int): Total allocated licenses.
    """
    if used_licenses > total_licenses:
        message = (
            f":rotating_light::1password: *1Password License Alert* :1password::rotating_light:\n\n"
            f"Used Licenses: {used_licenses}\n"
            f"Total Licenses**: {total_licenses}\n"
            f"Overage: {used_licenses - total_licenses}\n\n"
            f"*Immediate action required to resolve the overage.*"
        )
    else:
        message = (
            f":1password: *1Password License Report* :1password:\n\n"
            f"Used Licenses: {used_licenses}\n"
            f"Total Licenses: {total_licenses}\n"
            f"Available Licenses: {total_licenses - used_licenses}\n\n"
            f"*All licenses are within the allocated limit.*"
        )

    payload = {"text": message}

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Slack notification sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Slack notification: {e}")

def main():
    """
    Main function to fetch users, calculate licenses, and send Slack notifications.
    """
    users = fetch_users()
    if not users:
        print("No users fetched. Exiting.")
        return

    used_licenses = count_active_licenses(users)
    print(f"Used Licenses: {used_licenses}/{TOTAL_LICENSES}")
    send_slack_notification(used_licenses, TOTAL_LICENSES)

if __name__ == "__main__":
    main()
