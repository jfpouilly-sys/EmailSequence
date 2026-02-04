"""Outlook integration module for Lead Generator Standalone."""

from .outlook_service import OutlookService
from .reply_detector import ReplyDetector
from .unsub_detector import UnsubscribeDetector

__all__ = [
    'OutlookService',
    'ReplyDetector',
    'UnsubscribeDetector',
]
