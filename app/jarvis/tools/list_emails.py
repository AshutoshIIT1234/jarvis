"""List emails tool for Gmail integration."""

from .email_utils import get_gmail_service, format_message


def list_emails(
    max_results: int = 10,
    query: str = "",
    label: str = "INBOX",
) -> dict:
    """
    List emails from Gmail.

    Args:
        max_results (int): Maximum number of emails to return
        query (str): Search query (Gmail search syntax)
        label (str): Gmail label to search in (default: INBOX)

    Returns:
        dict: Information about emails or error details
    """
    try:
        # Get Gmail service
        service = get_gmail_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Gmail. Please check credentials.",
                "emails": [],
            }

        # Build the query
        search_query = f"label:{label}"
        if query:
            search_query += f" {query}"

        # Get list of messages
        results = (
            service.users()
            .messages()
            .list(userId="me", q=search_query, maxResults=max_results)
            .execute()
        )

        messages = results.get("messages", [])

        if not messages:
            return {
                "status": "success",
                "message": "No emails found.",
                "emails": [],
            }

        # Get full message details and format them
        emails = []
        for msg in messages:
            message = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="full")
                .execute()
            )
            emails.append(format_message(message))

        return {
            "status": "success",
            "message": f"Found {len(emails)} emails.",
            "emails": emails,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing emails: {str(e)}",
            "emails": [],
        }