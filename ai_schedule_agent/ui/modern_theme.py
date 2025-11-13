"""Modern UI Theme with Glassmorphism and Neumorphism Effects"""

from tkinter import ttk, font as tkfont
import tkinter as tk


class ModernTheme:
    """Modern theme with glassmorphism and neumorphism styling"""

    # Color Palette - Light blues, whites, and subtle gradients
    COLORS = {
        # Primary Colors
        'primary': '#4A90E2',           # Soft blue
        'primary_light': '#6BA4EC',     # Lighter blue
        'primary_dark': '#357ABD',      # Darker blue

        # Background Colors
        'bg_primary': '#F5F7FA',        # Light gray-blue background
        'bg_secondary': '#FFFFFF',      # Pure white
        'bg_card': '#FAFBFC',          # Card background
        'bg_sidebar': '#E8EDF2',        # Sidebar background

        # Glassmorphism
        'glass_bg': '#FFFFFF',          # Glass background (with alpha)
        'glass_border': '#E0E5EB',      # Glass border
        'glass_shadow': '#00000010',    # Subtle shadow

        # Text Colors
        'text_primary': '#2C3E50',      # Dark blue-gray
        'text_secondary': '#7F8C9A',    # Medium gray
        'text_light': '#A8B2BD',        # Light gray
        'text_white': '#FFFFFF',        # White text

        # Accent Colors
        'accent_blue': '#5B9FED',       # Bright blue
        'accent_green': '#6BCF9F',      # Soft green
        'accent_purple': '#9B7FED',     # Soft purple
        'accent_orange': '#FFAB6B',     # Soft orange
        'accent_pink': '#ED7FA8',       # Soft pink
        'accent_teal': '#5ED4D2',       # Soft teal

        # Status Colors
        'success': '#6BCF9F',           # Green
        'warning': '#FFB946',           # Orange
        'error': '#F07178',             # Red
        'info': '#5B9FED',              # Blue

        # UI Elements
        'border': '#E0E5EB',            # Border color
        'border_light': '#F0F2F5',      # Light border
        'divider': '#E8EDF2',           # Divider line
        'hover': '#F0F4F8',             # Hover state
        'active': '#E8EDF2',            # Active state
        'disabled': '#D0D5DD',          # Disabled state
    }

    # Consultation Type Colors (matching reference design)
    CONSULTATION_COLORS = {
        'meeting': '#9B7FED',           # Purple 
        'focus': '#5B9FED',             # Blue 
        'break': '#6BCF9F',             # Green 
        'personal': '#FFAB6B',          # Orange 
        'task': '#ED7FA8',              # Pink 
        'other': '#5ED4D2',             # Teal 
    }

    # Spacing System
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 24,
        'xxl': 32,
    }

    # Border Radius
    RADIUS = {
        'sm': 6,
        'md': 10,
        'lg': 16,
        'xl': 20,
        'full': 100,
    }

    # Shadows (for neumorphism effect)
    SHADOWS = {
        'light': '2 2 4 #00000010',
        'medium': '4 4 8 #00000015',
        'heavy': '8 8 16 #00000020',
        'inner': 'inset 2 2 4 #00000010',
    }

    # Font Sizes
    FONT_SIZES = {
        'xs': 9,
        'sm': 10,
        'base': 11,
        'md': 12,
        'lg': 14,
        'xl': 16,
        'xxl': 20,
        'title': 24,
    }

    @staticmethod
    def configure_styles(style: ttk.Style, root: tk.Tk):
        """Configure modern ttk styles with glassmorphism effect

        Args:
            style: ttk.Style instance
            root: Root tk window
        """
        # Use 'clam' as base theme for modern look
        style.theme_use('clam')

        # Configure root window
        root.configure(bg=ModernTheme.COLORS['bg_primary'])

        # Configure default fonts with Chinese support
        try:
            default_font = tkfont.Font(family='Microsoft YaHei', size=ModernTheme.FONT_SIZES['base'])
            heading_font = tkfont.Font(family='Microsoft YaHei', size=ModernTheme.FONT_SIZES['lg'], weight='bold')
            title_font = tkfont.Font(family='Microsoft YaHei', size=ModernTheme.FONT_SIZES['title'], weight='bold')
        except:
            default_font = tkfont.Font(size=ModernTheme.FONT_SIZES['base'])
            heading_font = tkfont.Font(size=ModernTheme.FONT_SIZES['lg'], weight='bold')
            title_font = tkfont.Font(size=ModernTheme.FONT_SIZES['title'], weight='bold')

        # === Frame Styles ===
        style.configure('TFrame',
                       background=ModernTheme.COLORS['bg_primary'])

        style.configure('Card.TFrame',
                       background=ModernTheme.COLORS['bg_card'],
                       relief='flat',
                       borderwidth=0)

        style.configure('Sidebar.TFrame',
                       background=ModernTheme.COLORS['bg_sidebar'])

        style.configure('Glass.TFrame',
                       background=ModernTheme.COLORS['glass_bg'],
                       relief='flat',
                       borderwidth=1)

        # === Label Styles ===
        style.configure('TLabel',
                       background=ModernTheme.COLORS['bg_primary'],
                       foreground=ModernTheme.COLORS['text_primary'],
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['base']))

        style.configure('Title.TLabel',
                       background=ModernTheme.COLORS['bg_primary'],
                       foreground=ModernTheme.COLORS['text_primary'],
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['title'], 'bold'))

        style.configure('Heading.TLabel',
                       background=ModernTheme.COLORS['bg_primary'],
                       foreground=ModernTheme.COLORS['text_primary'],
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['lg'], 'bold'))

        style.configure('Secondary.TLabel',
                       background=ModernTheme.COLORS['bg_primary'],
                       foreground=ModernTheme.COLORS['text_secondary'],
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['sm']))

        style.configure('Light.TLabel',
                       background=ModernTheme.COLORS['bg_primary'],
                       foreground=ModernTheme.COLORS['text_light'],
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['xs']))

        # === Button Styles ===
        style.configure('Modern.TButton',
                       background=ModernTheme.COLORS['primary'],
                       foreground=ModernTheme.COLORS['text_white'],
                       borderwidth=0,
                       padding=(16, 10),
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['base'], 'bold'),
                       relief='flat')

        style.map('Modern.TButton',
                 background=[
                     ('active', ModernTheme.COLORS['primary_light']),
                     ('pressed', ModernTheme.COLORS['primary_dark']),
                     ('disabled', ModernTheme.COLORS['disabled'])
                 ])

        style.configure('Glass.TButton',
                       background=ModernTheme.COLORS['glass_bg'],
                       foreground=ModernTheme.COLORS['text_primary'],
                       borderwidth=1,
                       padding=(16, 10),
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['base']),
                       relief='flat')

        style.map('Glass.TButton',
                 background=[
                     ('active', ModernTheme.COLORS['hover']),
                     ('pressed', ModernTheme.COLORS['active'])
                 ])

        style.configure('Icon.TButton',
                       background=ModernTheme.COLORS['bg_secondary'],
                       foreground=ModernTheme.COLORS['text_secondary'],
                       borderwidth=0,
                       padding=(10, 10),
                       relief='flat')

        style.map('Icon.TButton',
                 background=[
                     ('active', ModernTheme.COLORS['hover']),
                     ('pressed', ModernTheme.COLORS['active'])
                 ])

        # === Notebook (Tabs) Styles ===
        style.configure('Modern.TNotebook',
                       background=ModernTheme.COLORS['bg_primary'],
                       borderwidth=0,
                       relief='flat')

        style.configure('Modern.TNotebook.Tab',
                       background=ModernTheme.COLORS['bg_secondary'],
                       foreground=ModernTheme.COLORS['text_secondary'],
                       padding=(20, 12),
                       borderwidth=0,
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['base']))

        style.map('Modern.TNotebook.Tab',
                 background=[
                     ('selected', ModernTheme.COLORS['primary']),
                     ('active', ModernTheme.COLORS['hover'])
                 ],
                 foreground=[
                     ('selected', ModernTheme.COLORS['text_white']),
                     ('active', ModernTheme.COLORS['text_primary'])
                 ])

        # === Entry Styles ===
        style.configure('Modern.TEntry',
                       fieldbackground=ModernTheme.COLORS['bg_secondary'],
                       foreground=ModernTheme.COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       padding=(12, 8),
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['base']))

        # === Combobox Styles ===
        style.configure('Modern.TCombobox',
                       fieldbackground=ModernTheme.COLORS['bg_secondary'],
                       foreground=ModernTheme.COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       padding=(12, 8),
                       font=('Microsoft YaHei', ModernTheme.FONT_SIZES['base']))

        # === Scrollbar Styles ===
        style.configure('Modern.Vertical.TScrollbar',
                       background=ModernTheme.COLORS['bg_secondary'],
                       troughcolor=ModernTheme.COLORS['bg_primary'],
                       borderwidth=0,
                       arrowcolor=ModernTheme.COLORS['text_secondary'])

        # === Progressbar Styles ===
        style.configure('Modern.Horizontal.TProgressbar',
                       background=ModernTheme.COLORS['primary'],
                       troughcolor=ModernTheme.COLORS['border_light'],
                       borderwidth=0,
                       thickness=4)

    @staticmethod
    def create_card_frame(parent, **kwargs):
        """Create a card-style frame with glassmorphism effect

        Args:
            parent: Parent widget
            **kwargs: Additional frame options

        Returns:
            ttk.Frame with card styling
        """
        frame = ttk.Frame(parent, style='Card.TFrame', **kwargs)
        return frame

    @staticmethod
    def create_glass_frame(parent, **kwargs):
        """Create a glassmorphism-style frame

        Args:
            parent: Parent widget
            **kwargs: Additional frame options

        Returns:
            ttk.Frame with glass styling
        """
        frame = ttk.Frame(parent, style='Glass.TFrame', **kwargs)
        return frame

    @staticmethod
    def create_sidebar_frame(parent, **kwargs):
        """Create a sidebar frame

        Args:
            parent: Parent widget
            **kwargs: Additional frame options

        Returns:
            ttk.Frame with sidebar styling
        """
        frame = ttk.Frame(parent, style='Sidebar.TFrame', **kwargs)
        return frame

    @staticmethod
    def get_consultation_color(event_type: str) -> str:
        """Get color for consultation/event type

        Args:
            event_type: Type of event

        Returns:
            Color hex code
        """
        return ModernTheme.CONSULTATION_COLORS.get(
            event_type.lower(),
            ModernTheme.CONSULTATION_COLORS['other']
        )
