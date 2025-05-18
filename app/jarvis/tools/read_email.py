"""Read email tool for Gmail integration."""

from .email_utils import get_gmail_service, format_message


def read_email(
    email_id: str,
) -> dict:
    """
    Read a specific email by its ID.

    Args:
        email_id (str): The ID of the email to read

    Returns:
        dict: The full email content or error details
    """
    try:
        # Get Gmail service
        service = get_gmail_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Gmail. Please check credentials.",
            }

        # Get the full message
        message = (
            service.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )

        # Format the message
        formatted_message = format_message(message)

        return {
            "status": "success",
            "message": "Email retrieved successfully",
            "email": formatted_message,
        }

    except Exception as e:
        return {"status": "error", "message": f"Error reading email: {str(e)}"}