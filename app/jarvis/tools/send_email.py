"""Send email tool for Gmail integration."""

from .email_utils import get_gmail_service, create_message


def send_email(
    to: str,
    subject: str,
    body: str,
    is_html: bool = False,
) -> dict:
    """
    Send an email using Gmail.

    Args:
        to (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content
        is_html (bool): Whether the body content is HTML

    Returns:
        dict: Information about the sent email or error details
    """
    try:
        # Get Gmail service
        service = get_gmail_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Gmail. Please check credentials.",
            }

        # Get user's email address (sender)
        profile = service.users().getProfile(userId="me").execute()
        sender = profile.get("emailAddress")

        # Create the email message
        message = create_message(sender, to, subject, body, is_html)

        # Send the email
        sent_message = (
            service.users()
            .messages()
            .send(userId="me", body=message)
            .execute()
        )

        return {
            "status": "success",
            "message": "Email sent successfully",
            "message_id": sent_message["id"],
        }

    except Exception as e:
        return {"status": "error", "message": f"Error sending email: {str(e)}"}