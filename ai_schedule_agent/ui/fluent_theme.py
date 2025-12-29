"""Fluent Design System Theme for AI Schedule Agent

Implements Microsoft's Fluent Design System principles:
- Acrylic materials (frosted glass effect)
- Reveal highlights (interactive glow)
- Depth and elevation
- Motion and animations
- Responsive typography
"""

from tkinter import ttk, font as tkfont
import tkinter as tk
from typing import Dict, Tuple


class FluentTheme:
    """Fluent Design System theme implementation for Tkinter

    This theme follows Microsoft's Fluent Design principles while
    adapting to Tkinter's capabilities and limitations.
    """

    # ============================================================================
    # COLOR SYSTEM
    # ============================================================================

    # Accent Colors - BizLink uses subtle monochrome accents
    ACCENT = {
        'default': '#1A1A1A',      # Dark gray/black (BizLink primary)
        'light1': '#2E2E2E',       # Slightly lighter
        'light2': '#464646',       # Medium
        'light3': '#6B6B6B',       # Light gray
        'dark1': '#121212',        # Darker
        'dark2': '#0A0A0A',        # Almost black
        'dark3': '#000000',        # Pure black
        'blue': '#0078D4',         # Optional blue for special cases
    }

    # Neutral Colors - Matched to BizLink reference
    NEUTRAL = {
        'gray10': '#FAF9F7',       # Warm beige background (BizLink)
        'gray20': '#F5F4F2',       # Slightly darker warm bg
        'gray30': '#EFEFEF',       # Light gray
        'gray40': '#E5E5E5',       # Subtle borders
        'gray50': '#D4D4D4',
        'gray60': '#B8B8B8',
        'gray70': '#A0A0A0',
        'gray80': '#8A8A8A',
        'gray90': '#757575',
        'gray100': '#6B6B6B',      # Secondary text (BizLink)
        'gray110': '#5F5F5F',
        'gray120': '#525252',
        'gray130': '#464646',      # Medium text
        'gray140': '#3A3A3A',
        'gray150': '#2E2E2E',
        'gray160': '#1A1A1A',      # Primary text (BizLink)
        'gray170': '#121212',
        'gray180': '#0A0A0A',
        'gray190': '#000000',      # Pure black
    }

    # Semantic Colors
    SEMANTIC = {
        'success': '#107C10',      # Green
        'success_bg': '#DFF6DD',
        'warning': '#FF8C00',      # Orange
        'warning_bg': '#FFF4CE',
        'error': '#D13438',        # Red
        'error_bg': '#FDE7E9',
        'info': '#0078D4',         # Blue
        'info_bg': '#E1F3FB',
    }

    # Acrylic Background Colors (semi-transparent simulation)
    ACRYLIC = {
        'base': '#F9F9F9',         # Base layer
        'layer1': '#FCFCFC',       # 80% opacity simulation
        'layer2': '#FEFEFE',       # 60% opacity simulation
        'overlay': '#00000008',    # Subtle overlay
        'border': '#E5E5E5',       # Acrylic border
    }

    # Depth Layers - BizLink elevation system
    ELEVATION = {
        'layer0': '#FFFFFF',       # Pure white cards (BizLink)
        'layer1': '#FFFFFF',       # Card surface
        'layer2': '#FFFFFF',       # Sidebar WHITE (BizLink sidebar)
        'layer3': '#F7F7F7',       # Subtle hover
        'layer4': '#2A2A2A',       # Dark card (BizLink "Prime Estate")
    }

    # Event Type Colors (matching consultation types)
    EVENT_COLORS = {
        'meeting': '#8764B8',      # Purple
        'focus': '#0078D4',        # Blue
        'break': '#107C10',        # Green
        'personal': '#D83B01',     # Orange
        'task': '#E3008C',         # Pink
        'other': '#00B7C3',        # Teal
    }

    # ============================================================================
    # TYPOGRAPHY SYSTEM
    # ============================================================================

    # Type Ramp (Font sizes in points)
    TYPE_RAMP = {
        'caption': 10,
        'body': 14,
        'body_strong': 14,
        'subtitle': 20,
        'title': 28,
        'title_large': 40,
        'display': 68,
    }

    # Font Weights
    WEIGHTS = {
        'regular': 'normal',
        'semibold': 'bold',        # Tkinter only supports normal/bold
        'bold': 'bold',
    }

    # Line Heights (multipliers)
    LINE_HEIGHTS = {
        'caption': 1.3,
        'body': 1.4,
        'subtitle': 1.3,
        'title': 1.2,
        'display': 1.1,
    }

    # Font Families (priority order)
    FONT_FAMILIES = ['Segoe UI', 'SF Pro Text', 'Microsoft YaHei', 'Arial', 'sans-serif']

    # ============================================================================
    # SPACING SYSTEM
    # ============================================================================

    # 4px base unit
    SPACING = {
        'none': 0,
        'xxs': 2,
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 20,
        'xxl': 24,
        'xxxl': 32,
        'huge': 40,
        'massive': 48,
        'gigantic': 64,
    }

    # ============================================================================
    # EFFECTS SYSTEM
    # ============================================================================

    # Border Radius - BizLink style
    RADIUS = {
        'none': 0,
        'small': 6,        # Small elements
        'medium': 8,       # Buttons
        'large': 12,       # Cards (BizLink)
        'xlarge': 16,      # Large cards
        'circular': 9999,  # Pills/avatars
    }

    # Shadows - BizLink soft shadows
    # Note: Tkinter has limited shadow support, these are reference values
    SHADOWS = {
        'card': {'offset': (0, 2), 'blur': 6, 'color': 'rgba(0,0,0,0.06)'},  # BizLink card shadow
        'card_hover': {'offset': (0, 4), 'blur': 12, 'color': 'rgba(0,0,0,0.08)'}, # Card hover
        'elevated': {'offset': (0, 6), 'blur': 16, 'color': 'rgba(0,0,0,0.10)'},  # Elevated
        'modal': {'offset': (0, 12), 'blur': 32, 'color': 'rgba(0,0,0,0.15)'},     # Modals
        'dark_card': {'offset': (0, 4), 'blur': 20, 'color': 'rgba(0,0,0,0.25)'}, # Dark card
    }

    # Border Widths
    BORDERS = {
        'thin': 1,
        'medium': 2,
        'thick': 3,
    }

    # ============================================================================
    # MOTION SYSTEM
    # ============================================================================

    # Duration (in milliseconds)
    DURATION = {
        'fast_enter': 150,
        'fast_leave': 75,
        'normal_enter': 250,
        'normal_leave': 200,
        'slow_enter': 500,
        'slow_leave': 400,
    }

    # Easing Curves (for use with canvas animations)
    EASING = {
        'linear': lambda t: t,
        'ease_in': lambda t: t * t,
        'ease_out': lambda t: t * (2 - t),
        'ease_in_out': lambda t: t * t * (3 - 2 * t),
        'decelerate': lambda t: 1 - (1 - t) ** 2,
        'accelerate': lambda t: t ** 2,
    }

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    @staticmethod
    def get_font_family() -> str:
        """Get the first available font family from the priority list

        Returns:
            Font family name
        """
        import tkinter.font as tkfont
        available_fonts = tkfont.families()

        for font_family in FluentTheme.FONT_FAMILIES:
            if font_family in available_fonts:
                return font_family

        return 'TkDefaultFont'

    @staticmethod
    def get_accent_color(variant: str = 'default') -> str:
        """Get accent color variant

        Args:
            variant: Color variant (default, light1-3, dark1-3)

        Returns:
            Hex color code
        """
        return FluentTheme.ACCENT.get(variant, FluentTheme.ACCENT['default'])

    @staticmethod
    def get_neutral_color(level: int) -> str:
        """Get neutral gray color by level

        Args:
            level: Gray level (10-190)

        Returns:
            Hex color code
        """
        key = f'gray{level}'
        return FluentTheme.NEUTRAL.get(key, FluentTheme.NEUTRAL['gray130'])

    @staticmethod
    def get_event_color(event_type: str) -> str:
        """Get color for event type

        Args:
            event_type: Type of event

        Returns:
            Hex color code
        """
        return FluentTheme.EVENT_COLORS.get(
            event_type.lower(),
            FluentTheme.EVENT_COLORS['other']
        )

    @staticmethod
    def get_elevation_color(layer: int) -> str:
        """Get background color for elevation layer

        Args:
            layer: Elevation layer (0-4)

        Returns:
            Hex color code
        """
        key = f'layer{layer}'
        return FluentTheme.ELEVATION.get(key, FluentTheme.ELEVATION['layer0'])

    @staticmethod
    def configure_styles(style: ttk.Style, root: tk.Tk):
        """Configure all Fluent Design ttk styles

        Args:
            style: ttk.Style instance
            root: Root window
        """
        # Use 'clam' as base theme
        style.theme_use('clam')

        # Configure root window
        root.configure(bg=FluentTheme.NEUTRAL['gray10'])

        # Get font family
        font_family = FluentTheme.get_font_family()

        # =======================================================================
        # FRAME STYLES
        # =======================================================================

        style.configure('TFrame',
                       background=FluentTheme.NEUTRAL['gray10'])

        style.configure('Fluent.TFrame',
                       background=FluentTheme.ELEVATION['layer0'],
                       relief='flat',
                       borderwidth=0)

        style.configure('FluentCard.TFrame',
                       background=FluentTheme.ELEVATION['layer0'],  # White cards like reference
                       relief='flat',
                       borderwidth=0)  # No border, shadows provide depth

        style.configure('FluentSidebar.TFrame',
                       background=FluentTheme.ELEVATION['layer2'],
                       relief='flat',
                       borderwidth=0)

        style.configure('FluentAcrylic.TFrame',
                       background=FluentTheme.ACRYLIC['base'],
                       relief='flat',
                       borderwidth=FluentTheme.BORDERS['thin'])

        # =======================================================================
        # LABEL STYLES
        # =======================================================================

        # Body text (default)
        style.configure('TLabel',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        # Caption
        style.configure('Caption.TLabel',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray130'],
                       font=(font_family, FluentTheme.TYPE_RAMP['caption']))

        # Body Strong
        style.configure('BodyStrong.TLabel',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       font=(font_family, FluentTheme.TYPE_RAMP['body_strong'], 'bold'))

        # Subtitle
        style.configure('Subtitle.TLabel',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       font=(font_family, FluentTheme.TYPE_RAMP['subtitle'], 'bold'))

        # Title
        style.configure('Title.TLabel',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       font=(font_family, FluentTheme.TYPE_RAMP['title'], 'bold'))

        # Display
        style.configure('Display.TLabel',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       font=(font_family, FluentTheme.TYPE_RAMP['display'], 'bold'))

        # Secondary text
        style.configure('Secondary.TLabel',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray130'],
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        # Disabled text
        style.configure('Disabled.TLabel',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray90'],
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        # =======================================================================
        # BUTTON STYLES
        # =======================================================================

        # Primary Button (Accent filled)
        style.configure('Primary.TButton',
                       background=FluentTheme.ACCENT['default'],
                       foreground='#FFFFFF',
                       borderwidth=0,
                       relief='flat',
                       padding=(FluentTheme.SPACING['lg'], FluentTheme.SPACING['sm']),
                       font=(font_family, FluentTheme.TYPE_RAMP['body'], 'bold'))

        style.map('Primary.TButton',
                 background=[
                     ('active', FluentTheme.ACCENT['dark1']),
                     ('pressed', FluentTheme.ACCENT['dark2']),
                     ('disabled', FluentTheme.NEUTRAL['gray60'])
                 ])

        # Secondary Button (Outlined)
        style.configure('Secondary.TButton',
                       background=FluentTheme.ELEVATION['layer0'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       borderwidth=FluentTheme.BORDERS['thin'],
                       relief='solid',
                       padding=(FluentTheme.SPACING['lg'], FluentTheme.SPACING['sm']),
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        style.map('Secondary.TButton',
                 background=[
                     ('active', FluentTheme.ELEVATION['layer2']),
                     ('pressed', FluentTheme.ELEVATION['layer3']),
                     ('disabled', FluentTheme.NEUTRAL['gray20'])
                 ],
                 foreground=[
                     ('disabled', FluentTheme.NEUTRAL['gray90'])
                 ])

        # Accent Button (Accent outlined)
        style.configure('Accent.TButton',
                       background=FluentTheme.ELEVATION['layer0'],
                       foreground=FluentTheme.ACCENT['default'],
                       borderwidth=FluentTheme.BORDERS['thin'],
                       relief='solid',
                       padding=(FluentTheme.SPACING['lg'], FluentTheme.SPACING['sm']),
                       font=(font_family, FluentTheme.TYPE_RAMP['body'], 'bold'))

        style.map('Accent.TButton',
                 background=[
                     ('active', FluentTheme.ACRYLIC['layer1']),
                     ('pressed', FluentTheme.ACRYLIC['layer2']),
                     ('disabled', FluentTheme.NEUTRAL['gray20'])
                 ],
                 foreground=[
                     ('disabled', FluentTheme.NEUTRAL['gray90'])
                 ])

        # Subtle Button (Transparent)
        style.configure('Subtle.TButton',
                       background=FluentTheme.ELEVATION['layer0'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       borderwidth=0,
                       relief='flat',
                       padding=(FluentTheme.SPACING['lg'], FluentTheme.SPACING['sm']),
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        style.map('Subtle.TButton',
                 background=[
                     ('active', FluentTheme.ELEVATION['layer2']),
                     ('pressed', FluentTheme.ELEVATION['layer3']),
                     ('disabled', FluentTheme.ELEVATION['layer0'])
                 ],
                 foreground=[
                     ('disabled', FluentTheme.NEUTRAL['gray90'])
                 ])

        # =======================================================================
        # ENTRY STYLES
        # =======================================================================

        style.configure('Fluent.TEntry',
                       fieldbackground=FluentTheme.ELEVATION['layer0'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       borderwidth=FluentTheme.BORDERS['thin'],
                       relief='solid',
                       padding=(FluentTheme.SPACING['sm'], FluentTheme.SPACING['sm']),
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        style.map('Fluent.TEntry',
                 fieldbackground=[
                     ('focus', FluentTheme.ELEVATION['layer0']),
                     ('disabled', FluentTheme.NEUTRAL['gray20'])
                 ],
                 foreground=[
                     ('disabled', FluentTheme.NEUTRAL['gray90'])
                 ],
                 bordercolor=[
                     ('focus', FluentTheme.ACCENT['default']),
                     ('!focus', FluentTheme.NEUTRAL['gray60'])
                 ])

        # =======================================================================
        # COMBOBOX STYLES
        # =======================================================================

        style.configure('Fluent.TCombobox',
                       fieldbackground=FluentTheme.ELEVATION['layer0'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       borderwidth=FluentTheme.BORDERS['thin'],
                       relief='solid',
                       padding=(FluentTheme.SPACING['sm'], FluentTheme.SPACING['sm']),
                       font=(font_family, FluentTheme.TYPE_RAMP['body']),
                       arrowcolor=FluentTheme.NEUTRAL['gray130'])

        style.map('Fluent.TCombobox',
                 fieldbackground=[
                     ('focus', FluentTheme.ELEVATION['layer0']),
                     ('readonly', FluentTheme.ELEVATION['layer0']),
                     ('disabled', FluentTheme.NEUTRAL['gray20'])
                 ],
                 foreground=[
                     ('disabled', FluentTheme.NEUTRAL['gray90'])
                 ],
                 bordercolor=[
                     ('focus', FluentTheme.ACCENT['default']),
                     ('!focus', FluentTheme.NEUTRAL['gray60'])
                 ])

        # =======================================================================
        # CHECKBUTTON STYLES
        # =======================================================================

        style.configure('Fluent.TCheckbutton',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        # =======================================================================
        # RADIOBUTTON STYLES
        # =======================================================================

        style.configure('Fluent.TRadiobutton',
                       background=FluentTheme.NEUTRAL['gray10'],
                       foreground=FluentTheme.NEUTRAL['gray160'],
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        # =======================================================================
        # PROGRESSBAR STYLES
        # =======================================================================

        style.configure('Fluent.Horizontal.TProgressbar',
                       background=FluentTheme.ACCENT['default'],
                       troughcolor=FluentTheme.NEUTRAL['gray40'],
                       borderwidth=0,
                       thickness=4)

        # =======================================================================
        # SCROLLBAR STYLES
        # =======================================================================

        style.configure('Fluent.Vertical.TScrollbar',
                       background=FluentTheme.NEUTRAL['gray60'],
                       troughcolor=FluentTheme.NEUTRAL['gray20'],
                       borderwidth=0,
                       arrowcolor=FluentTheme.NEUTRAL['gray130'])

        style.map('Fluent.Vertical.TScrollbar',
                 background=[
                     ('active', FluentTheme.NEUTRAL['gray80'])
                 ])

        style.configure('Fluent.Horizontal.TScrollbar',
                       background=FluentTheme.NEUTRAL['gray60'],
                       troughcolor=FluentTheme.NEUTRAL['gray20'],
                       borderwidth=0,
                       arrowcolor=FluentTheme.NEUTRAL['gray130'])

        # =======================================================================
        # SEPARATOR STYLES
        # =======================================================================

        style.configure('Fluent.TSeparator',
                       background=FluentTheme.NEUTRAL['gray40'])

        # =======================================================================
        # NOTEBOOK (TABS) STYLES
        # =======================================================================

        style.configure('Fluent.TNotebook',
                       background=FluentTheme.NEUTRAL['gray10'],
                       borderwidth=0,
                       relief='flat')

        style.configure('Fluent.TNotebook.Tab',
                       background=FluentTheme.ELEVATION['layer0'],
                       foreground=FluentTheme.NEUTRAL['gray130'],
                       padding=(FluentTheme.SPACING['lg'], FluentTheme.SPACING['sm']),
                       borderwidth=0,
                       font=(font_family, FluentTheme.TYPE_RAMP['body']))

        style.map('Fluent.TNotebook.Tab',
                 background=[
                     ('selected', FluentTheme.ELEVATION['layer0']),
                     ('active', FluentTheme.ELEVATION['layer2'])
                 ],
                 foreground=[
                     ('selected', FluentTheme.ACCENT['default']),
                     ('active', FluentTheme.NEUTRAL['gray160'])
                 ])


class FluentAnimation:
    """Animation utilities for Fluent Design motion system"""

    @staticmethod
    def animate_value(widget, duration: int, easing_func, update_func,
                     start_value: float, end_value: float):
        """Animate a value over time

        Args:
            widget: Widget to schedule animation frames on
            duration: Animation duration in milliseconds
            easing_func: Easing function from FluentTheme.EASING
            update_func: Function to call with interpolated value
            start_value: Starting value
            end_value: Ending value
        """
        steps = max(1, duration // 16)  # ~60fps
        current_step = [0]  # Use list to allow modification in closure

        def step():
            current_step[0] += 1
            progress = min(1.0, current_step[0] / steps)
            eased_progress = easing_func(progress)
            current_value = start_value + (end_value - start_value) * eased_progress

            update_func(current_value)

            if current_step[0] < steps:
                widget.after(16, step)

        step()

    @staticmethod
    def fade_in(widget, duration: int = None):
        """Fade in a widget

        Args:
            widget: Widget to fade in
            duration: Duration in milliseconds (default: DURATION['normal_enter'])
        """
        if duration is None:
            duration = FluentTheme.DURATION['normal_enter']

        # Note: Tkinter doesn't support alpha transparency on widgets
        # This is a placeholder for potential Canvas-based implementations
        widget.state(['!disabled']) if hasattr(widget, 'state') else None

    @staticmethod
    def fade_out(widget, duration: int = None):
        """Fade out a widget

        Args:
            widget: Widget to fade out
            duration: Duration in milliseconds (default: DURATION['normal_leave'])
        """
        if duration is None:
            duration = FluentTheme.DURATION['normal_leave']

        # Note: Tkinter doesn't support alpha transparency on widgets
        # This is a placeholder for potential Canvas-based implementations
        widget.state(['disabled']) if hasattr(widget, 'state') else None
