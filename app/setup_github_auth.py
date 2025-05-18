#!/usr/bin/env python3
"""
GitHub Authentication Setup Script

This script helps you set up authentication for GitHub integration.
Follow the instructions in the console.
"""

import json
import os
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# Path for token storage
TOKEN_PATH = Path(os.path.expanduser("~/.credentials/github_token.json"))


def setup_oauth():
    """Set up authentication for GitHub"""
    print("\n=== GitHub Authentication Setup ===\n")

    # Ask for GitHub username and personal access token
    username = input("Enter your GitHub username: ")
    token = input("Enter your GitHub personal access token: ")

    # Validate the credentials
    print("\nValidating GitHub credentials...")
    try:
        # Test the API connection
        response = requests.get(
            "https://api.github.com/user",
            auth=HTTPBasicAuth(username, token),
            headers={"Accept": "application/vnd.github.v3+json"}
        )

        if response.status_code == 200:
            user_data = response.json()
            print(f"\nSuccess! Connected to GitHub API for: {user_data['login']}")

            # Save the credentials
            credentials = {
                "username": username,
                "token": token
            }

            # Save the credentials for the next run
            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            TOKEN_PATH.write_text(json.dumps(credentials))

            print(f"\nSuccessfully saved credentials to {TOKEN_PATH}")
            print("\nGitHub authentication setup complete! You can now use the GitHub integration.")
            return True
        else:
            print(f"\nError: Authentication failed. Status code: {response.status_code}")
            print("Please check your username and personal access token and try again.")
            return False

    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        return False


if __name__ == "__main__":
    setup_oauth()