"""Demo of Enterprise Theme
Clean, light, modern enterprise-grade UI
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_schedule_agent.ui.enterprise_theme import EnterpriseTheme


def create_demo():
    """Create a demo window showing the Enterprise theme"""

    root = tk.Tk()
    root.title("Enterprise Theme Demo")
    root.geometry("900x700")

    # Apply Enterprise theme
    style = ttk.Style()
    EnterpriseTheme.configure_styles(style, root)

    # Main container - light gray background
    main = tk.Frame(root, bg=EnterpriseTheme.BACKGROUND['app'])
    main.pack(fill='both', expand=True, padx=24, pady=24)

    # ========================================================================
    # Header
    # ========================================================================

    header = tk.Frame(main, bg=EnterpriseTheme.BACKGROUND['app'])
    header.pack(fill='x', pady=(0, 24))

    title = tk.Label(
        header,
        text="Schedule Manager",
        bg=EnterpriseTheme.BACKGROUND['app'],
        fg=EnterpriseTheme.TEXT['primary'],
        font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['h1'], 'bold')
    )
    title.pack(anchor='w')

    subtitle = tk.Label(
        header,
        text="Manage your schedule with a clean, professional interface",
        bg=EnterpriseTheme.BACKGROUND['app'],
        fg=EnterpriseTheme.TEXT['secondary'],
        font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['body'], 'normal')
    )
    subtitle.pack(anchor='w', pady=(4, 0))

    # ========================================================================
    # Card 1: Event Form
    # ========================================================================

    card1 = EnterpriseTheme.create_card_frame(main)
    card1.pack(fill='x', pady=(0, 16))

    # Card header
    card_title = tk.Label(
        card1.content,
        text="Create New Event",
        bg=EnterpriseTheme.BACKGROUND['card'],
        fg=EnterpriseTheme.TEXT['primary'],
        font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['h2'], 'bold')
    )
    card_title.pack(anchor='w', pady=(0, 16))

    # Input fields
    title_frame, title_label, title_entry = EnterpriseTheme.create_input_frame(
        card1.content,
        "Event Title"
    )
    title_frame.pack(fill='x', pady=(0, 12))

    desc_frame, desc_label, desc_entry = EnterpriseTheme.create_input_frame(
        card1.content,
        "Description"
    )
    desc_frame.pack(fill='x', pady=(0, 12))

    # Date and time in a row
    datetime_row = tk.Frame(card1.content, bg=EnterpriseTheme.BACKGROUND['card'])
    datetime_row.pack(fill='x', pady=(0, 16))

    # Date field (half width)
    date_col = tk.Frame(datetime_row, bg=EnterpriseTheme.BACKGROUND['card'])
    date_col.pack(side='left', fill='x', expand=True, padx=(0, 8))
    date_frame, date_label, date_entry = EnterpriseTheme.create_input_frame(
        date_col,
        "Date"
    )
    date_frame.pack(fill='x')

    # Time field (half width)
    time_col = tk.Frame(datetime_row, bg=EnterpriseTheme.BACKGROUND['card'])
    time_col.pack(side='left', fill='x', expand=True, padx=(8, 0))
    time_frame, time_label, time_entry = EnterpriseTheme.create_input_frame(
        time_col,
        "Time"
    )
    time_frame.pack(fill='x')

    # Buttons
    btn_row = tk.Frame(card1.content, bg=EnterpriseTheme.BACKGROUND['card'])
    btn_row.pack(fill='x')

    # Primary button (blue - for main action)
    create_btn = EnterpriseTheme.create_button(
        btn_row,
        "Create Event",
        variant='primary'
    )
    create_btn.pack(side='right')

    # Secondary button (bordered)
    cancel_btn = EnterpriseTheme.create_button(
        btn_row,
        "Cancel",
        variant='secondary'
    )
    cancel_btn.pack(side='right', padx=(0, 8))

    # Ghost button (minimal)
    draft_btn = EnterpriseTheme.create_button(
        btn_row,
        "Save as Draft",
        variant='ghost'
    )
    draft_btn.pack(side='right', padx=(0, 8))

    # ========================================================================
    # Card 2: Upcoming Events
    # ========================================================================

    card2 = EnterpriseTheme.create_card_frame(main)
    card2.pack(fill='both', expand=True)

    # Card header
    events_title = tk.Label(
        card2.content,
        text="Upcoming Events",
        bg=EnterpriseTheme.BACKGROUND['card'],
        fg=EnterpriseTheme.TEXT['primary'],
        font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['h2'], 'bold')
    )
    events_title.pack(anchor='w', pady=(0, 16))

    # Event list items
    events = [
        {"title": "Team Meeting", "time": "Today, 2:00 PM", "type": "meeting"},
        {"title": "Code Review", "time": "Tomorrow, 10:30 AM", "type": "focus"},
        {"title": "Lunch Break", "time": "Tomorrow, 12:00 PM", "type": "break"},
    ]

    for event in events:
        event_item = tk.Frame(
            card2.content,
            bg=EnterpriseTheme.BACKGROUND['card'],
            highlightbackground=EnterpriseTheme.BORDER['light'],
            highlightthickness=1
        )
        event_item.pack(fill='x', pady=(0, 8), ipady=8, ipadx=12)

        # Event type indicator (colored dot)
        color = EnterpriseTheme.get_event_color(event['type'])
        indicator = tk.Label(
            event_item,
            text="●",
            bg=EnterpriseTheme.BACKGROUND['card'],
            fg=color,
            font=(EnterpriseTheme.get_font_family(), 16)
        )
        indicator.pack(side='left', padx=(0, 8))

        # Event details
        details = tk.Frame(event_item, bg=EnterpriseTheme.BACKGROUND['card'])
        details.pack(side='left', fill='both', expand=True)

        event_title_label = tk.Label(
            details,
            text=event['title'],
            bg=EnterpriseTheme.BACKGROUND['card'],
            fg=EnterpriseTheme.TEXT['primary'],
            font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['body'], 'normal'),
            anchor='w'
        )
        event_title_label.pack(anchor='w')

        event_time_label = tk.Label(
            details,
            text=event['time'],
            bg=EnterpriseTheme.BACKGROUND['card'],
            fg=EnterpriseTheme.TEXT['tertiary'],
            font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['small'], 'normal'),
            anchor='w'
        )
        event_time_label.pack(anchor='w')

    # ========================================================================
    # Status bar
    # ========================================================================

    status = tk.Frame(main, bg=EnterpriseTheme.BACKGROUND['app'])
    status.pack(fill='x', pady=(16, 0))

    status_text = tk.Label(
        status,
        text="3 events scheduled this week",
        bg=EnterpriseTheme.BACKGROUND['app'],
        fg=EnterpriseTheme.TEXT['tertiary'],
        font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['small'], 'normal')
    )
    status_text.pack(anchor='w')

    root.mainloop()


if __name__ == '__main__':
    create_demo()
