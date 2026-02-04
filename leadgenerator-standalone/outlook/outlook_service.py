"""Outlook COM Interop service for Lead Generator Standalone."""

import logging
import sys
from datetime import datetime
from typing import List, Optional, Any
from dataclasses import dataclass

from core.exceptions import OutlookError
from core.models import OutlookEmail

logger = logging.getLogger(__name__)

# Only import pywin32 on Windows
if sys.platform == 'win32':
    try:
        import pythoncom
        import win32com.client
        OUTLOOK_AVAILABLE = True
    except ImportError:
        OUTLOOK_AVAILABLE = False
        logger.warning("pywin32 not installed - Outlook integration disabled")
else:
    OUTLOOK_AVAILABLE = False
    logger.info("Non-Windows platform - Outlook integration disabled")


class OutlookService:
    """Service for interacting with Outlook via COM Interop."""

    def __init__(self):
        self._outlook = None
        self._namespace = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize COM and connect to Outlook."""
        if not OUTLOOK_AVAILABLE:
            logger.warning("Outlook COM not available")
            return False

        try:
            pythoncom.CoInitialize()
            self._outlook = win32com.client.Dispatch("Outlook.Application")
            self._namespace = self._outlook.GetNamespace("MAPI")
            self._initialized = True
            logger.info("Outlook COM initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Outlook COM: {e}")
            self._initialized = False
            return False

    def is_outlook_running(self) -> bool:
        """Check if Outlook is running and accessible."""
        if not OUTLOOK_AVAILABLE:
            return False

        try:
            if not self._initialized:
                return self.initialize()

            # Try to access Outlook to verify it's running
            _ = self._namespace.CurrentUser
            return True
        except Exception as e:
            logger.debug(f"Outlook not available: {e}")
            return False

    def get_default_account(self) -> Optional[str]:
        """Get the default email account."""
        if not self._ensure_initialized():
            return None

        try:
            accounts = self._namespace.Accounts
            if accounts.Count > 0:
                return accounts.Item(1).SmtpAddress
            return None
        except Exception as e:
            logger.error(f"Failed to get default account: {e}")
            return None

    def get_accounts(self) -> List[str]:
        """Get all email accounts."""
        if not self._ensure_initialized():
            return []

        try:
            accounts = []
            for i in range(1, self._namespace.Accounts.Count + 1):
                account = self._namespace.Accounts.Item(i)
                accounts.append(account.SmtpAddress)
            return accounts
        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            return []

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html_body: bool = False,
        send_at: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Send an email via Outlook.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            attachments: List of file paths to attach
            cc: CC recipients
            bcc: BCC recipients
            html_body: If True, body is treated as HTML
            send_at: Optional scheduled send time (not supported in all Outlook versions)

        Returns:
            Outlook EntryID of the sent message, or None on failure
        """
        if not self._ensure_initialized():
            raise OutlookError("Outlook is not available")

        try:
            mail = self._outlook.CreateItem(0)  # 0 = olMailItem
            mail.To = to
            mail.Subject = subject

            if html_body:
                mail.HTMLBody = body
            else:
                mail.Body = body

            if cc:
                mail.CC = cc
            if bcc:
                mail.BCC = bcc

            if attachments:
                for attachment_path in attachments:
                    mail.Attachments.Add(attachment_path)

            # Send the email
            mail.Send()

            # Get EntryID after sending (may be in Sent Items)
            # Note: EntryID changes after send, so this might not be reliable
            entry_id = getattr(mail, 'EntryID', None)

            logger.info(f"Email sent to {to}: {subject[:50]}...")
            return entry_id

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            raise OutlookError(f"Failed to send email: {e}")

    def get_unread_emails(
        self,
        folder_name: str = 'Inbox',
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[OutlookEmail]:
        """
        Get unread emails from a folder.

        Args:
            folder_name: Name of the folder to scan
            since: Only get emails received after this time
            limit: Maximum number of emails to return
        """
        if not self._ensure_initialized():
            return []

        try:
            # Get folder
            folder = self._get_folder(folder_name)
            if not folder:
                logger.warning(f"Folder '{folder_name}' not found")
                return []

            items = folder.Items
            items.Sort("[ReceivedTime]", True)  # Sort descending

            emails = []
            for i in range(1, min(items.Count + 1, limit + 1)):
                try:
                    mail = items.Item(i)

                    # Check if it's a mail item
                    if mail.Class != 43:  # 43 = olMail
                        continue

                    # Check if unread
                    if mail.UnRead:
                        received_time = mail.ReceivedTime

                        # Check since filter
                        if since and received_time < since:
                            break  # Sorted descending, so we can stop

                        emails.append(OutlookEmail(
                            entry_id=mail.EntryID,
                            sender_email=self._get_sender_email(mail),
                            sender_name=mail.SenderName,
                            subject=mail.Subject,
                            body=mail.Body,
                            received_at=received_time.isoformat() if received_time else '',
                            is_read=not mail.UnRead
                        ))
                except Exception as e:
                    logger.warning(f"Error reading mail item: {e}")
                    continue

            return emails

        except Exception as e:
            logger.error(f"Failed to get unread emails: {e}")
            return []

    def mark_as_read(self, entry_id: str) -> bool:
        """Mark an email as read."""
        if not self._ensure_initialized():
            return False

        try:
            mail = self._namespace.GetItemFromID(entry_id)
            mail.UnRead = False
            mail.Save()
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False

    def move_to_folder(self, entry_id: str, folder_name: str) -> bool:
        """Move an email to a different folder."""
        if not self._ensure_initialized():
            return False

        try:
            mail = self._namespace.GetItemFromID(entry_id)
            target_folder = self._get_folder(folder_name)

            if target_folder:
                mail.Move(target_folder)
                return True
            else:
                logger.warning(f"Target folder '{folder_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Failed to move email to {folder_name}: {e}")
            return False

    def _ensure_initialized(self) -> bool:
        """Ensure Outlook is initialized."""
        if not self._initialized:
            return self.initialize()
        return True

    def _get_folder(self, folder_name: str) -> Optional[Any]:
        """Get a folder by name."""
        try:
            inbox = self._namespace.GetDefaultFolder(6)  # 6 = olFolderInbox

            if folder_name.lower() == 'inbox':
                return inbox

            # Try to find folder in inbox subfolders
            for i in range(1, inbox.Folders.Count + 1):
                folder = inbox.Folders.Item(i)
                if folder.Name.lower() == folder_name.lower():
                    return folder

            # Try to find in root folders
            for i in range(1, self._namespace.Folders.Count + 1):
                try:
                    root_folder = self._namespace.Folders.Item(i)
                    for j in range(1, root_folder.Folders.Count + 1):
                        sub_folder = root_folder.Folders.Item(j)
                        if sub_folder.Name.lower() == folder_name.lower():
                            return sub_folder
                except Exception:
                    continue

            return None
        except Exception as e:
            logger.error(f"Failed to get folder {folder_name}: {e}")
            return None

    def _get_sender_email(self, mail) -> str:
        """Extract sender email address from mail item."""
        try:
            # Try different properties
            if hasattr(mail, 'SenderEmailAddress') and mail.SenderEmailAddress:
                sender = mail.SenderEmailAddress
                # Exchange addresses start with /O=
                if sender.startswith('/O='):
                    # Try to get SMTP address
                    try:
                        sender_obj = mail.Sender
                        if sender_obj:
                            smtp = sender_obj.GetExchangeUser()
                            if smtp:
                                return smtp.PrimarySmtpAddress
                    except Exception:
                        pass
                return sender

            # Fallback to sender name as email
            return mail.SenderName
        except Exception:
            return ''

    def cleanup(self) -> None:
        """Cleanup COM resources."""
        if OUTLOOK_AVAILABLE and self._initialized:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
            self._initialized = False
