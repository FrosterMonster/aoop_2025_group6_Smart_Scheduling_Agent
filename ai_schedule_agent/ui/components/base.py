"""Base Fluent Design UI Components

This module contains foundational UI components following Microsoft's
Fluent Design System principles.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Any
from ai_schedule_agent.ui.fluent_theme import FluentTheme


class FluentComponent:
    """Base class for all Fluent Design components

    Provides common functionality for component lifecycle, theming,
    and event handling.
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize Fluent component

        Args:
            parent: Parent widget
            **kwargs: Additional configuration options
        """
        self.parent = parent
        self.frame = ttk.Frame(parent, style='Fluent.TFrame')
        self._setup_component(**kwargs)
        self._bind_events()

    def _setup_component(self, **kwargs):
        """Setup component structure (override in subclasses)

        Args:
            **kwargs: Component-specific configuration
        """
        pass

    def _bind_events(self):
        """Bind component events (override in subclasses)"""
        pass

    def pack(self, **kwargs):
        """Pack the component frame

        Args:
            **kwargs: Pack options
        """
        self.frame.pack(**kwargs)
        return self

    def grid(self, **kwargs):
        """Grid the component frame

        Args:
            **kwargs: Grid options
        """
        self.frame.grid(**kwargs)
        return self

    def place(self, **kwargs):
        """Place the component frame

        Args:
            **kwargs: Place options
        """
        self.frame.place(**kwargs)
        return self

    def destroy(self):
        """Destroy the component"""
        self.frame.destroy()

    def configure(self, **kwargs):
        """Configure component options

        Args:
            **kwargs: Configuration options
        """
        pass


class FluentButton(FluentComponent):
    """Fluent Design button component

    Supports multiple visual variants:
    - primary: Filled with accent color
    - secondary: Outlined with neutral color
    - accent: Outlined with accent color
    - subtle: Transparent background

    Features:
    - Icon support
    - Loading state
    - Disabled state
    - Click callbacks

    Example:
        button = FluentButton(parent, text="Click Me", variant="primary")
        button.on_click = lambda: print("Clicked!")
        button.pack(padx=10, pady=5)
    """

    def __init__(self, parent: tk.Widget, text: str = "",
                 variant: str = "primary", icon: str = "",
                 command: Optional[Callable] = None, **kwargs):
        """Initialize Fluent button

        Args:
            parent: Parent widget
            text: Button text
            variant: Visual variant (primary, secondary, accent, subtle)
            icon: Icon text/emoji to display before text
            command: Click callback function
            **kwargs: Additional ttk.Button options
        """
        self.text = text
        self.variant = variant
        self.icon = icon
        self.command = command
        self._is_loading = False

        super().__init__(parent, **kwargs)

    def _setup_component(self, **kwargs):
        """Setup button structure"""
        # Determine button style based on variant
        style_map = {
            'primary': 'Primary.TButton',
            'secondary': 'Secondary.TButton',
            'accent': 'Accent.TButton',
            'subtle': 'Subtle.TButton',
        }
        button_style = style_map.get(self.variant, 'Primary.TButton')

        # Create button text with icon
        display_text = f"{self.icon} {self.text}".strip()

        # Create button
        self.button = ttk.Button(
            self.frame,
            text=display_text,
            command=self._handle_click,
            style=button_style,
            **kwargs
        )
        self.button.pack(fill='both', expand=True)

    def _bind_events(self):
        """Bind button events"""
        # Add hover effect simulation
        self.button.bind('<Enter>', self._on_enter)
        self.button.bind('<Leave>', self._on_leave)

    def _on_enter(self, event):
        """Handle mouse enter"""
        if not self._is_loading and str(self.button['state']) != 'disabled':
            self.button.state(['active'])

    def _on_leave(self, event):
        """Handle mouse leave"""
        if not self._is_loading:
            self.button.state(['!active'])

    def _handle_click(self):
        """Handle button click"""
        if not self._is_loading and self.command:
            self.command()

    def set_loading(self, loading: bool):
        """Set button loading state

        Args:
            loading: True to show loading state
        """
        self._is_loading = loading
        if loading:
            self._original_text = self.button['text']
            self.button.configure(text=f"⏳ {self._original_text}", state='disabled')
        else:
            if hasattr(self, '_original_text'):
                self.button.configure(text=self._original_text, state='normal')

    def set_enabled(self, enabled: bool):
        """Enable or disable button

        Args:
            enabled: True to enable, False to disable
        """
        self.button.configure(state='normal' if enabled else 'disabled')

    @property
    def on_click(self):
        """Get click callback"""
        return self.command

    @on_click.setter
    def on_click(self, callback: Callable):
        """Set click callback

        Args:
            callback: Function to call on click
        """
        self.command = callback
        self.button.configure(command=self._handle_click)


class FluentCard(FluentComponent):
    """Fluent Design card container

    A container with elevated styling, perfect for grouping related content.

    Features:
    - Elevation levels (layer1-4)
    - Optional header with title
    - Optional footer for actions
    - Scrollable body content

    Example:
        card = FluentCard(parent, title="My Card", elevation=1)
        content = ttk.Label(card.body, text="Card content here")
        content.pack(padx=10, pady=10)
        card.pack(padx=20, pady=10, fill='both', expand=True)
    """

    def __init__(self, parent: tk.Widget, title: str = "",
                 elevation: int = 1, padding: int = None, **kwargs):
        """Initialize Fluent card

        Args:
            parent: Parent widget
            title: Optional card title
            elevation: Elevation level (0-4)
            padding: Internal padding (default: FluentTheme.SPACING['lg'])
            **kwargs: Additional options
        """
        self.title = title
        self.elevation = max(0, min(4, elevation))
        self.padding = padding if padding is not None else FluentTheme.SPACING['lg']

        super().__init__(parent, **kwargs)

    def _setup_component(self, **kwargs):
        """Setup card structure with rounded appearance"""
        # Configure card frame with elevation
        bg_color = FluentTheme.get_elevation_color(self.elevation)
        self.frame.configure(style='FluentCard.TFrame')

        # Simulate BizLink-style soft shadow (Tkinter limitation)
        # BizLink uses very subtle, soft shadows: 0 2px 6px rgba(0,0,0,0.06)
        # We simulate with extremely subtle border
        shadow_frame = tk.Frame(
            self.frame,
            bg='#F0F0F0',  # Extremely subtle shadow simulation
        )
        shadow_frame.pack(fill='both', expand=True, padx=0, pady=0)

        # Card container - pure white like BizLink
        self.card_container = tk.Frame(
            shadow_frame,
            bg=bg_color,
            highlightbackground='#E8E8E8',  # Very light border
            highlightthickness=1
        )
        self.card_container.pack(fill='both', expand=True, padx=1, pady=2)  # More vertical offset for shadow effect

        # Header (optional)
        if self.title:
            self.header = tk.Frame(
                self.card_container,
                bg=bg_color,
                height=FluentTheme.SPACING['huge']
            )
            self.header.pack(fill='x', padx=self.padding, pady=(self.padding, 0))
            self.header.pack_propagate(False)

            # BizLink-style card title: clean, semi-bold, ~14-16px
            self.title_label = tk.Label(
                self.header,
                text=self.title,
                font=('Segoe UI', 15, 'bold'),  # BizLink card title
                fg=FluentTheme.NEUTRAL['gray160'],
                bg=bg_color
            )
            self.title_label.pack(side='left', anchor='w')

        # Body (scrollable content area)
        self.body = tk.Frame(
            self.card_container,
            bg=bg_color
        )
        self.body.pack(fill='both', expand=True, padx=self.padding, pady=self.padding)

        # Footer (optional, created on demand)
        self.footer = None

    def add_header_action(self, text: str, command: Callable):
        """Add an action button to the card header

        Args:
            text: Button text
            command: Click callback

        Returns:
            FluentButton instance
        """
        if not self.title:
            # Create header if it doesn't exist
            bg_color = FluentTheme.get_elevation_color(self.elevation)
            self.header = tk.Frame(
                self.card_container,
                bg=bg_color,
                height=FluentTheme.SPACING['huge']
            )
            self.header.pack(fill='x', padx=self.padding, pady=(self.padding, 0), before=self.body)
            self.header.pack_propagate(False)

        action_btn = FluentButton(self.header, text=text, variant='subtle', command=command)
        action_btn.pack(side='right', padx=FluentTheme.SPACING['xs'])
        return action_btn

    def add_footer(self):
        """Add a footer section to the card

        Returns:
            Footer frame for adding actions
        """
        if not self.footer:
            bg_color = FluentTheme.get_elevation_color(self.elevation)
            self.footer = tk.Frame(
                self.card_container,
                bg=bg_color,
                height=FluentTheme.SPACING['huge']
            )
            self.footer.pack(fill='x', padx=self.padding, pady=(0, self.padding))
            self.footer.pack_propagate(False)

        return self.footer


class FluentInput(FluentComponent):
    """Fluent Design text input component

    Features:
    - Floating label animation
    - Error/success states with colored borders
    - Inline validation feedback
    - Helper text support
    - Icon support

    Example:
        input_field = FluentInput(parent, label="Email", required=True)
        input_field.on_change = lambda val: validate_email(val)
        input_field.pack(padx=20, pady=10, fill='x')
    """

    def __init__(self, parent: tk.Widget, label: str = "",
                 placeholder: str = "", required: bool = False,
                 validation: Optional[Callable[[str], tuple[bool, str]]] = None,
                 **kwargs):
        """Initialize Fluent input

        Args:
            parent: Parent widget
            label: Input label
            placeholder: Placeholder text
            required: Whether field is required
            validation: Validation function (value) -> (is_valid, error_message)
            **kwargs: Additional Entry options
        """
        self.label_text = label
        self.placeholder = placeholder
        self.required = required
        self.validation = validation
        self._is_focused = False

        super().__init__(parent, **kwargs)

    def _setup_component(self, **kwargs):
        """Setup input structure"""
        # Label
        label_frame = ttk.Frame(self.frame)
        label_frame.pack(fill='x', pady=(0, FluentTheme.SPACING['xs']))

        if self.label_text:
            self.label = ttk.Label(
                label_frame,
                text=self.label_text,
                style='BodyStrong.TLabel'
            )
            self.label.pack(side='left')

            if self.required:
                required_label = ttk.Label(
                    label_frame,
                    text=" *",
                    foreground=FluentTheme.SEMANTIC['error']
                )
                required_label.pack(side='left')

        # Entry field
        self.entry = ttk.Entry(
            self.frame,
            style='Fluent.TEntry',
            **kwargs
        )
        self.entry.pack(fill='x')

        # Set placeholder
        if self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.configure(foreground=FluentTheme.NEUTRAL['gray90'])

        # Helper/error text
        self.helper_label = ttk.Label(
            self.frame,
            text="",
            style='Caption.TLabel',
            foreground=FluentTheme.NEUTRAL['gray110']
        )
        self.helper_label.pack(fill='x', pady=(FluentTheme.SPACING['xs'], 0))

        # Validation state
        self._validation_state = None  # None, 'error', 'success'

    def _bind_events(self):
        """Bind input events"""
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<KeyRelease>', self._on_key_release)

    def _on_focus_in(self, event):
        """Handle focus in"""
        self._is_focused = True

        # Clear placeholder
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(foreground=FluentTheme.NEUTRAL['gray160'])

    def _on_focus_out(self, event):
        """Handle focus out"""
        self._is_focused = False

        # Restore placeholder if empty
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.configure(foreground=FluentTheme.NEUTRAL['gray90'])

        # Validate on blur
        self._validate()

    def _on_key_release(self, event):
        """Handle key release"""
        if hasattr(self, 'on_change') and self.on_change:
            value = self.get_value()
            self.on_change(value)

    def _validate(self):
        """Validate input value"""
        value = self.get_value()

        # Check required
        if self.required and not value:
            self._set_error("This field is required")
            return False

        # Run custom validation
        if self.validation and value:
            is_valid, error_message = self.validation(value)
            if not is_valid:
                self._set_error(error_message)
                return False

        # Clear error if valid
        self._clear_validation()
        return True

    def _set_error(self, message: str):
        """Set error state

        Args:
            message: Error message to display
        """
        self._validation_state = 'error'
        self.helper_label.configure(
            text=message,
            foreground=FluentTheme.SEMANTIC['error']
        )
        # Note: Tkinter ttk.Entry doesn't support easy border color change
        # Would need custom styling or Canvas-based implementation

    def _clear_validation(self):
        """Clear validation state"""
        self._validation_state = None
        self.helper_label.configure(text="")

    def set_helper_text(self, text: str):
        """Set helper text

        Args:
            text: Helper text to display
        """
        if self._validation_state is None:
            self.helper_label.configure(
                text=text,
                foreground=FluentTheme.NEUTRAL['gray110']
            )

    def get_value(self) -> str:
        """Get input value

        Returns:
            Current input value (empty string if placeholder is shown)
        """
        value = self.entry.get()
        return "" if value == self.placeholder else value

    def set_value(self, value: str):
        """Set input value

        Args:
            value: Value to set
        """
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        self.entry.configure(foreground=FluentTheme.NEUTRAL['gray160'])

    @property
    def on_change(self) -> Optional[Callable]:
        """Get change callback"""
        return getattr(self, '_on_change_callback', None)

    @on_change.setter
    def on_change(self, callback: Callable[[str], None]):
        """Set change callback

        Args:
            callback: Function to call when value changes
        """
        self._on_change_callback = callback


class FluentComboBox(FluentComponent):
    """Fluent Design combobox/dropdown component

    Features:
    - Clean dropdown styling
    - Readonly or editable modes
    - Custom item styling
    - Change callbacks

    Example:
        combo = FluentComboBox(parent, label="Choose option",
                              values=["Option 1", "Option 2", "Option 3"])
        combo.on_change = lambda val: print(f"Selected: {val}")
        combo.pack(padx=20, pady=10, fill='x')
    """

    def __init__(self, parent: tk.Widget, label: str = "",
                 values: list = None, readonly: bool = True,
                 default: str = "", **kwargs):
        """Initialize Fluent combobox

        Args:
            parent: Parent widget
            label: Combobox label
            values: List of options
            readonly: Whether combobox is readonly
            default: Default selected value
            **kwargs: Additional Combobox options
        """
        self.label_text = label
        self.values = values or []
        self.readonly = readonly
        self.default = default

        super().__init__(parent, **kwargs)

    def _setup_component(self, **kwargs):
        """Setup combobox structure"""
        # Label
        if self.label_text:
            self.label = ttk.Label(
                self.frame,
                text=self.label_text,
                style='BodyStrong.TLabel'
            )
            self.label.pack(fill='x', pady=(0, FluentTheme.SPACING['xs']))

        # Combobox
        self.var = tk.StringVar(value=self.default)
        self.combobox = ttk.Combobox(
            self.frame,
            textvariable=self.var,
            values=self.values,
            state='readonly' if self.readonly else 'normal',
            style='Fluent.TCombobox',
            **kwargs
        )
        self.combobox.pack(fill='x')

    def _bind_events(self):
        """Bind combobox events"""
        self.combobox.bind('<<ComboboxSelected>>', self._on_select)

    def _on_select(self, event):
        """Handle selection change"""
        if hasattr(self, 'on_change') and self.on_change:
            self.on_change(self.get_value())

    def get_value(self) -> str:
        """Get selected value

        Returns:
            Currently selected value
        """
        return self.var.get()

    def set_value(self, value: str):
        """Set selected value

        Args:
            value: Value to select
        """
        self.var.set(value)

    def set_values(self, values: list):
        """Update available values

        Args:
            values: New list of values
        """
        self.values = values
        self.combobox.configure(values=values)

    @property
    def on_change(self) -> Optional[Callable]:
        """Get change callback"""
        return getattr(self, '_on_change_callback', None)

    @on_change.setter
    def on_change(self, callback: Callable[[str], None]):
        """Set change callback

        Args:
            callback: Function to call when selection changes
        """
        self._on_change_callback = callback
