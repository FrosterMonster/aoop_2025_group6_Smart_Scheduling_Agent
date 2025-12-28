"""Enterprise-Grade Modern UI Theme

A clean, light, professional theme with:
- Soft white and light gray backgrounds
- Subtle borders and gentle shadows
- Modern sans-serif typography with clear hierarchy
- Rounded input fields and cards
- Minimal thin-stroke iconography
- Blue used sparingly for focus and interaction
- Flat design with soft elevation
"""

from tkinter import ttk, font as tkfont
import tkinter as tk
from typing import Optional


class EnterpriseTheme:
    """Enterprise-grade modern theme with clean, light aesthetic"""

    # ============================================================================
    # COLOR SYSTEM - Soft, Professional Palette
    # ============================================================================

    # Backgrounds - Clean whites and soft light grays
    BACKGROUND = {
        'app': '#F8F9FA',             # App background - very light gray
        'card': '#FFFFFF',            # Card/container background - pure white
        'input': '#FFFFFF',           # Input field background - white
        'hover': '#F1F3F5',           # Hover state - barely gray
        'active': '#E9ECEF',          # Active/selected state
        'disabled': '#F8F9FA',        # Disabled background
    }

    # Borders - Very subtle, almost invisible
    BORDER = {
        'default': '#DEE2E6',         # Default subtle border
        'light': '#E9ECEF',           # Even lighter border
        'input': '#CED4DA',           # Input field border
        'focus': '#0066FF',           # Blue for focus (sparingly)
        'hover': '#ADB5BD',           # Border on hover
    }

    # Text - Professional gray scale
    TEXT = {
        'primary': '#212529',         # Primary text - dark gray (not black)
        'secondary': '#495057',       # Secondary text - medium gray
        'tertiary': '#6C757D',        # Tertiary text - lighter gray
        'placeholder': '#ADB5BD',     # Placeholder text
        'disabled': '#CED4DA',        # Disabled text
        'inverse': '#FFFFFF',         # White on dark backgrounds
    }

    # Blue - ONLY for interaction/focus (use very sparingly!)
    BLUE = {
        'focus': '#0066FF',           # Focus state only
        'hover': '#0052CC',           # Hover on blue elements
        'selected': '#E7F1FF',        # Very light blue for selected items
        'subtle': '#F0F6FF',          # Extremely subtle blue tint
    }

    # Shadows - Extremely gentle, barely visible
    SHADOW = {
        'card': '#00000008',          # Card shadow (very subtle)
        'hover': '#00000012',         # Hover elevation
        'input': '#00000010',         # Input field shadow
        'none': 'transparent',        # No shadow
    }

    # Semantic - Status colors
    SEMANTIC = {
        'success': '#10B981',
        'success_bg': '#ECFDF5',
        'warning': '#F59E0B',
        'warning_bg': '#FFFBEB',
        'error': '#EF4444',
        'error_bg': '#FEF2F2',
        'info': '#3B82F6',
        'info_bg': '#EFF6FF',
    }

    # Event Type Colors - Muted professional palette
    EVENT_COLORS = {
        'meeting': '#8B5CF6',         # Purple
        'focus': '#3B82F6',           # Blue
        'break': '#10B981',           # Green
        'personal': '#F59E0B',        # Amber
        'task': '#EC4899',            # Pink
        'other': '#06B6D4',           # Cyan
    }

    # ============================================================================
    # TYPOGRAPHY - Modern Sans-Serif with Clear Hierarchy
    # ============================================================================

    # Font Family - Clean, neutral sans-serif
    FONT_FAMILIES = [
        'Segoe UI',                   # Windows default (clean, readable)
        'SF Pro Text',                # macOS
        'Roboto',                     # Android/Modern
        'Helvetica Neue',             # Classic
        'Arial',                      # Universal fallback
        'sans-serif'
    ]

    # Type Scale - Restrained, clear hierarchy
    TYPE_SCALE = {
        'h1': 24,                     # Main headings
        'h2': 18,                     # Section headers
        'h3': 16,                     # Subsection headers
        'body': 14,                   # Default body text
        'small': 12,                  # Small text, captions
        'tiny': 11,                   # Very small labels
    }

    # Font Weights - Minimal, mostly regular
    WEIGHT = {
        'normal': 'normal',           # 400 - use this most of the time
        'medium': 'normal',           # 500 (fallback to normal)
        'semibold': 'bold',           # 600 - use sparingly for headings
    }

    # Line Heights
    LINE_HEIGHT = {
        'tight': 1.2,
        'normal': 1.5,
        'relaxed': 1.75,
    }

    # ============================================================================
    # SPACING - 8px base unit (generous, clean)
    # ============================================================================

    SPACING = {
        'none': 0,
        'xs': 4,                      # Minimal spacing
        'sm': 8,                      # Small gaps
        'md': 16,                     # Medium spacing (default)
        'lg': 24,                     # Large spacing
        'xl': 32,                     # Extra large
        'xxl': 48,                    # Section spacing
    }

    # ============================================================================
    # RADIUS - Gentle rounded corners
    # ============================================================================

    RADIUS = {
        'none': 0,
        'sm': 4,                      # Subtle rounding
        'md': 6,                      # Input fields, buttons
        'lg': 8,                      # Cards
        'xl': 12,                     # Large containers
    }

    # ============================================================================
    # BORDERS - Always 1px, subtle
    # ============================================================================

    BORDER_WIDTH = {
        'default': 1,                 # All borders are 1px
    }

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    @staticmethod
    def get_font_family() -> str:
        """Get the first available font family

        Returns:
            Font family name
        """
        import tkinter.font as tkfont
        available_fonts = tkfont.families()

        for font_family in EnterpriseTheme.FONT_FAMILIES:
            if font_family in available_fonts:
                return font_family

        return 'TkDefaultFont'

    @staticmethod
    def get_event_color(event_type: str) -> str:
        """Get color for event type

        Args:
            event_type: Type of event

        Returns:
            Hex color code
        """
        return EnterpriseTheme.EVENT_COLORS.get(
            event_type.lower(),
            EnterpriseTheme.EVENT_COLORS['other']
        )

    @staticmethod
    def configure_styles(style: ttk.Style, root: tk.Tk):
        """Configure all enterprise theme ttk styles

        Args:
            style: ttk.Style instance
            root: Root window
        """
        # Use 'clam' as base theme
        style.theme_use('clam')

        # Configure root window - clean light gray background
        root.configure(bg=EnterpriseTheme.BACKGROUND['app'])

        # Get best available font
        font_family = EnterpriseTheme.get_font_family()

        # =======================================================================
        # FRAME STYLES
        # =======================================================================

        # Default frame - light gray
        style.configure('TFrame',
                       background=EnterpriseTheme.BACKGROUND['app'])

        # Card frame - pure white
        style.configure('Enterprise.Card.TFrame',
                       background=EnterpriseTheme.BACKGROUND['card'],
                       relief='flat',
                       borderwidth=0)

        # =======================================================================
        # LABEL STYLES - Neutral, readable typography
        # =======================================================================

        # H1 - Main page headings (bold, larger)
        style.configure('Enterprise.H1.TLabel',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['h1'], 'bold'))

        # H2 - Section headers (bold)
        style.configure('Enterprise.H2.TLabel',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['h2'], 'bold'))

        # H3 - Subsection headers (bold)
        style.configure('Enterprise.H3.TLabel',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['h3'], 'bold'))

        # Body text - default (regular weight, most common)
        style.configure('TLabel',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body'], 'normal'))

        # Secondary text - de-emphasized
        style.configure('Enterprise.Secondary.TLabel',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['secondary'],
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body'], 'normal'))

        # Small text - captions, helper text
        style.configure('Enterprise.Small.TLabel',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['tertiary'],
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['small'], 'normal'))

        # =======================================================================
        # BUTTON STYLES - Rounded, flat, minimal
        # =======================================================================

        # Primary button - Blue (use sparingly for main actions only!)
        style.configure('Enterprise.Primary.TButton',
                       background=EnterpriseTheme.BLUE['focus'],
                       foreground='#FFFFFF',
                       borderwidth=0,
                       relief='flat',
                       padding=(EnterpriseTheme.SPACING['md'], EnterpriseTheme.SPACING['sm']),
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body'], 'normal'))

        style.map('Enterprise.Primary.TButton',
                 background=[
                     ('active', EnterpriseTheme.BLUE['hover']),
                     ('disabled', EnterpriseTheme.BACKGROUND['disabled'])
                 ],
                 foreground=[
                     ('disabled', EnterpriseTheme.TEXT['disabled'])
                 ])

        # Secondary button - Subtle border, no fill
        style.configure('Enterprise.Secondary.TButton',
                       background=EnterpriseTheme.BACKGROUND['card'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       borderwidth=1,
                       relief='solid',
                       padding=(EnterpriseTheme.SPACING['md'], EnterpriseTheme.SPACING['sm']),
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body'], 'normal'))

        style.map('Enterprise.Secondary.TButton',
                 background=[
                     ('active', EnterpriseTheme.BACKGROUND['hover']),
                     ('disabled', EnterpriseTheme.BACKGROUND['disabled'])
                 ],
                 foreground=[
                     ('disabled', EnterpriseTheme.TEXT['disabled'])
                 ],
                 bordercolor=[
                     ('active', EnterpriseTheme.BORDER['hover']),
                     ('!active', EnterpriseTheme.BORDER['default'])
                 ])

        # Subtle/Ghost button - Transparent, minimal
        style.configure('Enterprise.Ghost.TButton',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['secondary'],
                       borderwidth=0,
                       relief='flat',
                       padding=(EnterpriseTheme.SPACING['sm'], EnterpriseTheme.SPACING['xs']),
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body'], 'normal'))

        style.map('Enterprise.Ghost.TButton',
                 background=[
                     ('active', EnterpriseTheme.BACKGROUND['hover']),
                 ],
                 foreground=[
                     ('active', EnterpriseTheme.TEXT['primary']),
                     ('disabled', EnterpriseTheme.TEXT['disabled'])
                 ])

        # =======================================================================
        # ENTRY STYLES - Clean, rounded input fields
        # =======================================================================

        style.configure('Enterprise.TEntry',
                       fieldbackground=EnterpriseTheme.BACKGROUND['input'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       borderwidth=1,
                       relief='solid',
                       insertcolor=EnterpriseTheme.BLUE['focus'],  # Blue cursor for focus
                       padding=(EnterpriseTheme.SPACING['sm'], EnterpriseTheme.SPACING['sm']),
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body'], 'normal'))

        style.map('Enterprise.TEntry',
                 fieldbackground=[
                     ('disabled', EnterpriseTheme.BACKGROUND['disabled'])
                 ],
                 foreground=[
                     ('disabled', EnterpriseTheme.TEXT['disabled'])
                 ],
                 bordercolor=[
                     ('focus', EnterpriseTheme.BORDER['focus']),  # Blue border on focus
                     ('!focus', EnterpriseTheme.BORDER['input'])
                 ])

        # =======================================================================
        # COMBOBOX STYLES - Clean dropdowns
        # =======================================================================

        style.configure('Enterprise.TCombobox',
                       fieldbackground=EnterpriseTheme.BACKGROUND['input'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       borderwidth=1,
                       relief='solid',
                       padding=(EnterpriseTheme.SPACING['sm'], EnterpriseTheme.SPACING['sm']),
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body'], 'normal'),
                       arrowcolor=EnterpriseTheme.TEXT['tertiary'])

        style.map('Enterprise.TCombobox',
                 fieldbackground=[
                     ('disabled', EnterpriseTheme.BACKGROUND['disabled'])
                 ],
                 foreground=[
                     ('disabled', EnterpriseTheme.TEXT['disabled'])
                 ],
                 bordercolor=[
                     ('focus', EnterpriseTheme.BORDER['focus']),
                     ('!focus', EnterpriseTheme.BORDER['input'])
                 ])

        # =======================================================================
        # CHECKBUTTON STYLES
        # =======================================================================

        style.configure('Enterprise.TCheckbutton',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body']))

        # =======================================================================
        # RADIOBUTTON STYLES
        # =======================================================================

        style.configure('Enterprise.TRadiobutton',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['primary'],
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body']))

        # =======================================================================
        # SCROLLBAR STYLES - Minimal
        # =======================================================================

        style.configure('Enterprise.Vertical.TScrollbar',
                       background=EnterpriseTheme.BORDER['default'],
                       troughcolor=EnterpriseTheme.BACKGROUND['hover'],
                       borderwidth=0,
                       arrowcolor=EnterpriseTheme.TEXT['tertiary'])

        style.map('Enterprise.Vertical.TScrollbar',
                 background=[
                     ('active', EnterpriseTheme.TEXT['secondary'])
                 ])

        style.configure('Enterprise.Horizontal.TScrollbar',
                       background=EnterpriseTheme.BORDER['default'],
                       troughcolor=EnterpriseTheme.BACKGROUND['hover'],
                       borderwidth=0,
                       arrowcolor=EnterpriseTheme.TEXT['tertiary'])

        # =======================================================================
        # PROGRESSBAR STYLES
        # =======================================================================

        style.configure('Enterprise.Horizontal.TProgressbar',
                       background=EnterpriseTheme.BLUE['focus'],
                       troughcolor=EnterpriseTheme.BORDER['light'],
                       borderwidth=0,
                       thickness=4)

        # =======================================================================
        # SEPARATOR STYLES
        # =======================================================================

        style.configure('Enterprise.TSeparator',
                       background=EnterpriseTheme.BORDER['default'])

        # =======================================================================
        # NOTEBOOK (TABS) STYLES
        # =======================================================================

        style.configure('Enterprise.TNotebook',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       borderwidth=0,
                       relief='flat')

        style.configure('Enterprise.TNotebook.Tab',
                       background=EnterpriseTheme.BACKGROUND['app'],
                       foreground=EnterpriseTheme.TEXT['secondary'],
                       padding=(EnterpriseTheme.SPACING['lg'], EnterpriseTheme.SPACING['md']),
                       borderwidth=0,
                       font=(font_family, EnterpriseTheme.TYPE_SCALE['body']))

        style.map('Enterprise.TNotebook.Tab',
                 background=[
                     ('selected', EnterpriseTheme.BACKGROUND['card']),
                     ('active', EnterpriseTheme.BACKGROUND['hover'])
                 ],
                 foreground=[
                     ('selected', EnterpriseTheme.BLUE['focus']),
                     ('active', EnterpriseTheme.TEXT['primary'])
                 ])

    @staticmethod
    def create_card_frame(parent, padding: int = None, **kwargs) -> tk.Frame:
        """Create a clean white card with subtle border

        Args:
            parent: Parent widget
            padding: Internal padding (default: 16px)
            **kwargs: Additional frame options

        Returns:
            Frame with card styling
        """
        if padding is None:
            padding = EnterpriseTheme.SPACING['md']

        # Create white card with 1px border
        frame = tk.Frame(
            parent,
            bg=EnterpriseTheme.BACKGROUND['card'],
            highlightbackground=EnterpriseTheme.BORDER['default'],
            highlightthickness=1,
            **kwargs
        )

        # Add padding container
        padding_frame = tk.Frame(frame, bg=EnterpriseTheme.BACKGROUND['card'])
        padding_frame.pack(fill='both', expand=True, padx=padding, pady=padding)

        # Store reference to content area
        frame.content = padding_frame

        return frame

    @staticmethod
    def create_input_frame(parent, label_text: str, **entry_kwargs) -> tuple:
        """Create a clean labeled input field

        Args:
            parent: Parent widget
            label_text: Label text
            **entry_kwargs: Additional entry options

        Returns:
            Tuple of (frame, label, entry)
        """
        font_family = EnterpriseTheme.get_font_family()

        frame = tk.Frame(parent, bg=EnterpriseTheme.BACKGROUND['card'])

        # Label - small, medium gray
        label = tk.Label(
            frame,
            text=label_text,
            bg=EnterpriseTheme.BACKGROUND['card'],
            fg=EnterpriseTheme.TEXT['secondary'],
            font=(font_family, EnterpriseTheme.TYPE_SCALE['small'], 'normal'),
            anchor='w'
        )
        label.pack(fill='x', pady=(0, 4))

        # Entry - rounded, white background
        entry = ttk.Entry(frame, style='Enterprise.TEntry', **entry_kwargs)
        entry.pack(fill='x')

        return frame, label, entry

    @staticmethod
    def create_button(parent, text: str, variant: str = 'primary', **kwargs) -> ttk.Button:
        """Create a clean, flat button

        Args:
            parent: Parent widget
            text: Button text
            variant: Button variant ('primary' = blue, 'secondary' = bordered, 'ghost' = minimal)
            **kwargs: Additional button options

        Returns:
            Styled button
        """
        style_map = {
            'primary': 'Enterprise.Primary.TButton',      # Blue - use sparingly!
            'secondary': 'Enterprise.Secondary.TButton',  # Bordered
            'ghost': 'Enterprise.Ghost.TButton',          # Minimal
        }

        style = style_map.get(variant, 'Enterprise.Primary.TButton')
        return ttk.Button(parent, text=text, style=style, **kwargs)
