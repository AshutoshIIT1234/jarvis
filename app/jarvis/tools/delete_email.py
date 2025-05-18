"""Delete email tool for Gmail integration."""

from .email_utils import get_gmail_service


def delete_email(
    email_id: str,
    trash: bool = True,
) -> dict:
    """
    Delete or trash a specific email by its ID.

    Args:
        email_id (str): The ID of the email to delete
        trash (bool): If True, move to trash; if False, permanently delete

    Returns:
        dict: Status information about the deletion
    """
    try:
        # Get Gmail service
        service = get_gmail_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Gmail. Please check credentials.",
            }

        if trash:
            # Move the message to trash
            service.users().messages().trash(userId="me", id=email_id).execute()
            action = "moved to trash"
        else:
            # Permanently delete the message
            service.users().messages().delete(userId="me", id=email_id).execute()
            action = "permanently deleted"

        return {
            "status": "success",
            "message": f"Email {action} successfully",
        }

    except Exception as e:
        return {"status": "error", "message": f"Error deleting email: {str(e)}"}