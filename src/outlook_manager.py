"""Outlook COM automation for email operations."""
from datetime import datetime, timedelta
from typing import Optional
import os
import logging
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
        self.logger = logging.getLogger(__name__)

        try:
            self.logger.info("[OUTLOOK API] Initializing Outlook COM connection...")
            self.logger.info("[OUTLOOK API] Calling win32com.client.Dispatch('Outlook.Application')")
            self.outlook = win32com.client.Dispatch('Outlook.Application')

            self.logger.info("[OUTLOOK API] Calling GetNamespace('MAPI')")
            self.namespace = self.outlook.GetNamespace('MAPI')

            # Get Outlook version for logging
            try:
                version = self.outlook.Version
                self.logger.info(f"[OUTLOOK API] Successfully connected to Outlook version {version}")
            except:
                self.logger.info("[OUTLOOK API] Successfully connected to Outlook (version unknown)")

        except Exception as e:
            self.logger.error(f"[OUTLOOK API] Failed to connect to Outlook: {str(e)}")
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
        dry_run: bool = False,
        send_mode: str = "send",
        defer_hours: int = 0,
        msg_folder: str = ""
    ) -> dict:
        """
        Send an email via Outlook with flexible sending options.

        Args:
            to: Recipient email address
            subject: Email subject line
            html_body: HTML-formatted email body
            dry_run: If True, display email instead of sending
            send_mode: "send" (immediate), "msg_file" (save as .msg), or "defer" (delay send)
            defer_hours: Hours to defer sending (only used if send_mode="defer")
            msg_folder: Folder path for saving .msg files (only used if send_mode="msg_file")

        Returns:
            {
                "success": bool,
                "conversation_id": str,  # From mail.ConversationTopic
                "sent_time": datetime,
                "error": str | None,
                "msg_file_path": str | None  # Path to .msg file if send_mode="msg_file"
            }
        """
        try:
            self.logger.info(f"[OUTLOOK API] Creating email: To={to}, Subject='{subject}', Mode={send_mode}")

            self.logger.debug("[OUTLOOK API] Calling outlook.CreateItem(0) to create MailItem")
            mail = self.outlook.CreateItem(0)  # 0 = MailItem

            mail.To = to
            mail.Subject = subject
            mail.HTMLBody = html_body
            self.logger.debug(f"[OUTLOOK API] Email properties set (body length: {len(html_body)} chars)")

            sent_time = datetime.now()
            msg_file_path = None

            if dry_run:
                # Display email in Outlook window instead of sending
                self.logger.info("[OUTLOOK API] DRY RUN mode - Calling mail.Display()")
                mail.Display()
                conversation_id = subject  # Use subject as fallback in dry run
                self.logger.info(f"[OUTLOOK API] Email displayed for review: {to}")

            elif send_mode == "msg_file":
                # Save as .msg file
                if not msg_folder:
                    raise ValueError("msg_folder must be specified when send_mode='msg_file'")

                # Create folder if it doesn't exist
                abs_folder = os.path.abspath(msg_folder)
                os.makedirs(msg_folder, exist_ok=True)
                self.logger.info(f"[FILE WRITE] .msg output folder: {abs_folder}")

                # Generate filename: YYYYMMDD_HHMMSS_recipient.msg
                timestamp = sent_time.strftime("%Y%m%d_%H%M%S")
                # Sanitize email for filename
                safe_email = to.replace("@", "_at_").replace(".", "_")
                filename = f"{timestamp}_{safe_email}.msg"
                msg_file_path = os.path.join(msg_folder, filename)
                abs_msg_path = os.path.abspath(msg_file_path)

                # Save the message
                self.logger.info(f"[OUTLOOK API] Calling mail.SaveAs('{abs_msg_path}', 3) to save .msg file")
                mail.SaveAs(msg_file_path, 3)  # 3 = olMSG format
                file_size = os.path.getsize(msg_file_path)
                self.logger.info(f"[FILE WRITE] Saved .msg file: {abs_msg_path} ({file_size} bytes)")
                conversation_id = subject

            elif send_mode == "defer":
                # Schedule deferred delivery
                if defer_hours > 0:
                    defer_time = sent_time + timedelta(hours=defer_hours)
                    self.logger.info(f"[OUTLOOK API] Setting DeferredDeliveryTime to {defer_time} (in {defer_hours} hours)")
                    mail.DeferredDeliveryTime = defer_time

                # Send the email (it will be held in Outbox until defer time)
                self.logger.info(f"[OUTLOOK API] Calling mail.Send() - email will be sent at {defer_time if defer_hours > 0 else 'next send/receive'}")
                mail.Send()
                self.logger.info(f"[OUTLOOK API] Deferred email queued for {to}")
                conversation_id = subject

            else:  # send_mode == "send" (default)
                # Actually send the email immediately
                self.logger.info(f"[OUTLOOK API] Calling mail.Send() to send email immediately")
                mail.Send()
                # ConversationTopic is assigned by Outlook after sending
                # It might be the same as subject or a normalized version
                conversation_id = subject
                self.logger.info(f"[OUTLOOK API] Email sent successfully to {to}")

            return {
                "success": True,
                "conversation_id": conversation_id,
                "sent_time": sent_time,
                "error": None,
                "msg_file_path": msg_file_path
            }

        except Exception as e:
            self.logger.error(f"[OUTLOOK API] Failed to send email to {to}: {str(e)}")
            return {
                "success": False,
                "conversation_id": None,
                "sent_time": None,
                "error": str(e),
                "msg_file_path": None
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
            self.logger.info(f"[OUTLOOK API] Scanning inbox for replies from {len(known_contacts)} contacts (last {days_back} days)")
            self.logger.debug("[OUTLOOK API] Calling namespace.GetDefaultFolder(6) to get Inbox")
            inbox = self.namespace.GetDefaultFolder(6)  # 6 = Inbox

            messages = inbox.Items
            self.logger.debug(f"[OUTLOOK API] Found {messages.Count} total messages in inbox")

            self.logger.debug("[OUTLOOK API] Sorting messages by ReceivedTime (newest first)")
            messages.Sort("[ReceivedTime]", True)  # Sort by newest first

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_back)
            self.logger.debug(f"[OUTLOOK API] Cutoff date for scanning: {cutoff_date}")

            # Normalize contact emails for comparison
            contact_emails = {email.lower().strip() for email in known_contacts}

            scanned_count = 0
            for message in messages:
                try:
                    scanned_count += 1

                    # Check received time
                    received_time = message.ReceivedTime
                    if received_time < cutoff_date:
                        # Messages are sorted, so we can stop here
                        self.logger.debug(f"[OUTLOOK API] Reached cutoff date after scanning {scanned_count} messages")
                        break

                    # Get sender email address
                    msg_sender = self._get_sender_email(message)
                    if not msg_sender:
                        continue

                    # Check if sender is in our contact list
                    if msg_sender.lower().strip() in contact_emails:
                        conversation_topic = getattr(message, 'ConversationTopic', '')
                        msg_subject = getattr(message, 'Subject', '')

                        self.logger.info(f"[OUTLOOK API] Found reply from {msg_sender}: '{msg_subject}'")
                        results.append({
                            "sender_email": msg_sender,
                            "received_time": received_time,
                            "subject": msg_subject,
                            "conversation_topic": conversation_topic
                        })

                except Exception as e:
                    # Skip messages that cause errors
                    self.logger.debug(f"[OUTLOOK API] Error reading message: {str(e)}")
                    continue

            self.logger.info(f"[OUTLOOK API] Inbox scan complete: {scanned_count} messages scanned, {len(results)} replies found")

        except Exception as e:
            self.logger.error(f"[OUTLOOK API] Error scanning inbox: {str(e)}")

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
