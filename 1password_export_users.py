"""
Script: 1password_export_users - Export 1Password Team Users to CSV

Description:
This script fetches all users in a 1Password Teams account using the 1Password CLI (`op`) 
and exports them to a CSV file. The script identifies users with specific states ("ACTIVE" 
or "RECOVERY_STARTED") for license monitoring purposes. The 1Password CLI must be installed 
and configured with a Service Account Token.

Requirements:
- 1Password CLI (`op`) must be installed on the system.
- A valid 1Password Service Account Token with permissions to list users.
- The following environment variables must be set:
    - `OP_SERVICE_ACCOUNT_TOKEN`: Service Account Token for authentication with 1Password.
    - `OUTPUT_CSV`: (Optional) File path to save the exported user list in CSV format.

Functions:
- fetch_users: Runs the `op user list` command to fetch all users in JSON format.
- export_to_csv: Exports the fetched users to a CSV file.

Usage:
1. Install the 1Password CLI:
   For Linux:
       sudo apt install -y curl gpg
       curl -sS https://downloads.1password.com/linux/keys/1password.asc | sudo gpg --dearmor -o /usr/share/keyrings/1password-archive-keyring.gpg
       echo 'deb [signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/amd64 stable main' | sudo tee /etc/apt/sources.list.d/1password.list
       sudo apt update && sudo apt install 1password-cli

2. Set the Service Account Token as an environment variable:
   export OP_SERVICE_ACCOUNT_TOKEN="your-service-account-token"

3. Run the script:
   python 1password_export_users.py

4. Output:
   The script generates a CSV file containing user details such as ID, Email, Name, and State.

Notes:
- Ensure the Service Account Token has the necessary permissions to access user data.
- The `op` CLI uses the `OP_SERVICE_ACCOUNT_TOKEN` environment variable automatically for authentication.

Author: Chad Ramey
Date: December 17, 2024
"""

import csv
import json
import os
import subprocess

# Output CSV file
OUTPUT_CSV = "1password_team_users.csv"

def fetch_users():
    """Fetch users from 1Password using the 'op' CLI."""
    try:
        # Check if the token is set
        if not os.getenv("OP_SERVICE_ACCOUNT_TOKEN"):
            raise ValueError("OP_SERVICE_ACCOUNT_TOKEN environment variable is not set.")

        print("Fetching list of users from 1Password...")
        # Run 'op user list --format json' using the service account token
        result = subprocess.run(
            ["op", "user", "list", "--format", "json"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Parse the JSON output
        users = json.loads(result.stdout)
        return users
    except subprocess.CalledProcessError as e:
        print(f"Error running 'op' command: {e.stderr}")
        return []
    except Exception as ex:
        print(f"Error: {ex}")
        return []

def export_to_csv(users):
    """Export fetched users to a CSV file."""
    if not users:
        print("No users found to export.")
        return

    print(f"Exporting {len(users)} users to {OUTPUT_CSV}...")

    # Define CSV headers
    headers = ["ID", "Email", "Name", "State"]

    try:
        with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            # Write user data to CSV
            for user in users:
                writer.writerow({
                    "ID": user.get("id", ""),
                    "Email": user.get("email", ""),
                    "Name": user.get("name", ""),
                    "State": user.get("state", "")
                })

        print(f"Successfully exported users to {OUTPUT_CSV}.")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def main():
    """Main function to fetch users and export to CSV."""
    users = fetch_users()
    export_to_csv(users)

if __name__ == "__main__":
    main()
