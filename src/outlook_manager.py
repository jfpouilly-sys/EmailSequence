"""Outlook COM automation for email operations."""
from datetime import datetime, timedelta
from typing import Optional
import win32com.client
import pythoncom


class OutlookManager:
    """Handle all Outlook COM automation."""

    def __init__(self):
        """
        Initialize Outlook COM connection.

        Raises:
            ConnectionError: If Outlook is not running/available
        """
        try:
            self.outlook = win32com.client.Dispatch('Outlook.Application')
            self.namespace = self.outlook.GetNamespace('MAPI')
        except Exception as e:
            raise ConnectionError(
                "Could not connect to Microsoft Outlook.\n"
                "Please ensure Outlook is installed and try again.\n"
                f"Error: {str(e)}"
            )

    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        dry_run: bool = False
    ) -> dict:
        """
        Send an email via Outlook.

        Args:
            to: Recipient email address
            subject: Email subject line
            html_body: HTML-formatted email body
            dry_run: If True, display email instead of sending

        Returns:
            {
                "success": bool,
                "conversation_id": str,  # From mail.ConversationTopic
                "sent_time": datetime,
                "error": str | None
            }
        """
        try:
            mail = self.outlook.CreateItem(0)  # 0 = MailItem
            mail.To = to
            mail.Subject = subject
            mail.HTMLBody = html_body

            sent_time = datetime.now()

            if dry_run:
                # Display email in Outlook window instead of sending
                mail.Display()
                conversation_id = subject  # Use subject as fallback in dry run
            else:
                # Actually send the email
                mail.Send()
                # ConversationTopic is assigned by Outlook after sending
                # It might be the same as subject or a normalized version
                conversation_id = subject

            return {
                "success": True,
                "conversation_id": conversation_id,
                "sent_time": sent_time,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "conversation_id": None,
                "sent_time": None,
                "error": str(e)
            }

    def check_for_reply(
        self,
        original_subject: str,
        sender_email: str,
        since_date: datetime
    ) -> Optional[dict]:
        """
        Check inbox for reply from a specific sender.

        Args:
            original_subject: The subject line we sent (or ConversationTopic)
            sender_email: Email address to look for
            since_date: Only check emails received after this date

        Returns:
            None if no reply found, or:
            {
                "received_time": datetime,
                "subject": str,
                "preview": str  # First 200 chars of body
            }
        """
        try:
            inbox = self.namespace.GetDefaultFolder(6)  # 6 = Inbox
            messages = inbox.Items
            messages.Sort("[ReceivedTime]", True)  # Sort by newest first

            # Normalize sender email for comparison
            sender_email_lower = sender_email.lower().strip()

            for message in messages:
                try:
                    # Check received time
                    received_time = message.ReceivedTime
                    if received_time < since_date:
                        # Messages are sorted, so we can stop here
                        break

                    # Get sender email address
                    msg_sender = self._get_sender_email(message)
                    if not msg_sender:
                        continue

                    # Check if sender matches
                    if msg_sender.lower().strip() != sender_email_lower:
                        continue

                    # Check if it's part of the conversation
                    # Check both ConversationTopic and Subject
                    conversation_topic = getattr(message, 'ConversationTopic', '')
                    msg_subject = getattr(message, 'Subject', '')

                    if (original_subject in conversation_topic or
                        original_subject in msg_subject or
                        self._is_reply_subject(msg_subject, original_subject)):

                        # Get preview of body
                        body = getattr(message, 'Body', '')
                        preview = body[:200] if body else ''

                        return {
                            "received_time": received_time,
                            "subject": msg_subject,
                            "preview": preview
                        }

                except Exception:
                    # Skip messages that cause errors
                    continue

            return None

        except Exception:
            return None

    def get_recent_replies(
        self,
        known_contacts: list[str],
        days_back: int = 30
    ) -> list[dict]:
        """
        Batch scan inbox for replies from any known contact.

        Args:
            known_contacts: List of email addresses to look for
            days_back: How many days back to scan

        Returns:
            List of {
                "sender_email": str,
                "received_time": datetime,
                "subject": str,
                "conversation_topic": str
            }
        """
        results = []

        try:
            inbox = self.namespace.GetDefaultFolder(6)  # 6 = Inbox
            messages = inbox.Items
            messages.Sort("[ReceivedTime]", True)  # Sort by newest first

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_back)

            # Normalize contact emails for comparison
            contact_emails = {email.lower().strip() for email in known_contacts}

            for message in messages:
                try:
                    # Check received time
                    received_time = message.ReceivedTime
                    if received_time < cutoff_date:
                        # Messages are sorted, so we can stop here
                        break

                    # Get sender email address
                    msg_sender = self._get_sender_email(message)
                    if not msg_sender:
                        continue

                    # Check if sender is in our contact list
                    if msg_sender.lower().strip() in contact_emails:
                        conversation_topic = getattr(message, 'ConversationTopic', '')
                        msg_subject = getattr(message, 'Subject', '')

                        results.append({
                            "sender_email": msg_sender,
                            "received_time": received_time,
                            "subject": msg_subject,
                            "conversation_topic": conversation_topic
                        })

                except Exception:
                    # Skip messages that cause errors
                    continue

        except Exception:
            pass

        return results

    def is_outlook_running(self) -> bool:
        """Check if Outlook application is available."""
        try:
            # Try to get the Outlook application
            outlook = win32com.client.Dispatch('Outlook.Application')
            return True
        except Exception:
            return False

    def _get_sender_email(self, message) -> Optional[str]:
        """
        Extract sender email address from message.
        Handles both SMTP and Exchange format.

        Args:
            message: Outlook message object

        Returns:
            Email address or None
        """
        try:
            # Try SenderEmailAddress first
            sender = getattr(message, 'SenderEmailAddress', '')

            # If it's an Exchange format (starts with /O=), try to get SMTP
            if sender and sender.startswith('/O='):
                try:
                    # Try to get SMTP address from Sender property
                    sender_obj = message.Sender
                    if sender_obj:
                        smtp_address = getattr(sender_obj, 'Address', '')
                        if smtp_address and '@' in smtp_address:
                            return smtp_address
                except Exception:
                    pass

            # Return the address if it looks like an email
            if sender and '@' in sender:
                return sender

            # Try Reply recipients as fallback
            try:
                reply_recipients = message.ReplyRecipients
                if reply_recipients.Count > 0:
                    reply_addr = getattr(reply_recipients.Item(1), 'Address', '')
                    if reply_addr and '@' in reply_addr:
                        return reply_addr
            except Exception:
                pass

            return None

        except Exception:
            return None

    def _is_reply_subject(self, subject: str, original: str) -> bool:
        """
        Check if subject is a reply to original.

        Args:
            subject: Subject line to check
            original: Original subject line

        Returns:
            True if subject appears to be a reply to original
        """
        # Remove common reply prefixes
        subject_clean = subject.lower().strip()
        original_clean = original.lower().strip()

        # Remove RE:, FW:, FWD: etc.
        prefixes = ['re:', 'fw:', 'fwd:', 'aw:']
        for prefix in prefixes:
            if subject_clean.startswith(prefix):
                subject_clean = subject_clean[len(prefix):].strip()

        return original_clean in subject_clean or subject_clean in original_clean
