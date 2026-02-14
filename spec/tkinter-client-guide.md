# Lead Generator — Python Tkinter Desktop Client

**Version:** 1.0  
**Target:** Windows 11 — Python 3.10+  
**Backend:** Connects to .NET 8 API Server (same backend as WPF client)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Installation & Setup](#4-installation--setup)
5. [Core Modules](#5-core-modules)
6. [UI Screens](#6-ui-screens)
7. [Claude Code Implementation Prompts](#7-claude-code-implementation-prompts)
8. [Packaging & Distribution](#8-packaging--distribution)
9. [Mail Service (Python)](#9-mail-service-python)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERNAL NETWORK / VPN                       │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   PostgreSQL    │◄──►│   .NET 8 API    │ (unchanged)        │
│  │   Database      │    │   Server        │                    │
│  └─────────────────┘    └────────┬────────┘                    │
│                                  │                              │
│                                  │ REST / JSON                  │
│                                  │                              │
│    ┌─────────────────────────────┼─────────────────────────┐   │
│    │                             │                         │   │
│    ▼                             ▼                         ▼   │
│  ┌───────────────────┐ ┌───────────────────┐ ┌──────────────┐ │
│  │ WORKSTATION 1     │ │ WORKSTATION 2     │ │ HOME-MADE CRM│ │
│  │ ┌───────────────┐ │ │ ┌───────────────┐ │ │ (pulls data) │ │
│  │ │ Python Tk GUI │ │ │ │ Python Tk GUI │ │ └──────────────┘ │
│  │ │ (ttkbootstrap)│ │ │ │ (ttkbootstrap)│ │                  │
│  │ └───────────────┘ │ │ └───────────────┘ │                  │
│  │ ┌───────────────┐ │ │ ┌───────────────┐ │                  │
│  │ │ Mail Service  │ │ │ │ Mail Service  │ │                  │
│  │ │ (Python/pywin)│ │ │ │ (Python/pywin)│ │                  │
│  │ └───────────────┘ │ │ └───────────────┘ │                  │
│  │ ┌───────────────┐ │ │ ┌───────────────┐ │                  │
│  │ │   Outlook     │ │ │ │   Outlook     │ │                  │
│  │ └───────────────┘ │ │ └───────────────┘ │                  │
│  └───────────────────┘ └───────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

> **Key Point:** Only the desktop client and mail service change. The API server and database remain unchanged.

---

## 2. Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│ Component              │ Library                        │
├────────────────────────┼────────────────────────────────┤
│ Python                 │ 3.10+                          │
│ GUI Framework          │ tkinter + ttkbootstrap         │
│ Modern Theming         │ ttkbootstrap (Bootstrap look)  │
│ HTTP Client            │ requests + urllib3              │
│ CSV Parsing            │ pandas                         │
│ Charts / Reporting     │ matplotlib (embedded in Tk)    │
│ PDF Export             │ reportlab or fpdf2             │
│ Outlook Integration    │ pywin32 (win32com.client)      │
│ Background Tasks       │ threading + schedule           │
│ Configuration          │ pyyaml or python-dotenv        │
│ Logging                │ logging (built-in)             │
│ Packaging              │ PyInstaller                    │
│ Token Storage          │ keyring                        │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Project Structure

```
leadgenerator-client/
├── main.py                         # Application entry point
├── config.yaml                     # Configuration file
├── requirements.txt                # Python dependencies
│
├── core/
│   ├── __init__.py
│   ├── api_client.py               # REST API communication
│   ├── auth.py                     # JWT token management
│   ├── models.py                   # Data classes (dataclasses)
│   └── exceptions.py               # Custom exceptions
│
├── services/
│   ├── __init__.py
│   ├── campaign_service.py         # Campaign business logic
│   ├── contact_service.py          # Contact operations
│   ├── template_service.py         # Template management
│   ├── report_service.py           # Report generation
│   ├── csv_service.py              # CSV import/export
│   └── mail_service.py             # Outlook integration (pywin32)
│
├── ui/
│   ├── __init__.py
│   ├── app.py                      # Main application window
│   ├── theme.py                    # Custom theme configuration
│   ├── widgets/                    # Reusable custom widgets
│   │   ├── __init__.py
│   │   ├── data_table.py           # Sortable/filterable table
│   │   ├── status_badge.py         # Colored status indicator
│   │   ├── progress_card.py        # Campaign progress card
│   │   ├── merge_tag_picker.py     # Template merge tag selector
│   │   ├── file_attachment.py      # Attachment with mode selector
│   │   └── chart_widget.py         # Matplotlib embedded chart
│   │
│   ├── dialogs/                    # Dialog windows
│   │   ├── __init__.py
│   │   ├── confirm_dialog.py
│   │   ├── csv_import_wizard.py
│   │   └── user_form_dialog.py
│   │
│   └── views/                      # Main views
│       ├── __init__.py
│       ├── login_view.py
│       ├── dashboard_view.py
│       ├── campaign_list_view.py
│       ├── campaign_detail_view.py
│       ├── contact_list_view.py
│       ├── template_editor_view.py
│       ├── ab_test_view.py
│       ├── reports_view.py
│       ├── user_management_view.py
│       ├── mail_accounts_view.py
│       ├── suppression_view.py
│       └── settings_view.py
│
├── mail_worker/                    # Background mail service
│   ├── __init__.py
│   ├── worker.py                   # Main worker loop
│   ├── outlook_service.py          # Outlook COM Interop
│   ├── reply_detector.py           # Reply detection
│   └── unsub_detector.py           # Unsubscribe detection
│
├── assets/
│   ├── icon.ico
│   ├── logo.png
│   └── splash.png
│
├── scripts/
│   ├── build.bat                   # PyInstaller build script
│   └── install.bat                 # Installation script
│
└── tests/
    ├── test_api_client.py
    ├── test_csv_service.py
    └── test_unsub_detection.py
```

---

## 4. Installation & Setup

### 4.1 Prerequisites

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKSTATION REQUIREMENTS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • Windows 10/11                                                │
│  • Python 3.10+ (or bundled via PyInstaller)                    │
│  • Microsoft Outlook 2016+ (installed and configured)           │
│  • Network access to API server                                 │
│  • 2 GB RAM minimum                                             │
│  • 200 MB disk space                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Developer Setup

```bash
# Clone/create project
mkdir leadgenerator-client
cd leadgenerator-client

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4.3 requirements.txt

```
# GUI
ttkbootstrap>=1.10.1
Pillow>=10.0.0

# HTTP / API
requests>=2.31.0
urllib3>=2.0.0

# Data
pandas>=2.0.0

# Charts
matplotlib>=3.7.0

# PDF Export
fpdf2>=2.7.0

# Outlook COM
pywin32>=306

# Background scheduler
schedule>=1.2.0

# Configuration
pyyaml>=6.0.1

# Token storage
keyring>=24.0.0

# Packaging
pyinstaller>=6.0.0
```

### 4.4 config.yaml

```yaml
# API Server
api:
  base_url: "http://YOUR_SERVER:5000"
  timeout_seconds: 30
  retry_attempts: 3

# Session
session:
  timeout_minutes: 480
  auto_refresh_minutes: 60

# Mail Service
mail:
  scan_interval_seconds: 60
  scan_folders:
    - "Inbox"
    - "Unsubscribe"
  processed_folder: "Processed"

# Unsubscribe Keywords
unsubscribe:
  keywords_en:
    - "UNSUBSCRIBE"
    - "STOP"
    - "REMOVE"
    - "OPT OUT"
    - "OPT-OUT"
  keywords_fr:
    - "DÉSINSCRIRE"
    - "DÉSINSCRIPTION"
    - "STOP"
    - "ARRÊTER"
    - "SUPPRIMER"

# Logging
logging:
  level: "INFO"
  file: "logs/leadgenerator.log"
  max_size_mb: 10
  backup_count: 5

# UI
ui:
  theme: "cosmo"  # ttkbootstrap theme
  window_width: 1280
  window_height: 800
```

---

## 5. Core Modules

### 5.1 API Client — `core/api_client.py`

```python
"""
REST API client for communicating with the Lead Generator backend.
Handles JWT authentication, token refresh, and all CRUD operations.
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Any
import keyring

logger = logging.getLogger(__name__)

SERVICE_NAME = "LeadGenerator"


class ApiClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._username: Optional[str] = None

    # ── Authentication ───────────────────────────────────────────

    def login(self, username: str, password: str) -> dict:
        """Authenticate and store JWT token."""
        response = self._request(
            "POST", "/api/auth/login",
            json={"username": username, "password": password},
            auth_required=False
        )
        self._access_token = response["token"]
        self._token_expiry = datetime.utcnow() + timedelta(
            minutes=response.get("expiresInMinutes", 480)
        )
        self._username = username
        self.session.headers.update({
            "Authorization": f"Bearer {self._access_token}"
        })
        # Store token securely
        keyring.set_password(SERVICE_NAME, username, self._access_token)
        return response

    def logout(self):
        """Clear session and stored token."""
        if self._username:
            try:
                keyring.delete_password(SERVICE_NAME, self._username)
            except keyring.errors.PasswordDeleteError:
                pass
        self._access_token = None
        self._token_expiry = None
        self.session.headers.pop("Authorization", None)

    @property
    def is_authenticated(self) -> bool:
        return (
            self._access_token is not None
            and self._token_expiry is not None
            and datetime.utcnow() < self._token_expiry
        )

    # ── Generic HTTP Methods ─────────────────────────────────────

    def _request(self, method: str, endpoint: str, auth_required: bool = True, **kwargs) -> Any:
        """Send HTTP request with error handling and token refresh."""
        if auth_required and not self.is_authenticated:
            raise AuthenticationError("Not authenticated. Please login.")

        url = f"{self.base_url}{endpoint}"
        try:
            resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            if resp.status_code == 204:
                return None
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Session expired. Please login again.")
            elif e.response.status_code == 403:
                raise PermissionError("You don't have permission for this action.")
            raise ApiError(f"API Error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to server at {self.base_url}")

    def get(self, endpoint: str, params: dict = None) -> Any:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, json: dict = None, files: dict = None) -> Any:
        return self._request("POST", endpoint, json=json, files=files)

    def put(self, endpoint: str, json: dict = None) -> Any:
        return self._request("PUT", endpoint, json=json)

    def delete(self, endpoint: str) -> Any:
        return self._request("DELETE", endpoint)

    # ── Campaigns ────────────────────────────────────────────────

    def get_campaigns(self, status: str = None) -> list:
        params = {"status": status} if status else None
        return self.get("/api/campaigns", params=params)

    def get_campaign(self, campaign_id: str) -> dict:
        return self.get(f"/api/campaigns/{campaign_id}")

    def create_campaign(self, data: dict) -> dict:
        return self.post("/api/campaigns", json=data)

    def update_campaign(self, campaign_id: str, data: dict) -> dict:
        return self.put(f"/api/campaigns/{campaign_id}", json=data)

    def delete_campaign(self, campaign_id: str):
        return self.delete(f"/api/campaigns/{campaign_id}")

    # ── Contacts ─────────────────────────────────────────────────

    def get_contacts(self, list_id: str) -> list:
        return self.get(f"/api/contactlists/{list_id}/contacts")

    def import_contacts(self, list_id: str, contacts: list) -> dict:
        return self.post(f"/api/contactlists/{list_id}/contacts/import", json=contacts)

    def check_overlap(self, contact_ids: list) -> list:
        return self.post("/api/contacts/check-overlap", json={"contactIds": contact_ids})

    # ── Email Steps ──────────────────────────────────────────────

    def get_email_steps(self, campaign_id: str) -> list:
        return self.get(f"/api/campaigns/{campaign_id}/steps")

    def create_email_step(self, campaign_id: str, data: dict) -> dict:
        return self.post(f"/api/campaigns/{campaign_id}/steps", json=data)

    def update_email_step(self, step_id: str, data: dict) -> dict:
        return self.put(f"/api/emailsteps/{step_id}", json=data)

    # ── Attachments ──────────────────────────────────────────────

    def upload_attachment(self, step_id: str, file_path: str, delivery_mode: str, link_text: str = None) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"deliveryMode": delivery_mode, "linkText": link_text or ""}
            return self._request("POST", f"/api/emailsteps/{step_id}/attachments", files=files, data=data)

    # ── Reports ──────────────────────────────────────────────────

    def get_campaign_report(self, campaign_id: str) -> dict:
        return self.get(f"/api/reports/campaign/{campaign_id}")

    def get_download_report(self, campaign_id: str) -> list:
        return self.get(f"/api/reports/downloads/{campaign_id}")

    # ── Users (Admin) ────────────────────────────────────────────

    def get_users(self) -> list:
        return self.get("/api/users")

    def create_user(self, data: dict) -> dict:
        return self.post("/api/users", json=data)

    # ── Mail Accounts ────────────────────────────────────────────

    def get_mail_accounts(self) -> list:
        return self.get("/api/mailaccounts")

    # ── Suppression List ─────────────────────────────────────────

    def get_suppression_list(self) -> list:
        return self.get("/api/suppression")

    def add_to_suppression(self, email: str, scope: str, reason: str = "") -> dict:
        return self.post("/api/suppression", json={
            "email": email, "scope": scope, "reason": reason
        })


class AuthenticationError(Exception):
    pass

class ApiError(Exception):
    pass
```

### 5.2 Data Models — `core/models.py`

```python
"""
Data models for the Lead Generator application.
Uses dataclasses for clean serialization/deserialization.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    USER = "User"


class CampaignStatus(str, Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class ContactStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    RESPONDED = "Responded"
    COMPLETED = "Completed"
    BOUNCED = "Bounced"
    UNSUBSCRIBED = "Unsubscribed"
    OPTED_OUT = "OptedOut"
    PAUSED = "Paused"


class DeliveryMode(str, Enum):
    ATTACHMENT = "Attachment"
    LINK = "Link"


@dataclass
class User:
    user_id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            user_id=data["userId"],
            username=data["username"],
            email=data["email"],
            role=UserRole(data["role"]),
            is_active=data.get("isActive", True),
        )


@dataclass
class Contact:
    contact_id: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    company: str = ""
    title: str = ""
    position: str = ""
    phone: str = ""
    linkedin_url: str = ""
    custom1: str = ""
    custom2: str = ""
    custom3: str = ""
    custom4: str = ""
    custom5: str = ""
    custom6: str = ""
    custom7: str = ""
    custom8: str = ""
    custom9: str = ""
    custom10: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        return cls(**{k: data.get(k, "") for k in cls.__dataclass_fields__})


@dataclass
class Campaign:
    campaign_id: str = ""
    name: str = ""
    description: str = ""
    campaign_ref: str = ""
    status: CampaignStatus = CampaignStatus.DRAFT
    contact_count: int = 0
    sent_count: int = 0
    response_count: int = 0
    bounce_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Campaign":
        return cls(
            campaign_id=data.get("campaignId", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            campaign_ref=data.get("campaignRef", ""),
            status=CampaignStatus(data.get("status", "Draft")),
            contact_count=data.get("contactCount", 0),
            sent_count=data.get("sentCount", 0),
            response_count=data.get("responseCount", 0),
            bounce_count=data.get("bounceCount", 0),
        )


@dataclass
class EmailStep:
    step_id: str = ""
    step_number: int = 0
    subject_template: str = ""
    body_template: str = ""
    delay_days: int = 0
    attachments: List[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "EmailStep":
        return cls(
            step_id=data.get("stepId", ""),
            step_number=data.get("stepNumber", 0),
            subject_template=data.get("subjectTemplate", ""),
            body_template=data.get("bodyTemplate", ""),
            delay_days=data.get("delayDays", 0),
            attachments=data.get("attachments", []),
        )
```

### 5.3 CSV Import Service — `services/csv_service.py`

```python
"""
CSV import/export with field mapping support.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Standard fields that can be mapped
STANDARD_FIELDS = {
    "title": "Title",
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
    "company": "Company",
    "position": "Position",
    "phone": "Phone",
    "linkedin_url": "LinkedIn URL",
    "source": "Source",
}

# Custom fields available for mapping
CUSTOM_FIELDS = {f"custom{i}": f"Custom {i}" for i in range(1, 11)}

# All mappable fields
ALL_FIELDS = {**STANDARD_FIELDS, **CUSTOM_FIELDS}

REQUIRED_FIELDS = ["first_name", "last_name", "email", "company"]


class CsvService:

    @staticmethod
    def read_csv_preview(file_path: str, max_rows: int = 5) -> Tuple[List[str], List[List[str]], int]:
        """
        Read CSV file and return headers, preview rows, and total row count.
        Returns: (headers, preview_rows, total_count)
        """
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        df.columns = [col.strip() for col in df.columns]

        headers = df.columns.tolist()
        preview = df.head(max_rows).fillna("").values.tolist()
        total = len(df)

        return headers, preview, total

    @staticmethod
    def auto_map_fields(csv_headers: List[str]) -> Dict[str, str]:
        """
        Auto-detect field mapping based on common column name patterns.
        Returns: {csv_column: internal_field_name}
        """
        mapping = {}

        patterns = {
            "first_name": ["prénom", "prenom", "firstname", "first_name", "first name", "given name"],
            "last_name": ["nom", "lastname", "last_name", "last name", "surname", "family name"],
            "email": ["email", "e-mail", "courriel", "mail", "email address"],
            "company": ["société", "societe", "company", "entreprise", "organization", "organisation"],
            "title": ["titre", "title", "civilité", "civilite", "salutation"],
            "position": ["poste", "position", "fonction", "job title", "job_title", "role"],
            "phone": ["téléphone", "telephone", "phone", "tel", "mobile"],
            "linkedin_url": ["linkedin", "linkedin_url", "linkedin url"],
        }

        for csv_col in csv_headers:
            col_lower = csv_col.strip().lower()
            for field_name, keywords in patterns.items():
                if col_lower in keywords:
                    mapping[csv_col] = field_name
                    break

        return mapping

    @staticmethod
    def import_csv(file_path: str, field_mapping: Dict[str, str],
                   custom_labels: Dict[str, str] = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Import CSV file using provided field mapping.
        Returns: (valid_contacts, errors)
        """
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        df.columns = [col.strip() for col in df.columns]

        valid_contacts = []
        errors = []

        for idx, row in df.iterrows():
            contact = {}
            row_errors = []

            for csv_col, field_name in field_mapping.items():
                if csv_col in df.columns:
                    value = str(row[csv_col]).strip() if pd.notna(row[csv_col]) else ""
                    contact[field_name] = value

            # Validate required fields
            for req in REQUIRED_FIELDS:
                if not contact.get(req):
                    row_errors.append(f"Missing required field: {ALL_FIELDS.get(req, req)}")

            # Validate email format
            email = contact.get("email", "")
            if email and "@" not in email:
                row_errors.append(f"Invalid email: {email}")

            # Add custom labels
            if custom_labels:
                for field_key, label in custom_labels.items():
                    contact[f"{field_key}_label"] = label

            if row_errors:
                errors.append({"row": idx + 2, "data": contact, "errors": row_errors})
            else:
                valid_contacts.append(contact)

        return valid_contacts, errors

    @staticmethod
    def export_csv(contacts: List[Dict], file_path: str, fields: List[str] = None):
        """Export contacts to CSV file."""
        df = pd.DataFrame(contacts)
        if fields:
            df = df[[f for f in fields if f in df.columns]]
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        logger.info(f"Exported {len(contacts)} contacts to {file_path}")
```

---

## 6. UI Screens

### 6.1 Main Application — `ui/app.py`

```python
"""
Main application window with sidebar navigation.
Uses ttkbootstrap for modern Windows 11 look.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging
from core.api_client import ApiClient

logger = logging.getLogger(__name__)


class MainApplication(ttk.Window):
    def __init__(self, api_client: ApiClient, user: dict):
        super().__init__(
            title="Lead Generator",
            themename="cosmo",  # Modern light theme
            size=(1280, 800),
            minsize=(1024, 600),
        )
        self.api_client = api_client
        self.current_user = user
        self.current_view = None

        self._build_ui()
        self.show_view("dashboard")

    def _build_ui(self):
        # ── Top Menu Bar ──────────────────────────────────────
        self.menu_frame = ttk.Frame(self, bootstyle="dark")
        self.menu_frame.pack(fill=X, side=TOP)

        ttk.Label(
            self.menu_frame, text="  📧 Lead Generator",
            font=("Segoe UI", 14, "bold"),
            bootstyle="inverse-dark"
        ).pack(side=LEFT, padx=10, pady=8)

        # User info (right side)
        user_frame = ttk.Frame(self.menu_frame, bootstyle="dark")
        user_frame.pack(side=RIGHT, padx=10)

        ttk.Label(
            user_frame,
            text=f"👤 {self.current_user['username']} ({self.current_user['role']})",
            bootstyle="inverse-dark"
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            user_frame, text="Logout",
            bootstyle="outline-light",
            command=self._logout
        ).pack(side=LEFT, padx=5, pady=5)

        # ── Main Content Area ─────────────────────────────────
        self.main_paned = ttk.PanedWindow(self, orient=HORIZONTAL)
        self.main_paned.pack(fill=BOTH, expand=True)

        # ── Sidebar ───────────────────────────────────────────
        self.sidebar = ttk.Frame(self.main_paned, width=220)
        self.main_paned.add(self.sidebar, weight=0)

        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("📧", "Campaigns", "campaigns"),
            ("👥", "Contacts", "contacts"),
            ("📝", "Templates", "templates"),
            ("🧪", "A/B Tests", "abtests"),
            ("📈", "Reports", "reports"),
        ]

        # Admin-only items
        if self.current_user["role"] in ("Admin", "Manager"):
            nav_items.append(("🚫", "Suppression List", "suppression"))

        if self.current_user["role"] == "Admin":
            nav_items.extend([
                ("👤", "Users", "users"),
                ("📬", "Mail Accounts", "mail_accounts"),
                ("⚙️", "Settings", "settings"),
            ])

        ttk.Label(
            self.sidebar, text="NAVIGATION",
            font=("Segoe UI", 9), foreground="gray"
        ).pack(anchor=W, padx=15, pady=(15, 5))

        self.nav_buttons = {}
        for icon, label, view_name in nav_items:
            btn = ttk.Button(
                self.sidebar,
                text=f"  {icon}  {label}",
                bootstyle="link",
                command=lambda v=view_name: self.show_view(v),
                width=25,
            )
            btn.pack(fill=X, padx=5, pady=1)
            self.nav_buttons[view_name] = btn

        # ── Content Area ──────────────────────────────────────
        self.content_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.content_frame, weight=1)

    def show_view(self, view_name: str):
        """Switch to a different view."""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Highlight active nav button
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(bootstyle="info")
            else:
                btn.configure(bootstyle="link")

        # Load view
        from ui.views import (
            dashboard_view, campaign_list_view, contact_list_view,
            template_editor_view, reports_view, user_management_view,
            mail_accounts_view, suppression_view, ab_test_view,
            settings_view
        )

        view_map = {
            "dashboard": dashboard_view.DashboardView,
            "campaigns": campaign_list_view.CampaignListView,
            "contacts": contact_list_view.ContactListView,
            "templates": template_editor_view.TemplateEditorView,
            "abtests": ab_test_view.ABTestView,
            "reports": reports_view.ReportsView,
            "suppression": suppression_view.SuppressionView,
            "users": user_management_view.UserManagementView,
            "mail_accounts": mail_accounts_view.MailAccountsView,
            "settings": settings_view.SettingsView,
        }

        view_class = view_map.get(view_name)
        if view_class:
            self.current_view = view_class(self.content_frame, self.api_client)
            self.current_view.pack(fill=BOTH, expand=True)

    def _logout(self):
        self.api_client.logout()
        self.destroy()
        # Reopen login window
        from ui.views.login_view import show_login
        show_login()
```

### 6.2 Login Window — `ui/views/login_view.py`

```python
"""
Login window with standalone authentication.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from core.api_client import ApiClient, AuthenticationError
import yaml


def show_login():
    """Display login window and return authenticated API client."""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    api_client = ApiClient(
        base_url=config["api"]["base_url"],
        timeout=config["api"]["timeout_seconds"]
    )

    login_win = ttk.Window(
        title="Lead Generator - Login",
        themename="cosmo",
        size=(400, 500),
        resizable=(False, False),
    )
    login_win.place_window_center()

    # ── Logo / Header ─────────────────────────────────
    header = ttk.Frame(login_win)
    header.pack(fill=X, pady=(40, 20))

    ttk.Label(
        header, text="📧", font=("Segoe UI", 48)
    ).pack()
    ttk.Label(
        header, text="Lead Generator",
        font=("Segoe UI", 20, "bold")
    ).pack()
    ttk.Label(
        header, text="Digital Marketing Campaign Tool",
        font=("Segoe UI", 10), foreground="gray"
    ).pack()

    # ── Form ──────────────────────────────────────────
    form = ttk.Frame(login_win, padding=40)
    form.pack(fill=X)

    ttk.Label(form, text="Username").pack(anchor=W)
    username_var = ttk.StringVar()
    username_entry = ttk.Entry(form, textvariable=username_var, font=("Segoe UI", 11))
    username_entry.pack(fill=X, pady=(2, 15))
    username_entry.focus_set()

    ttk.Label(form, text="Password").pack(anchor=W)
    password_var = ttk.StringVar()
    password_entry = ttk.Entry(form, textvariable=password_var, show="●", font=("Segoe UI", 11))
    password_entry.pack(fill=X, pady=(2, 5))

    remember_var = ttk.BooleanVar(value=False)
    ttk.Checkbutton(
        form, text="Remember me",
        variable=remember_var, bootstyle="round-toggle"
    ).pack(anchor=W, pady=(5, 20))

    # ── Status ────────────────────────────────────────
    status_label = ttk.Label(form, text="", foreground="red")
    status_label.pack()

    def do_login(*args):
        username = username_var.get().strip()
        password = password_var.get().strip()

        if not username or not password:
            status_label.config(text="Please enter username and password")
            return

        status_label.config(text="Connecting...", foreground="gray")
        login_win.update()

        try:
            result = api_client.login(username, password)
            login_win.destroy()

            # Open main application
            from ui.app import MainApplication
            app = MainApplication(api_client, result["user"])
            app.mainloop()

        except AuthenticationError:
            status_label.config(text="Invalid username or password", foreground="red")
            password_var.set("")
            password_entry.focus_set()
        except ConnectionError:
            status_label.config(text="Cannot connect to server", foreground="red")
        except Exception as e:
            status_label.config(text=str(e), foreground="red")

    login_btn = ttk.Button(
        form, text="Login", bootstyle="primary",
        command=do_login, width=20
    )
    login_btn.pack(pady=(10, 0))

    # Bind Enter key
    password_entry.bind("<Return>", do_login)
    username_entry.bind("<Return>", lambda e: password_entry.focus_set())

    # ── Footer ────────────────────────────────────────
    ttk.Label(
        login_win,
        text=f"Server: {config['api']['base_url']}",
        font=("Segoe UI", 8), foreground="gray"
    ).pack(side=BOTTOM, pady=10)

    login_win.mainloop()
```

### 6.3 Dashboard — `ui/views/dashboard_view.py`

```python
"""
Dashboard with campaign overview and quick stats.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging

logger = logging.getLogger(__name__)


class DashboardView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding=20)
        self.api_client = api_client
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # ── Header ────────────────────────────────────
        ttk.Label(
            self, text="Dashboard",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor=W, pady=(0, 20))

        # ── KPI Cards ─────────────────────────────────
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=X, pady=(0, 20))

        self.kpi_cards = {}
        kpis = [
            ("active_campaigns", "Active Campaigns", "info", "📧"),
            ("total_contacts", "Total Contacts", "primary", "👥"),
            ("emails_sent", "Emails Sent (30d)", "success", "✉️"),
            ("response_rate", "Response Rate", "warning", "📈"),
        ]

        for i, (key, label, style, icon) in enumerate(kpis):
            card = self._create_kpi_card(cards_frame, icon, "—", label, style)
            card.grid(row=0, column=i, padx=8, sticky=NSEW)
            cards_frame.columnconfigure(i, weight=1)
            self.kpi_cards[key] = card

        # ── Active Campaigns Table ────────────────────
        table_label = ttk.Label(
            self, text="Active Campaigns",
            font=("Segoe UI", 14, "bold")
        )
        table_label.pack(anchor=W, pady=(10, 5))

        # Table frame
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=True)

        columns = ("name", "ref", "contacts", "sent", "responded", "progress", "status")
        self.campaign_tree = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", height=12,
            bootstyle="primary"
        )

        headers = {
            "name": ("Campaign", 200),
            "ref": ("Ref", 100),
            "contacts": ("Contacts", 80),
            "sent": ("Sent", 80),
            "responded": ("Responded", 90),
            "progress": ("Progress", 100),
            "status": ("Status", 80),
        }

        for col, (heading, width) in headers.items():
            self.campaign_tree.heading(col, text=heading)
            self.campaign_tree.column(col, width=width, anchor=CENTER if col != "name" else W)

        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.campaign_tree.yview)
        self.campaign_tree.configure(yscrollcommand=scrollbar.set)
        self.campaign_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _create_kpi_card(self, parent, icon, value, label, style):
        """Create a KPI metric card."""
        card = ttk.Labelframe(parent, text="", bootstyle=style, padding=15)

        ttk.Label(
            card, text=icon, font=("Segoe UI", 24)
        ).pack(anchor=W)

        value_label = ttk.Label(
            card, text=value,
            font=("Segoe UI", 28, "bold"), bootstyle=style
        )
        value_label.pack(anchor=W)
        card._value_label = value_label  # Store reference for updates

        ttk.Label(
            card, text=label,
            font=("Segoe UI", 10), foreground="gray"
        ).pack(anchor=W)

        return card

    def _load_data(self):
        """Load dashboard data from API."""
        try:
            # Load campaigns
            campaigns = self.api_client.get_campaigns(status="Active")

            # Update table
            for item in self.campaign_tree.get_children():
                self.campaign_tree.delete(item)

            total_contacts = 0
            total_sent = 0
            total_responded = 0

            for c in campaigns:
                contacts = c.get("contactCount", 0)
                sent = c.get("sentCount", 0)
                responded = c.get("responseCount", 0)
                progress = f"{int(sent / max(contacts, 1) * 100)}%" if contacts > 0 else "0%"

                self.campaign_tree.insert("", END, values=(
                    c["name"], c["campaignRef"], contacts,
                    sent, responded, progress, c["status"]
                ))

                total_contacts += contacts
                total_sent += sent
                total_responded += responded

            # Update KPI cards
            self.kpi_cards["active_campaigns"]._value_label.config(text=str(len(campaigns)))
            self.kpi_cards["total_contacts"]._value_label.config(text=str(total_contacts))
            self.kpi_cards["emails_sent"]._value_label.config(text=str(total_sent))

            rate = f"{int(total_responded / max(total_sent, 1) * 100)}%"
            self.kpi_cards["response_rate"]._value_label.config(text=rate)

        except Exception as e:
            logger.error(f"Failed to load dashboard: {e}")
```

### 6.4 CSV Import Wizard — `ui/dialogs/csv_import_wizard.py`

```python
"""
3-step CSV import wizard with field mapping.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
from services.csv_service import CsvService, ALL_FIELDS, REQUIRED_FIELDS
import logging

logger = logging.getLogger(__name__)


class CsvImportWizard(ttk.Toplevel):
    def __init__(self, parent, api_client, list_id: str):
        super().__init__(parent)
        self.title("Import Contacts from CSV")
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.api_client = api_client
        self.list_id = list_id
        self.csv_service = CsvService()

        # State
        self.file_path = None
        self.csv_headers = []
        self.preview_data = []
        self.total_rows = 0
        self.field_mapping = {}
        self.custom_labels = {}

        self.current_step = 1
        self._build_ui()

    def _build_ui(self):
        # ── Step Indicator ────────────────────────────
        self.step_frame = ttk.Frame(self, padding=10)
        self.step_frame.pack(fill=X)

        self.step_labels = {}
        steps = ["1. Upload File", "2. Map Fields", "3. Validate & Import"]
        for i, label in enumerate(steps):
            lbl = ttk.Label(
                self.step_frame, text=label,
                font=("Segoe UI", 10, "bold" if i == 0 else "normal"),
                foreground="black" if i == 0 else "gray"
            )
            lbl.pack(side=LEFT, padx=20)
            self.step_labels[i + 1] = lbl

        ttk.Separator(self).pack(fill=X)

        # ── Content Area ──────────────────────────────
        self.content = ttk.Frame(self, padding=20)
        self.content.pack(fill=BOTH, expand=True)

        # ── Button Bar ────────────────────────────────
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=X, side=BOTTOM)

        self.back_btn = ttk.Button(btn_frame, text="← Back", command=self._prev_step)
        self.back_btn.pack(side=LEFT, padx=5)
        self.back_btn.config(state=DISABLED)

        self.next_btn = ttk.Button(btn_frame, text="Next →", bootstyle="primary",
                                    command=self._next_step)
        self.next_btn.pack(side=RIGHT, padx=5)

        self._show_step_1()

    def _show_step_1(self):
        """Step 1: File selection and preview."""
        for w in self.content.winfo_children():
            w.destroy()

        ttk.Label(
            self.content, text="Select CSV File",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor=W, pady=(0, 10))

        file_frame = ttk.Frame(self.content)
        file_frame.pack(fill=X, pady=5)

        self.file_var = ttk.StringVar(value=self.file_path or "No file selected")
        ttk.Entry(file_frame, textvariable=self.file_var, state="readonly").pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        ttk.Button(file_frame, text="Browse...", command=self._browse_file).pack(side=RIGHT)

        # Preview area
        self.preview_frame = ttk.Labelframe(self.content, text="Preview", padding=10)
        self.preview_frame.pack(fill=BOTH, expand=True, pady=10)

        if self.file_path:
            self._show_preview()

    def _browse_file(self):
        """Open file dialog and load preview."""
        path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if path:
            self.file_path = path
            self.file_var.set(path)
            try:
                self.csv_headers, self.preview_data, self.total_rows = \
                    self.csv_service.read_csv_preview(path)
                self.field_mapping = self.csv_service.auto_map_fields(self.csv_headers)
                self._show_preview()
            except Exception as e:
                Messagebox.show_error(f"Error reading CSV: {e}", parent=self)

    def _show_preview(self):
        """Display CSV data preview in table."""
        for w in self.preview_frame.winfo_children():
            w.destroy()

        ttk.Label(
            self.preview_frame,
            text=f"Found {self.total_rows} rows, {len(self.csv_headers)} columns"
        ).pack(anchor=W, pady=(0, 5))

        tree = ttk.Treeview(
            self.preview_frame,
            columns=self.csv_headers,
            show="headings", height=5
        )
        for col in self.csv_headers:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in self.preview_data:
            tree.insert("", END, values=row)

        tree.pack(fill=BOTH, expand=True)

    def _show_step_2(self):
        """Step 2: Field mapping."""
        for w in self.content.winfo_children():
            w.destroy()

        ttk.Label(
            self.content, text="Map CSV Columns to Contact Fields",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor=W, pady=(0, 10))

        # Scrollable mapping area
        canvas = ttk.Canvas(self.content)
        scrollbar = ttk.Scrollbar(self.content, orient=VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Headers
        ttk.Label(scroll_frame, text="CSV Column", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=10, sticky=W)
        ttk.Label(scroll_frame, text="→", font=("Segoe UI", 10)).grid(row=0, column=1, padx=5)
        ttk.Label(scroll_frame, text="Contact Field", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=10, sticky=W)
        ttk.Label(scroll_frame, text="Merge Tag", font=("Segoe UI", 10, "bold")).grid(row=0, column=3, padx=10, sticky=W)

        # Field options
        field_options = ["— Do not import —"] + [f"{v} ({k})" for k, v in ALL_FIELDS.items()]

        self.mapping_vars = {}
        for i, csv_col in enumerate(self.csv_headers):
            ttk.Label(scroll_frame, text=csv_col).grid(row=i+1, column=0, padx=10, pady=3, sticky=W)
            ttk.Label(scroll_frame, text="→").grid(row=i+1, column=1, padx=5)

            var = ttk.StringVar()
            combo = ttk.Combobox(scroll_frame, textvariable=var, values=field_options, width=25, state="readonly")
            combo.grid(row=i+1, column=2, padx=10, pady=3)

            # Pre-select auto-mapped fields
            if csv_col in self.field_mapping:
                mapped = self.field_mapping[csv_col]
                display = f"{ALL_FIELDS[mapped]} ({mapped})"
                var.set(display)
            else:
                var.set("— Do not import —")

            # Show merge tag
            tag_label = ttk.Label(scroll_frame, text="", foreground="blue")
            tag_label.grid(row=i+1, column=3, padx=10, sticky=W)

            self.mapping_vars[csv_col] = (var, tag_label)

            # Update merge tag on selection
            var.trace_add("write", lambda *a, v=var, l=tag_label: self._update_tag(v, l))
            self._update_tag(var, tag_label)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _update_tag(self, var, label):
        """Update merge tag display based on selection."""
        selection = var.get()
        if selection == "— Do not import —":
            label.config(text="")
        else:
            field_key = selection.split("(")[-1].rstrip(")")
            label.config(text=f"{{{{{field_key.strip()}}}}}")

    def _show_step_3(self):
        """Step 3: Validation and import."""
        for w in self.content.winfo_children():
            w.destroy()

        # Build final mapping
        self.field_mapping = {}
        for csv_col, (var, _) in self.mapping_vars.items():
            selection = var.get()
            if selection != "— Do not import —":
                field_key = selection.split("(")[-1].rstrip(")").strip()
                self.field_mapping[csv_col] = field_key

        # Run validation
        valid, errors = self.csv_service.import_csv(self.file_path, self.field_mapping)

        ttk.Label(
            self.content, text="Validation Results",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor=W, pady=(0, 10))

        results = ttk.Frame(self.content)
        results.pack(fill=X, pady=10)

        ttk.Label(results, text=f"✅ {len(valid)} contacts ready to import",
                   foreground="green", font=("Segoe UI", 11)).pack(anchor=W)

        if errors:
            ttk.Label(results, text=f"⚠️ {len(errors)} contacts with errors (will be skipped)",
                       foreground="orange", font=("Segoe UI", 11)).pack(anchor=W)

        self.next_btn.config(text=f"Import {len(valid)} Contacts", bootstyle="success")
        self._valid_contacts = valid

    def _next_step(self):
        if self.current_step == 1:
            if not self.file_path:
                Messagebox.show_warning("Please select a CSV file", parent=self)
                return
            self.current_step = 2
            self._show_step_2()
        elif self.current_step == 2:
            self.current_step = 3
            self._show_step_3()
        elif self.current_step == 3:
            self._do_import()
            return

        self.back_btn.config(state=NORMAL)
        self._update_step_indicator()

    def _prev_step(self):
        if self.current_step > 1:
            self.current_step -= 1
            if self.current_step == 1:
                self._show_step_1()
                self.back_btn.config(state=DISABLED)
            elif self.current_step == 2:
                self._show_step_2()
            self.next_btn.config(text="Next →", bootstyle="primary")
            self._update_step_indicator()

    def _update_step_indicator(self):
        for step, lbl in self.step_labels.items():
            if step == self.current_step:
                lbl.config(font=("Segoe UI", 10, "bold"), foreground="black")
            elif step < self.current_step:
                lbl.config(font=("Segoe UI", 10), foreground="green")
            else:
                lbl.config(font=("Segoe UI", 10), foreground="gray")

    def _do_import(self):
        """Send contacts to API."""
        try:
            result = self.api_client.import_contacts(self.list_id, self._valid_contacts)
            Messagebox.show_info(
                f"Successfully imported {result.get('imported', len(self._valid_contacts))} contacts!",
                parent=self
            )
            self.destroy()
        except Exception as e:
            Messagebox.show_error(f"Import failed: {e}", parent=self)
```

### 6.5 Template Editor with Merge Tags — `ui/views/template_editor_view.py`

```python
"""
Email template editor with merge tag insertion and live preview.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolledtext import ScrolledText
import re
import logging

logger = logging.getLogger(__name__)

MERGE_TAGS = {
    "Contact Fields": [
        ("{{Title}}", "Title"),
        ("{{FirstName}}", "First Name"),
        ("{{LastName}}", "Last Name"),
        ("{{FullName}}", "Full Name"),
        ("{{Email}}", "Email"),
        ("{{Company}}", "Company"),
        ("{{Position}}", "Position"),
        ("{{Phone}}", "Phone"),
    ],
    "Custom Fields": [
        (f"{{{{Custom{i}}}}}", f"Custom {i}") for i in range(1, 11)
    ],
    "Sender Info": [
        ("{{SenderName}}", "Sender Name"),
        ("{{SenderEmail}}", "Sender Email"),
        ("{{SenderCompany}}", "Sender Company"),
    ],
    "Campaign": [
        ("{{CampaignRef}}", "Campaign Reference"),
        ("{{UnsubscribeText}}", "Unsubscribe Text"),
    ],
}

# Sample contact for preview
SAMPLE_CONTACT = {
    "Title": "Mr",
    "FirstName": "Jean",
    "LastName": "Dupont",
    "FullName": "Jean Dupont",
    "Email": "jd@acme.fr",
    "Company": "Acme Corp",
    "Position": "CTO",
    "Phone": "+33 6 12 34 56 78",
    "Custom1": "Manufacturing",
    "Custom2": "Supply chain delays",
    "Custom3": "50K€",
    "Custom4": "", "Custom5": "", "Custom6": "",
    "Custom7": "", "Custom8": "", "Custom9": "", "Custom10": "",
    "SenderName": "Pierre Martin",
    "SenderEmail": "pm@company.com",
    "SenderCompany": "Your Company",
    "CampaignRef": "ISIT-250042",
    "UnsubscribeText": "To unsubscribe, reply with STOP",
}


class TemplateEditorView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding=20)
        self.api_client = api_client
        self._build_ui()

    def _build_ui(self):
        ttk.Label(
            self, text="Template Editor",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor=W, pady=(0, 15))

        # ── Horizontal split: Editor | Preview ────────
        paned = ttk.PanedWindow(self, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=True)

        # LEFT: Editor
        editor_frame = ttk.Frame(paned)
        paned.add(editor_frame, weight=1)

        # Subject
        ttk.Label(editor_frame, text="Subject Line:", font=("Segoe UI", 10, "bold")).pack(anchor=W)
        self.subject_var = ttk.StringVar()
        subject_frame = ttk.Frame(editor_frame)
        subject_frame.pack(fill=X, pady=(2, 10))
        self.subject_entry = ttk.Entry(subject_frame, textvariable=self.subject_var, font=("Consolas", 11))
        self.subject_entry.pack(side=LEFT, fill=X, expand=True)
        self.subject_var.trace_add("write", lambda *a: self._update_preview())

        # Body
        ttk.Label(editor_frame, text="Email Body:", font=("Segoe UI", 10, "bold")).pack(anchor=W)
        self.body_text = ScrolledText(editor_frame, font=("Consolas", 11), height=15, wrap="word")
        self.body_text.pack(fill=BOTH, expand=True, pady=(2, 10))
        self.body_text.bind("<KeyRelease>", lambda e: self._update_preview())

        # Merge Tag Picker
        tag_frame = ttk.Labelframe(editor_frame, text="Insert Merge Tag", padding=5)
        tag_frame.pack(fill=X, pady=(5, 0))

        for category, tags in MERGE_TAGS.items():
            cat_frame = ttk.Frame(tag_frame)
            cat_frame.pack(fill=X, pady=2)
            ttk.Label(cat_frame, text=f"{category}:", font=("Segoe UI", 8, "bold"), foreground="gray").pack(side=LEFT, padx=(0, 5))
            for tag, display in tags[:6]:  # Show first 6 per category
                btn = ttk.Button(
                    cat_frame, text=display, bootstyle="outline-info",
                    command=lambda t=tag: self._insert_tag(t)
                )
                btn.pack(side=LEFT, padx=1)

        # RIGHT: Preview
        preview_frame = ttk.Labelframe(paned, text="Live Preview", padding=10)
        paned.add(preview_frame, weight=1)

        self.preview_subject = ttk.Label(
            preview_frame, text="Subject: ...",
            font=("Segoe UI", 11, "bold"), wraplength=400
        )
        self.preview_subject.pack(anchor=W, pady=(0, 10))

        ttk.Separator(preview_frame).pack(fill=X, pady=5)

        self.preview_body = ttk.Label(
            preview_frame, text="...",
            font=("Segoe UI", 10), wraplength=400, justify=LEFT
        )
        self.preview_body.pack(anchor=NW, fill=BOTH, expand=True)

    def _insert_tag(self, tag: str):
        """Insert merge tag at cursor position."""
        try:
            self.body_text.insert("insert", tag)
        except Exception:
            self.body_text.insert(END, tag)
        self._update_preview()

    def _update_preview(self):
        """Render template with sample contact data."""
        subject = self.subject_var.get()
        body = self.body_text.get("1.0", END)

        for tag, value in SAMPLE_CONTACT.items():
            placeholder = "{{" + tag + "}}"
            subject = subject.replace(placeholder, value or f"[{tag}]")
            body = body.replace(placeholder, value or f"[{tag}]")

        self.preview_subject.config(text=f"Subject: {subject}")
        self.preview_body.config(text=body)