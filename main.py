"""CLI interface for Email Sequence System."""
import os
import sys
import click
from datetime import datetime

from src.config import Config
from src.contact_tracker import ContactTracker
from src.sequence_engine import SequenceEngine


@click.group()
def cli():
    """Email Sequence Automation System - Manage automated email campaigns with Outlook."""
    pass


@cli.command()
def init():
    """Initialize new contacts file with sample data."""
    click.echo("Initializing email sequence system...")

    config_path = "config.yaml"

    # Create config if it doesn't exist
    if not os.path.exists(config_path):
        click.echo(click.style("Creating default config.yaml...", fg='yellow'))
        # Config file should already exist from setup
        click.echo(click.style("✓ Config file created", fg='green'))
    else:
        click.echo(click.style("✓ Config file already exists", fg='green'))

    # Load config
    try:
        config = Config(config_path)
    except Exception as e:
        click.echo(click.style(f"✗ Error loading config: {e}", fg='red'))
        sys.exit(1)

    # Create contacts file
    if not os.path.exists(config.contacts_file):
        click.echo(f"Creating contacts file: {config.contacts_file}")
        tracker = ContactTracker(config.contacts_file)

        # Add a sample contact
        tracker.add_contact({
            'title': 'Mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'company': 'Example Corp',
            'status': 'pending',
            'notes': 'Sample contact - replace with real data'
        })

        click.echo(click.style("✓ Contacts file created with sample data", fg='green'))
    else:
        click.echo(click.style("✓ Contacts file already exists", fg='green'))

    # Create templates directory
    if not os.path.exists(config.templates_folder):
        os.makedirs(config.templates_folder)
        click.echo(click.style(f"✓ Created {config.templates_folder} directory", fg='green'))
    else:
        click.echo(click.style(f"✓ Templates directory exists", fg='green'))

    # Create logs directory
    log_dir = os.path.dirname(config.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        click.echo(click.style(f"✓ Created {log_dir} directory", fg='green'))

    click.echo(click.style("\n✓ Initialization complete!", fg='green', bold=True))
    click.echo("\nNext steps:")
    click.echo("1. Edit contacts.xlsx to add your contacts")
    click.echo("2. Create email templates in the templates/ folder")
    click.echo("3. Edit config.yaml to customize settings")
    click.echo("4. Run 'python main.py send --dry-run' to test")


@cli.command()
@click.option('--dry-run', is_flag=True, help='Display emails instead of sending')
def send(dry_run):
    """Send initial emails to all pending contacts."""
    try:
        config = Config()

        # Override dry_run if flag is set
        if dry_run:
            click.echo(click.style("DRY RUN MODE - Emails will be displayed but not sent", fg='yellow'))

        engine = SequenceEngine(config)

        # Override config dry_run if flag provided
        if dry_run:
            engine.config._config['dry_run'] = True

        click.echo("Sending initial emails...")

        result = engine.start_sequence()

        # Display results
        click.echo(click.style(f"\n✓ Sent: {result['sent']}", fg='green'))
        if result['failed'] > 0:
            click.echo(click.style(f"✗ Failed: {result['failed']}", fg='red'))

        if result['errors']:
            click.echo(click.style("\nErrors:", fg='red'))
            for error in result['errors']:
                click.echo(f"  - {error}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


@cli.command()
def check():
    """Check inbox for replies and update statuses."""
    try:
        config = Config()
        engine = SequenceEngine(config)

        click.echo("Checking for replies...")

        result = engine.check_replies()

        click.echo(click.style(f"\n✓ Replies found: {result['replies_found']}", fg='green'))

        if result['contacts_updated']:
            click.echo("\nUpdated contacts:")
            for email in result['contacts_updated']:
                click.echo(f"  - {email}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Display emails instead of sending')
def followup(dry_run):
    """Send follow-up emails to non-responders."""
    try:
        config = Config()

        if dry_run:
            click.echo(click.style("DRY RUN MODE - Emails will be displayed but not sent", fg='yellow'))

        engine = SequenceEngine(config)

        if dry_run:
            engine.config._config['dry_run'] = True

        click.echo("Sending follow-up emails...")

        result = engine.send_followups()

        # Display results
        click.echo(click.style(f"\n✓ Sent: {result['sent']}", fg='green'))
        if result['completed'] > 0:
            click.echo(click.style(f"✓ Completed: {result['completed']}", fg='blue'))
        if result['failed'] > 0:
            click.echo(click.style(f"✗ Failed: {result['failed']}", fg='red'))

        if result['errors']:
            click.echo(click.style("\nErrors:", fg='red'))
            for error in result['errors']:
                click.echo(f"  - {error}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


@cli.command()
def cycle():
    """Run full cycle (check replies + send follow-ups) - for scheduler."""
    try:
        config = Config()
        engine = SequenceEngine(config)

        click.echo("Running full cycle...")

        result = engine.run_full_cycle()

        # Display results
        click.echo(click.style(f"\n✓ Replies found: {result['replies_found']}", fg='green'))
        click.echo(click.style(f"✓ Follow-ups sent: {result['followups_sent']}", fg='green'))
        if result['completed'] > 0:
            click.echo(click.style(f"✓ Completed: {result['completed']}", fg='blue'))
        if result['followups_failed'] > 0:
            click.echo(click.style(f"✗ Failed: {result['followups_failed']}", fg='red'))

        if result['errors']:
            click.echo(click.style("\nErrors:", fg='red'))
            for error in result['errors']:
                click.echo(f"  - {error}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


@cli.command()
def status():
    """Show current status report."""
    try:
        config = Config()
        engine = SequenceEngine(config)

        report = engine.get_status_report()

        click.echo(click.style("\n=== Email Sequence Status ===\n", fg='cyan', bold=True))

        click.echo(f"Total contacts: {report['total_contacts']}")
        if report['sequence_id']:
            click.echo(f"Sequence ID: {report['sequence_id']}")

        if report['last_activity']:
            click.echo(f"Last activity: {report['last_activity']}")

        click.echo(click.style("\nStatus breakdown:", fg='cyan'))
        for status, count in report['by_status'].items():
            if count > 0:
                color = 'green' if status == 'replied' else 'white'
                click.echo(f"  {status:15} {count:4}", color=color)

        reply_rate_pct = report['reply_rate'] * 100
        color = 'green' if reply_rate_pct > 20 else 'yellow' if reply_rate_pct > 10 else 'red'
        click.echo(click.style(f"\nReply rate: {reply_rate_pct:.1f}%", fg=color, bold=True))

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


@cli.command()
@click.option('--email', required=True, help='Contact email address')
@click.option('--first-name', required=True, help='First name')
@click.option('--last-name', required=True, help='Last name')
@click.option('--title', default='', help='Title (Mr, Ms, Dr, etc.)')
@click.option('--company', default='', help='Company name')
@click.option('--notes', default='', help='Notes')
def add(email, first_name, last_name, title, company, notes):
    """Add a new contact."""
    try:
        config = Config()
        tracker = ContactTracker(config.contacts_file)

        contact_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'title': title,
            'company': company,
            'notes': notes,
            'status': 'pending'
        }

        success = tracker.add_contact(contact_data)

        if success:
            click.echo(click.style(f"✓ Added contact: {email}", fg='green'))
        else:
            click.echo(click.style(f"✗ Contact already exists: {email}", fg='red'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


@cli.command()
@click.option('--email', required=True, help='Contact email address')
def optout(email):
    """Mark a contact as opted-out."""
    try:
        config = Config()
        tracker = ContactTracker(config.contacts_file)

        success = tracker.update_contact(email, {'status': 'opted_out'})

        if success:
            click.echo(click.style(f"✓ Marked {email} as opted-out", fg='green'))
        else:
            click.echo(click.style(f"✗ Contact not found: {email}", fg='red'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


@cli.command()
@click.option('--email', required=True, help='Contact email address')
def reset(email):
    """Reset a contact to pending status."""
    try:
        config = Config()
        tracker = ContactTracker(config.contacts_file)

        updates = {
            'status': 'pending',
            'sequence_id': None,
            'initial_sent_date': None,
            'last_contact_date': None,
            'followup_count': 0,
            'conversation_id': None,
            'replied_date': None
        }

        success = tracker.update_contact(email, updates)

        if success:
            click.echo(click.style(f"✓ Reset {email} to pending", fg='green'))
        else:
            click.echo(click.style(f"✗ Contact not found: {email}", fg='red'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


@cli.command()
def templates():
    """List all available templates."""
    try:
        config = Config()

        if not os.path.exists(config.templates_folder):
            click.echo(click.style(f"✗ Templates folder not found: {config.templates_folder}", fg='red'))
            sys.exit(1)

        from src.template_engine import TemplateEngine
        engine = TemplateEngine(config.templates_folder)

        available = engine.get_available_templates()

        if available:
            click.echo(click.style("\nAvailable templates:", fg='cyan'))
            for template in available:
                click.echo(f"  - {template}")
        else:
            click.echo(click.style("No templates found", fg='yellow'))
            click.echo(f"Create .html files in: {config.templates_folder}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'))
        sys.exit(1)


if __name__ == '__main__':
    cli()
