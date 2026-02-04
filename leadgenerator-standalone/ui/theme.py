"""Theme configuration for Lead Generator Standalone UI."""

# ttkbootstrap theme settings
THEME_NAME = "cosmo"

# Color palette
COLORS = {
    'primary': '#2780E3',
    'secondary': '#6C757D',
    'success': '#3FB618',
    'info': '#9954BB',
    'warning': '#FF7518',
    'danger': '#FF0039',
    'light': '#F8F9FA',
    'dark': '#373A3C',
    'bg': '#FFFFFF',
    'fg': '#373A3C'
}

# Status colors
STATUS_COLORS = {
    'Draft': 'secondary',
    'Active': 'success',
    'Paused': 'warning',
    'Completed': 'info',
    'Archived': 'secondary',
    'Pending': 'secondary',
    'InProgress': 'primary',
    'Responded': 'success',
    'Bounced': 'danger',
    'Unsubscribed': 'danger',
    'OptedOut': 'warning',
    'Sent': 'success',
    'Failed': 'danger',
    'Skipped': 'secondary'
}

# Font settings
FONTS = {
    'heading': ('Segoe UI', 14, 'bold'),
    'subheading': ('Segoe UI', 12, 'bold'),
    'body': ('Segoe UI', 10),
    'small': ('Segoe UI', 9),
    'mono': ('Consolas', 10)
}

# Spacing
PADDING = {
    'small': 5,
    'medium': 10,
    'large': 20
}

# Window sizes
WINDOW_SIZES = {
    'main': (1200, 800),
    'dialog': (600, 400),
    'wizard': (700, 500)
}
