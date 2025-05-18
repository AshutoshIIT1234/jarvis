"""Utility functions for GitHub integration."""

import json
import os
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# Path for token storage
TOKEN_PATH = Path(os.path.expanduser("~/.credentials/github_token.json"))


def get_github_auth():
    """
    Get GitHub authentication credentials.

    Returns:
        tuple: (username, token) or (None, None) if authentication fails
    """
    try:
        if TOKEN_PATH.exists():
            credentials = json.loads(TOKEN_PATH.read_text())
            return credentials.get("username"), credentials.get("token")
        else:
            print(f"Error: {TOKEN_PATH} not found. Please run setup_github_auth.py first.")
            return None, None
    except Exception as e:
        print(f"Error loading GitHub credentials: {str(e)}")
        return None, None


def get_github_headers():
    """
    Get headers for GitHub API requests.

    Returns:
        dict: Headers for GitHub API requests or None if authentication fails
    """
    username, token = get_github_auth()
    if not username or not token:
        return None

    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }


def test_github_connection():
    """
    Test the connection to GitHub API.

    Returns:
        dict: User information or error details
    """
    username, token = get_github_auth()
    if not username or not token:
        return {
            "status": "error",
            "message": "GitHub credentials not found. Please run setup_github_auth.py."
        }

    try:
        response = requests.get(
            "https://api.github.com/user",
            auth=HTTPBasicAuth(username, token),
            headers={"Accept": "application/vnd.github.v3+json"}
        )

        if response.status_code == 200:
            return {
                "status": "success",
                "message": f"Connected to GitHub as {response.json()['login']}",
                "user": response.json()
            }
        else:
            return {
                "status": "error",
                "message": f"GitHub API error: {response.status_code} - {response.text}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error connecting to GitHub: {str(e)}"
        }