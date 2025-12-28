# Enterprise Theme Design Guide

A clean, light, enterprise-grade UI theme for the AI Schedule Agent application.

## Design Philosophy

The Enterprise Theme follows modern UI/UX best practices with a focus on:

- **Clean & Light**: Soft white backgrounds with subtle gray accents
- **Professional**: Enterprise-grade aesthetics suitable for business environments
- **Readable**: Clear typography hierarchy with modern sans-serif fonts
- **Minimal**: Flat design with soft elevation, no heavy gradients or strong contrasts
- **Focused Interaction**: Blue used sparingly only for focus, selection, and interaction states

---

## Color System

### Background Colors

| Usage | Color | Hex | Description |
|-------|-------|-----|-------------|
| Primary Background | ![](https://via.placeholder.com/20/FAFBFC/FAFBFC) | `#FAFBFC` | Soft white for main areas |
| Card Background | ![](https://via.placeholder.com/20/FFFFFF/FFFFFF) | `#FFFFFF` | Pure white for cards |
| Section Background | ![](https://via.placeholder.com/20/F5F7F9/F5F7F9) | `#F5F7F9` | Light gray for sections |
| Hover State | ![](https://via.placeholder.com/20/F0F3F6/F0F3F6) | `#F0F3F6` | Very subtle hover |

### Border Colors

| Usage | Color | Hex | Description |
|-------|-------|-----|-------------|
| Default Border | ![](https://via.placeholder.com/20/E4E7EB/E4E7EB) | `#E4E7EB` | Soft gray borders |
| Light Border | ![](https://via.placeholder.com/20/F0F2F5/F0F2F5) | `#F0F2F5` | Very light borders |
| Focus Border | ![](https://via.placeholder.com/20/3B82F6/3B82F6) | `#3B82F6` | Blue for focus |

### Text Colors

| Usage | Color | Hex | Description |
|-------|-------|-----|-------------|
| Primary Text | ![](https://via.placeholder.com/20/1E293B/1E293B) | `#1E293B` | Dark slate for main text |
| Secondary Text | ![](https://via.placeholder.com/20/64748B/64748B) | `#64748B` | Medium slate for secondary |
| Tertiary Text | ![](https://via.placeholder.com/20/94A3B8/94A3B8) | `#94A3B8` | Light slate for subtle text |

### Blue - Interaction Color

| Usage | Color | Hex | When to Use |
|-------|-------|-----|-------------|
| Primary Blue | ![](https://via.placeholder.com/20/3B82F6/3B82F6) | `#3B82F6` | Focus states, primary buttons, selections |
| Hover Blue | ![](https://via.placeholder.com/20/2563EB/2563EB) | `#2563EB` | Button hover states |
| Light Blue | ![](https://via.placeholder.com/20/DBEAFE/DBEAFE) | `#DBEAFE` | Blue backgrounds |

**Important**: Blue should be used **sparingly** - only for:
- Input field focus borders
- Primary action buttons
- Selected states
- Interactive hover states

### Event Type Colors

| Event Type | Color | Hex |
|------------|-------|-----|
| Meeting | ![](https://via.placeholder.com/20/8B5CF6/8B5CF6) | `#8B5CF6` Purple |
| Focus | ![](https://via.placeholder.com/20/3B82F6/3B82F6) | `#3B82F6` Blue |
| Break | ![](https://via.placeholder.com/20/10B981/10B981) | `#10B981` Green |
| Personal | ![](https://via.placeholder.com/20/F59E0B/F59E0B) | `#F59E0B` Amber |
| Task | ![](https://via.placeholder.com/20/EC4899/EC4899) | `#EC4899` Pink |
| Other | ![](https://via.placeholder.com/20/06B6D4/06B6D4) | `#06B6D4` Cyan |

---

## Typography

### Font Family Priority

1. **Inter** - Modern geometric sans-serif (preferred)
2. **SF Pro Display** - Apple system font
3. **Segoe UI** - Windows system font
4. **Arial** - Universal fallback

### Type Scale

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| Display | 32pt | Bold | Page titles |
| Heading 1 | 24pt | Bold | Section headers |
| Heading 2 | 20pt | Bold | Subsection headers |
| Heading 3 | 16pt | Bold | Card headers |
| Body Large | 15pt | Regular | Emphasized body text |
| Body | 14pt | Regular | Default text |
| Body Small | 13pt | Regular | De-emphasized text |
| Caption | 12pt | Regular | Helper text, labels |
| Micro | 11pt | Regular | Badges, tiny text |

### Typography Hierarchy Example

```
Display Text (32pt Bold)
  Heading 1 (24pt Bold)
    Heading 2 (20pt Bold)
      Heading 3 (16pt Bold)
        Body Large (15pt)
        Body Text (14pt)
        Body Small (13pt)
        Caption (12pt)
```

### Font Weight Guidelines

- Use **regular** (400) for most body text
- Use **bold** (700) for headings and emphasis
- Avoid overuse of bold - restrained weights create professional appearance

---

## Spacing System

Based on **4px** base unit for consistency:

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Tight spacing, small gaps |
| `sm` | 8px | Input padding, small margins |
| `md` | 12px | Medium spacing |
| `lg` | 16px | Card padding, standard gaps |
| `xl` | 20px | Button padding horizontal |
| `xxl` | 24px | Large margins |
| `3xl` | 32px | Section spacing |
| `4xl` | 40px | Large section gaps |
| `5xl` | 48px | Extra large spacing |
| `6xl` | 64px | Maximum spacing |

---

## Border Radius

Rounded corners for friendly, modern appearance:

| Token | Value | Usage |
|-------|-------|-------|
| `sm` | 6px | Input fields |
| `md` | 8px | Buttons |
| `lg` | 12px | Cards |
| `xl` | 16px | Large cards |
| `full` | 9999px | Pills, circular avatars |

---

## Shadows

Gentle shadows for soft elevation without harsh contrast:

| Shadow | CSS Equivalent | Usage |
|--------|----------------|-------|
| Subtle | `0 1px 2px rgba(15,23,42,0.03)` | Minimal elevation |
| Small | `0 2px 4px rgba(15,23,42,0.05)` | Card elevation |
| Medium | `0 4px 6px rgba(15,23,42,0.08)` | Hover states |
| Large | `0 8px 16px rgba(15,23,42,0.12)` | Modals, popovers |
| Focus | `0 0 0 3px rgba(59,130,246,0.15)` | Focus ring |

---

## Component Styles

### Buttons

#### Primary Button
- **Background**: Blue (`#3B82F6`)
- **Text**: White
- **Padding**: 16px horizontal, 8px vertical
- **Border Radius**: 8px
- **Border**: None
- **Hover**: Darker blue (`#2563EB`)

```python
btn = EnterpriseTheme.create_button(parent, "Submit", variant='primary')
```

#### Secondary Button
- **Background**: White
- **Text**: Dark slate
- **Border**: 1px solid gray (`#E4E7EB`)
- **Padding**: 16px horizontal, 8px vertical
- **Border Radius**: 8px
- **Hover**: Light gray background

```python
btn = EnterpriseTheme.create_button(parent, "Cancel", variant='secondary')
```

#### Subtle Button
- **Background**: Transparent
- **Text**: Medium slate
- **Border**: None
- **Padding**: 12px horizontal, 8px vertical
- **Hover**: Light gray background

```python
btn = EnterpriseTheme.create_button(parent, "More", variant='subtle')
```

### Input Fields

- **Background**: White
- **Border**: 1px solid gray (`#E4E7EB`)
- **Border Radius**: 6px (rounded)
- **Padding**: 12px horizontal, 8px vertical
- **Font Size**: 14pt
- **Focus State**: Blue border (`#3B82F6`) with subtle shadow

```python
frame, label, entry = EnterpriseTheme.create_input_frame(parent, "Email Address")
```

### Cards

- **Background**: Pure white
- **Border**: 1px solid light gray (`#E4E7EB`)
- **Border Radius**: 12px
- **Shadow**: Subtle (small card shadow)
- **Padding**: 16px

```python
card = EnterpriseTheme.create_card_frame(parent, padding=16)
# Add content to card.content
tk.Label(card.content, text="Card content").pack()
```

---

## Visual Design Principles

### 1. Minimal Iconography

Use thin-stroke icons (1-2px stroke width) sparingly:
- Line icons preferred over filled icons
- Icons should be subtle, not dominating
- Use Unicode symbols when possible: ⚙️ ✓ ✕ ⓘ ⚠️

### 2. Flat Design with Soft Elevation

- No gradients on buttons or cards
- Soft shadows for depth (not hard drop shadows)
- Elevation created through subtle layering
- Maximum 3 elevation levels on screen at once

### 3. Blue for Interaction Only

Blue is reserved for:
- Focus rings on input fields
- Primary action buttons
- Selected items
- Active/hover states

Blue should NOT be used for:
- Regular text
- Decorative elements
- Section backgrounds
- Icons (unless interactive)

### 4. Clear Visual Separation

Achieve separation through:
- Subtle borders (`#E4E7EB`)
- Gentle shadows
- Slight background color changes
- Adequate whitespace

Avoid:
- Heavy borders
- Strong contrast
- Dark dividers

### 5. Restrained Typography

- Mostly regular weight (400)
- Bold only for headings and strong emphasis
- Clear size hierarchy
- Generous line height (1.5 for body text)

---

## Usage Examples

### Basic Application Setup

```python
import tkinter as tk
from tkinter import ttk
from ai_schedule_agent.ui.enterprise_theme import EnterpriseTheme

# Create root window
root = tk.Tk()
root.title("AI Schedule Agent")
root.geometry("1200x800")

# Apply enterprise theme
style = ttk.Style()
EnterpriseTheme.configure_styles(style, root)

# Main container
main_frame = tk.Frame(root, bg=EnterpriseTheme.BACKGROUND['primary'])
main_frame.pack(fill='both', expand=True, padx=20, pady=20)

# Create a card
card = EnterpriseTheme.create_card_frame(main_frame)
card.pack(fill='x', pady=10)

# Add title to card
title = tk.Label(
    card.content,
    text="Quick Schedule",
    bg=EnterpriseTheme.BACKGROUND['secondary'],
    fg=EnterpriseTheme.TEXT['primary'],
    font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['heading-2'], 'bold')
)
title.pack(anchor='w', pady=(0, 12))

# Add input field
input_frame, label, entry = EnterpriseTheme.create_input_frame(
    card.content,
    "Event Description"
)
input_frame.pack(fill='x', pady=8)

# Add buttons
btn_frame = tk.Frame(card.content, bg=EnterpriseTheme.BACKGROUND['secondary'])
btn_frame.pack(fill='x', pady=(12, 0))

submit_btn = EnterpriseTheme.create_button(btn_frame, "Schedule Event", variant='primary')
submit_btn.pack(side='left', padx=(0, 8))

cancel_btn = EnterpriseTheme.create_button(btn_frame, "Cancel", variant='secondary')
cancel_btn.pack(side='left')

root.mainloop()
```

### Creating a Form

```python
# Form container
form_card = EnterpriseTheme.create_card_frame(parent)
form_card.pack(fill='x', pady=10)

# Title
title = tk.Label(
    form_card.content,
    text="Event Details",
    bg=EnterpriseTheme.BACKGROUND['secondary'],
    fg=EnterpriseTheme.TEXT['primary'],
    font=(EnterpriseTheme.get_font_family(), EnterpriseTheme.TYPE_SCALE['heading-2'], 'bold')
)
title.pack(anchor='w', pady=(0, 16))

# Input fields
fields = ['Title', 'Description', 'Location', 'Date', 'Time']
for field in fields:
    frame, label, entry = EnterpriseTheme.create_input_frame(form_card.content, field)
    frame.pack(fill='x', pady=8)

# Submit button
btn_container = tk.Frame(form_card.content, bg=EnterpriseTheme.BACKGROUND['secondary'])
btn_container.pack(fill='x', pady=(16, 0))

submit = EnterpriseTheme.create_button(btn_container, "Create Event", variant='primary')
submit.pack(side='right')
```

---

## Migration from Existing Themes

### From FluentTheme

| FluentTheme | EnterpriseTheme |
|-------------|-----------------|
| `FluentCard.TFrame` | `Enterprise.Card.TFrame` |
| `Primary.TButton` | `Enterprise.Primary.TButton` |
| `Fluent.TEntry` | `Enterprise.TEntry` |
| `FluentTheme.NEUTRAL['gray10']` | `EnterpriseTheme.BACKGROUND['primary']` |
| `FluentTheme.get_font_family()` | `EnterpriseTheme.get_font_family()` |

### From ModernTheme

| ModernTheme | EnterpriseTheme |
|-------------|-----------------|
| `Card.TFrame` | `Enterprise.Card.TFrame` |
| `Modern.TButton` | `Enterprise.Primary.TButton` |
| `Modern.TEntry` | `Enterprise.TEntry` |
| `ModernTheme.COLORS['bg_primary']` | `EnterpriseTheme.BACKGROUND['primary']` |

---

## Best Practices

### ✅ Do

- Use consistent spacing from the spacing system
- Apply rounded corners to all interactive elements
- Keep shadows subtle and soft
- Use blue only for interactive states
- Maintain clear typography hierarchy
- Provide adequate whitespace between sections
- Use thin borders for separation

### ❌ Don't

- Don't use heavy shadows or dark borders
- Don't use gradients on UI elements
- Don't overuse bold text
- Don't use blue for decorative purposes
- Don't mix border radius values
- Don't crowd elements together
- Don't use more than 3 font sizes on one screen

---

## Accessibility Considerations

- **Color Contrast**: All text meets WCAG AA standards (4.5:1 for normal text)
- **Focus Indicators**: Blue focus rings are clearly visible
- **Interactive Targets**: Minimum 44x44px touch targets
- **Typography**: 14pt default for readability
- **Spacing**: Adequate space between clickable elements

---

## Theme Preview

The Enterprise Theme provides a clean, professional appearance perfect for business applications:

- **Light & Airy**: Soft backgrounds reduce eye strain
- **Professional**: Suitable for enterprise environments
- **Modern**: Contemporary design patterns
- **Focused**: Blue draws attention to important actions
- **Minimal**: No visual clutter or unnecessary decoration

This theme is ideal for productivity applications, business tools, scheduling systems, and any enterprise-grade software.
