"""GitHub tools for repository operations."""

import base64
import json
from pathlib import Path

import requests

from .github_utils import get_github_auth, get_github_headers


def list_repositories() -> dict:
    """
    List repositories for the authenticated user.

    Returns:
        dict: Information about repositories or error details
    """
    try:
        headers = get_github_headers()
        if not headers:
            return {
                "status": "error",
                "message": "Failed to authenticate with GitHub. Please check credentials.",
                "repositories": []
            }

        # Get list of repositories
        response = requests.get(
            "https://api.github.com/user/repos",
            headers=headers
        )

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"GitHub API error: {response.status_code} - {response.text}",
                "repositories": []
            }

        repos = response.json()

        if not repos:
            return {
                "status": "success",
                "message": "No repositories found.",
                "repositories": []
            }

        # Format repositories for display
        formatted_repos = []
        for repo in repos:
            formatted_repos.append({
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "private": repo.get("private"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "language": repo.get("language")
            })

        return {
            "status": "success",
            "message": f"Found {len(formatted_repos)} repositories.",
            "repositories": formatted_repos
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing repositories: {str(e)}",
            "repositories": []
        }


def create_repository(name: str, description: str = "", private: bool = False) -> dict:
    """
    Create a new repository.

    Args:
        name (str): Name of the repository
        description (str): Description of the repository
        private (bool): Whether the repository should be private

    Returns:
        dict: Information about the created repository or error details
    """
    try:
        headers = get_github_headers()
        if not headers:
            return {
                "status": "error",
                "message": "Failed to authenticate with GitHub. Please check credentials."
            }

        # Create repository
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True  # Initialize with README
        }

        response = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=data
        )

        if response.status_code not in [200, 201]:
            return {
                "status": "error",
                "message": f"GitHub API error: {response.status_code} - {response.text}"
            }

        repo = response.json()
        return {
            "status": "success",
            "message": f"Repository '{name}' created successfully.",
            "repository": {
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "clone_url": repo.get("clone_url"),
                "private": repo.get("private")
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating repository: {str(e)}"
        }


def scan_repository(repo_name: str, path: str = "") -> dict:
    """
    Scan a repository to list files and directories.

    Args:
        repo_name (str): Name of the repository (format: username/repo)
        path (str): Path within the repository to scan

    Returns:
        dict: Information about repository contents or error details
    """
    try:
        headers = get_github_headers()
        if not headers:
            return {
                "status": "error",
                "message": "Failed to authenticate with GitHub. Please check credentials.",
                "contents": []
            }

        # Get repository contents
        url = f"https://api.github.com/repos/{repo_name}/contents"
        if path:
            url += f"/{path}"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"GitHub API error: {response.status_code} - {response.text}",
                "contents": []
            }

        contents = response.json()

        if not contents:
            return {
                "status": "success",
                "message": "No contents found.",
                "contents": []
            }

        # Format contents for display
        formatted_contents = []
        if isinstance(contents, list):
            for item in contents:
                formatted_contents.append({
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "type": item.get("type"),  # file or dir
                    "size": item.get("size"),
                    "url": item.get("html_url")
                })
        else:
            # Single file response
            formatted_contents.append({
                "name": contents.get("name"),
                "path": contents.get("path"),
                "type": contents.get("type"),
                "size": contents.get("size"),
                "url": contents.get("html_url")
            })

        return {
            "status": "success",
            "message": f"Found {len(formatted_contents)} items in repository.",
            "contents": formatted_contents
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error scanning repository: {str(e)}",
            "contents": []
        }


def push_to_repository(repo_name: str, file_path: str, content: str, commit_message: str) -> dict:
    """
    Push a file to a repository.

    Args:
        repo_name (str): Name of the repository (format: username/repo)
        file_path (str): Path to the file in the repository
        content (str): Content of the file
        commit_message (str): Commit message

    Returns:
        dict: Information about the push operation or error details
    """
    try:
        headers = get_github_headers()
        if not headers:
            return {
                "status": "error",
                "message": "Failed to authenticate with GitHub. Please check credentials."
            }

        # Check if file exists to get the SHA (needed for update)
        url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
        response = requests.get(url, headers=headers)
        sha = None

        if response.status_code == 200:
            # File exists, get SHA for update
            sha = response.json().get("sha")

        # Prepare data for creating/updating file
        data = {
            "message": commit_message,
            "content": base64.b64encode(content.encode()).decode()
        }

        if sha:
            data["sha"] = sha

        # Create or update file
        response = requests.put(url, headers=headers, json=data)

        if response.status_code not in [200, 201]:
            return {
                "status": "error",
                "message": f"GitHub API error: {response.status_code} - {response.text}"
            }

        result = response.json()
        return {
            "status": "success",
            "message": f"File '{file_path}' pushed to repository successfully.",
            "commit": {
                "sha": result.get("commit", {}).get("sha"),
                "url": result.get("commit", {}).get("html_url")
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error pushing to repository: {str(e)}"
        }