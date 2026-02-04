#!/usr/bin/env python3
"""
Lead Generator - System Diagnostic Script
Checks all backend components and provides installation help.

Usage:
    python diagnostic.py [--api-url URL] [--json]
"""
import sys
import json
import socket
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    INFO = "INFO"


@dataclass
class CheckResult:
    name: str
    status: Status
    message: str
    fix: Optional[str] = None
    details: Optional[str] = None


@dataclass
class DiagnosticReport:
    timestamp: str
    hostname: str
    checks: List[CheckResult]
    passed: int = 0
    warnings: int = 0
    failed: int = 0

    def add_check(self, result: CheckResult):
        self.checks.append(result)
        if result.status == Status.PASS:
            self.passed += 1
        elif result.status == Status.WARN or result.status == Status.INFO:
            self.warnings += 1
        elif result.status == Status.FAIL:
            self.failed += 1


class SystemDiagnostic:
    """System diagnostic checker for Lead Generator."""

    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url.rstrip('/')
        self.report = DiagnosticReport(
            timestamp=datetime.now().isoformat(),
            hostname=socket.gethostname(),
            checks=[]
        )

    def check_api_health(self) -> CheckResult:
        """Check if API is running and healthy."""
        if not REQUESTS_AVAILABLE:
            return CheckResult(
                name="API Health",
                status=Status.WARN,
                message="Cannot check - requests library not installed",
                fix="pip install requests"
            )

        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return CheckResult(
                    name="API Health",
                    status=Status.PASS,
                    message="API is running and healthy",
                    details=f"Status: {data.get('status', 'unknown')}"
                )
            else:
                return CheckResult(
                    name="API Health",
                    status=Status.FAIL,
                    message=f"API returned HTTP {response.status_code}",
                    fix="Check API logs at logs/api/api-*.log"
                )
        except requests.exceptions.ConnectionError:
            return CheckResult(
                name="API Health",
                status=Status.FAIL,
                message="API is not responding - server may not be running",
                fix="Start the API with: dotnet run --project src/LeadGenerator.Api"
            )
        except requests.exceptions.Timeout:
            return CheckResult(
                name="API Health",
                status=Status.FAIL,
                message="API request timed out",
                fix="Check if API is overloaded or network issues"
            )
        except Exception as e:
            return CheckResult(
                name="API Health",
                status=Status.FAIL,
                message=f"Error checking API: {str(e)}"
            )

    def check_api_version(self) -> CheckResult:
        """Check API version endpoint."""
        if not REQUESTS_AVAILABLE:
            return CheckResult(
                name="API Version",
                status=Status.WARN,
                message="Cannot check - requests library not installed"
            )

        try:
            response = requests.get(f"{self.api_url}/api/version", timeout=5)
            if response.status_code == 200:
                data = response.json()
                version = data.get('version', 'unknown')
                return CheckResult(
                    name="API Version",
                    status=Status.PASS,
                    message=f"API version: {version}",
                    details=json.dumps(data, indent=2)
                )
            else:
                return CheckResult(
                    name="API Version",
                    status=Status.WARN,
                    message=f"Version endpoint returned HTTP {response.status_code}"
                )
        except Exception as e:
            return CheckResult(
                name="API Version",
                status=Status.WARN,
                message=f"Could not retrieve version: {str(e)}"
            )

    def check_database_connection(self) -> CheckResult:
        """Check database connection via API."""
        if not REQUESTS_AVAILABLE:
            return CheckResult(
                name="Database Connection",
                status=Status.WARN,
                message="Cannot check - requests library not installed"
            )

        try:
            # Try auth endpoint - 401 means DB is working but not authenticated
            response = requests.get(f"{self.api_url}/api/auth/me", timeout=5)
            if response.status_code in [200, 401]:
                return CheckResult(
                    name="Database Connection",
                    status=Status.PASS,
                    message="Database connection working"
                )
            elif response.status_code == 500:
                return CheckResult(
                    name="Database Connection",
                    status=Status.FAIL,
                    message="Database connection error (HTTP 500)",
                    fix="Check PostgreSQL is running and connection string is correct"
                )
            else:
                return CheckResult(
                    name="Database Connection",
                    status=Status.WARN,
                    message=f"Unexpected response: HTTP {response.status_code}"
                )
        except requests.exceptions.ConnectionError:
            return CheckResult(
                name="Database Connection",
                status=Status.FAIL,
                message="Cannot verify - API not responding",
                fix="Start the API first"
            )
        except Exception as e:
            return CheckResult(
                name="Database Connection",
                status=Status.FAIL,
                message=f"Error: {str(e)}"
            )

    def check_port(self, port: int, service_name: str) -> CheckResult:
        """Check if a port is listening."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                return CheckResult(
                    name=f"Port {port} ({service_name})",
                    status=Status.PASS,
                    message=f"Port {port} is listening"
                )
            else:
                return CheckResult(
                    name=f"Port {port} ({service_name})",
                    status=Status.FAIL,
                    message=f"Port {port} is not listening",
                    fix=f"Start the {service_name} service"
                )
        except Exception as e:
            return CheckResult(
                name=f"Port {port} ({service_name})",
                status=Status.FAIL,
                message=f"Error checking port: {str(e)}"
            )
        finally:
            sock.close()

    def check_directory(self, path: str, name: str, required: bool = False) -> CheckResult:
        """Check if a directory exists."""
        p = Path(path)
        if p.exists():
            return CheckResult(
                name=f"Directory: {name}",
                status=Status.PASS,
                message=f"Directory exists: {path}"
            )
        else:
            status = Status.FAIL if required else Status.INFO
            return CheckResult(
                name=f"Directory: {name}",
                status=status,
                message=f"Directory not found: {path}",
                fix=f"mkdir -p {path}" if required else "Will be created on first run"
            )

    def check_windows_service(self, service_name: str) -> CheckResult:
        """Check Windows service status."""
        if sys.platform != 'win32':
            return CheckResult(
                name=f"Service: {service_name}",
                status=Status.INFO,
                message="Windows service check skipped (not on Windows)"
            )

        try:
            result = subprocess.run(
                ['sc', 'query', service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                if 'RUNNING' in result.stdout:
                    return CheckResult(
                        name=f"Service: {service_name}",
                        status=Status.PASS,
                        message=f"Service '{service_name}' is running"
                    )
                else:
                    return CheckResult(
                        name=f"Service: {service_name}",
                        status=Status.WARN,
                        message=f"Service '{service_name}' exists but is not running",
                        fix=f"net start \"{service_name}\""
                    )
            else:
                return CheckResult(
                    name=f"Service: {service_name}",
                    status=Status.INFO,
                    message=f"Service '{service_name}' not installed"
                )
        except Exception as e:
            return CheckResult(
                name=f"Service: {service_name}",
                status=Status.WARN,
                message=f"Could not check service: {str(e)}"
            )

    def check_python_dependencies(self) -> CheckResult:
        """Check required Python packages."""
        required = ['ttkbootstrap', 'requests', 'pandas', 'pyyaml']
        missing = []

        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        if not missing:
            return CheckResult(
                name="Python Dependencies",
                status=Status.PASS,
                message="All required packages installed"
            )
        else:
            return CheckResult(
                name="Python Dependencies",
                status=Status.WARN,
                message=f"Missing packages: {', '.join(missing)}",
                fix=f"pip install {' '.join(missing)}"
            )

    def run_all_checks(self) -> DiagnosticReport:
        """Run all diagnostic checks."""
        # API checks
        self.report.add_check(self.check_api_health())
        self.report.add_check(self.check_api_version())
        self.report.add_check(self.check_database_connection())

        # Port checks
        self.report.add_check(self.check_port(5000, "API"))
        self.report.add_check(self.check_port(5432, "PostgreSQL"))

        # Service checks (Windows)
        self.report.add_check(self.check_windows_service("Lead Generator Mail Service"))

        # Directory checks
        self.report.add_check(self.check_directory("logs/api", "API Logs"))
        self.report.add_check(self.check_directory("logs/mailservice", "Mail Service Logs"))
        self.report.add_check(self.check_directory("client/logs/gui", "GUI Logs"))

        if sys.platform == 'win32':
            self.report.add_check(self.check_directory(
                "C:/LeadGenerator/Files", "File Storage", required=True
            ))

        # Python dependencies
        self.report.add_check(self.check_python_dependencies())

        return self.report

    def print_report(self, json_output: bool = False):
        """Print the diagnostic report."""
        if json_output:
            output = {
                "timestamp": self.report.timestamp,
                "hostname": self.report.hostname,
                "summary": {
                    "passed": self.report.passed,
                    "warnings": self.report.warnings,
                    "failed": self.report.failed
                },
                "checks": [
                    {
                        "name": c.name,
                        "status": c.status.value,
                        "message": c.message,
                        "fix": c.fix,
                        "details": c.details
                    }
                    for c in self.report.checks
                ]
            }
            print(json.dumps(output, indent=2))
            return

        # Console output
        print()
        print("=" * 60)
        print("   LEAD GENERATOR - SYSTEM DIAGNOSTIC")
        print(f"   {self.report.timestamp}")
        print(f"   Host: {self.report.hostname}")
        print("=" * 60)
        print()

        status_colors = {
            Status.PASS: '\033[92m',  # Green
            Status.FAIL: '\033[91m',  # Red
            Status.WARN: '\033[93m',  # Yellow
            Status.INFO: '\033[94m',  # Blue
        }
        reset = '\033[0m'

        for i, check in enumerate(self.report.checks, 1):
            color = status_colors.get(check.status, '')
            status_str = f"[{check.status.value}]"
            print(f"[{i:2d}] {check.name}")
            print(f"     {color}{status_str}{reset} {check.message}")
            if check.fix:
                print(f"     FIX: {check.fix}")
            if check.details:
                for line in check.details.split('\n'):
                    print(f"          {line}")
            print()

        # Summary
        print("=" * 60)
        print("   DIAGNOSTIC SUMMARY")
        print("=" * 60)
        print()
        print(f"   Passed:   {self.report.passed}")
        print(f"   Warnings: {self.report.warnings}")
        print(f"   Failed:   {self.report.failed}")
        print()

        if self.report.failed == 0:
            if self.report.warnings == 0:
                print("   STATUS: ALL SYSTEMS OPERATIONAL")
            else:
                print("   STATUS: SYSTEM OPERATIONAL WITH WARNINGS")
        else:
            print("   STATUS: SYSTEM HAS ISSUES - Please fix failed items")

        print()
        print("=" * 60)
        print("   QUICK START")
        print("=" * 60)
        print()
        print("   Start API:")
        print("     dotnet run --project src/LeadGenerator.Api")
        print()
        print("   Start Mail Service:")
        print("     dotnet run --project src/LeadGenerator.MailService")
        print()
        print("   Start GUI:")
        print("     cd client && python main.py")
        print()
        print("   Default Login:")
        print("     Username: admin")
        print("     Password: Admin123!")
        print()
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Lead Generator System Diagnostic")
    parser.add_argument('--api-url', default='http://localhost:5000',
                        help='API base URL (default: http://localhost:5000)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    args = parser.parse_args()

    diagnostic = SystemDiagnostic(api_url=args.api_url)
    diagnostic.run_all_checks()
    diagnostic.print_report(json_output=args.json)

    # Exit with error code if there are failures
    sys.exit(diagnostic.report.failed)


if __name__ == "__main__":
    main()
