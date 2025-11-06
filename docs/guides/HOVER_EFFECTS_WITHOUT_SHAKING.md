# How to Implement Hover Effects Without Layout Shaking

## The Problem

When implementing hover effects in Tkinter, it's common to encounter layout instability where widgets "shake" or "jitter" when the mouse hovers over them. This happens when hover effects change properties that affect layout dimensions.

### Common Causes of Shaking

1. **Changing `relief` property**: `relief='flat'` → `relief='raised'` adds implicit borders
2. **Changing `borderwidth`**: Adding/removing border pixels causes layout reflow
3. **Changing `highlightthickness`**: Adding border space shifts widget position
4. **Changing font properties**: Bold fonts are wider, causing text reflow
5. **Changing padding**: Additional padding expands widget size

## ❌ Bad Pattern: Direct Relief Changes

```python
# DON'T DO THIS - causes shaking
event_frame = tk.Frame(parent, bg='blue', relief='flat')
event_frame.pack(fill='x')

def on_enter(e):
    event_frame.config(relief='raised', borderwidth=2)  # Adds space!

def on_leave(e):
    event_frame.config(relief='flat')  # Removes space!

event_frame.bind("<Enter>", on_enter)
event_frame.bind("<Leave>", on_leave)
```

**Why it shakes**:
- `relief='raised'` with `borderwidth=2` adds 2 pixels of border space
- Layout manager recalculates widget positions
- Adjacent widgets shift to accommodate the new space
- Visual "jump" or "jitter" occurs

## ❌ Bad Pattern: Changing Border Thickness

```python
# DON'T DO THIS - causes shaking
day_frame = tk.Frame(parent, highlightthickness=1, highlightbackground='gray')
day_frame.grid(row=0, column=0)

def on_enter(e):
    day_frame.config(highlightthickness=2)  # Layout change!

def on_leave(e):
    day_frame.config(highlightthickness=1)

day_frame.bind("<Enter>", on_enter)
day_frame.bind("<Leave>", on_leave)
```

**Why it shakes**:
- Changing `highlightthickness` from 1 to 2 adds 1 pixel all around (4px total)
- Grid layout recalculates cell sizes
- Entire row/column may shift
- Ripple effect across the UI

## ✅ Good Pattern: Pre-Allocated Border Space

The solution is to **always allocate border space** and only change the **color**, never the **thickness**.

### Implementation

```python
# Container with FIXED border space
event_container = tk.Frame(
    parent,
    bg=parent['bg'],                    # Match parent background
    highlightthickness=2,               # Fixed border size
    highlightbackground=parent['bg']    # Initially invisible
)
event_container.pack(fill='x', pady=3, padx=2)

# Inner frame for actual content
event_frame = tk.Frame(
    event_container,
    bg='#4285f4',
    relief='flat',
    cursor="hand2"
)
event_frame.pack(fill='both', expand=True)

# Content widgets
label = tk.Label(event_frame, text="Event Title", bg='#4285f4', fg='white')
label.pack()

# Hover effect - ONLY change color, NOT size
def on_enter(e):
    event_container.config(highlightbackground='white')  # Show border

def on_leave(e):
    event_container.config(highlightbackground=parent['bg'])  # Hide border

# Bind to all widgets for smooth interaction
for widget in [event_container, event_frame, label]:
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
```

### Why This Works

1. **Border space pre-allocated**: `highlightthickness=2` always reserves 2 pixels
2. **No layout changes**: Border size never changes, only color
3. **Smooth transition**: Color change is instant, no reflow needed
4. **Two-layer structure**:
   - Outer container handles border (invisible until hover)
   - Inner frame holds content (never changes size)

## 🎨 Visual Comparison

### Before (Shaking)
```
Normal state:     Hover state:
┌──────────┐     ┌─┬────────┬─┐   ← Border added (2px)
│ Content  │     │ │Content │ │   ← Content shifts
└──────────┘     └─┴────────┴─┘   ← Adjacent widgets shift down
```

### After (Stable)
```
Normal state:          Hover state:
┌───────────┐         ┌───────────┐   ← Same size
│┌─────────┐│         │┌─────────┐│   ← Same position
││ Content ││         ││ Content ││   ← No shift
│└─────────┘│         │└─────────┘│
└───────────┘         └───────────┘
    ↑                      ↑
Invisible border      Visible white border
```

## 📋 Complete Examples

### Example 1: Event Card in Calendar

```python
def create_event_widget(parent, event_data):
    """Create event widget with stable hover effect"""

    # Outer container - holds fixed border space
    container = tk.Frame(
        parent,
        bg=parent['bg'],           # Match parent (e.g., '#fafbfc')
        highlightthickness=1,      # 1px border space
        highlightbackground=parent['bg']  # Initially invisible
    )
    container.pack(fill='x', pady=1, padx=1)

    # Inner frame - holds content
    content = tk.Frame(
        container,
        bg='#4285f4',              # Google Blue
        relief='flat',
        cursor="hand2"
    )
    content.pack(fill='both', expand=True)

    # Content widgets
    time_label = tk.Label(
        content,
        text="09:00",
        font=('Segoe UI', 8),
        bg='#4285f4',
        fg='white',
        padx=4,
        pady=2
    )
    time_label.pack(side='left')

    title_label = tk.Label(
        content,
        text="Team Meeting",
        font=('Segoe UI', 8),
        bg='#4285f4',
        fg='white',
        padx=4,
        pady=2
    )
    title_label.pack(side='left')

    # Hover handlers
    def on_enter(e):
        container.config(highlightbackground='white')

    def on_leave(e):
        container.config(highlightbackground=parent['bg'])

    # Bind to all widgets
    for widget in [container, content, time_label, title_label]:
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    return container
```

### Example 2: Day Cell in Month View

```python
def create_day_cell(parent, date, events):
    """Create day cell with stable layout"""

    # Day frame with FIXED height
    day_frame = tk.Frame(
        parent,
        bg='#fafbfc',
        relief='flat',
        highlightbackground='#e8eaed',  # Light gray
        highlightthickness=1,            # Fixed border
        height=120                       # Fixed height
    )
    day_frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
    day_frame.grid_propagate(False)  # Don't resize based on content

    # Hover effect - only change color
    def on_enter(e):
        day_frame.config(highlightbackground='#1a73e8')  # Blue

    def on_leave(e):
        day_frame.config(highlightbackground='#e8eaed')  # Gray

    day_frame.bind("<Enter>", on_enter)
    day_frame.bind("<Leave>", on_leave)

    # Add content (day number, events, etc.)
    # ...

    return day_frame
```

## 🔧 Technical Details

### Why `highlightbackground` Instead of `borderwidth`?

| Property | Changes Layout? | Visible When? | Use Case |
|----------|----------------|---------------|----------|
| `highlightbackground` | ❌ No | Always (if thickness > 0) | ✅ Best for hover |
| `highlightthickness` | ✅ Yes | When > 0 | ❌ Don't change |
| `borderwidth` | ✅ Yes | With relief | ❌ Don't change |
| `relief` | ✅ Yes | When not 'flat' | ❌ Don't change |

### Color Matching for Invisible Borders

```python
# Container matches parent background
parent_bg = parent['bg']  # e.g., '#fafbfc'

container = tk.Frame(
    parent,
    bg=parent_bg,                  # Same as parent
    highlightthickness=2,          # Fixed space
    highlightbackground=parent_bg  # Invisible (matches background)
)
```

**Result**: Border exists but is invisible because it's the same color as the background.

## 🎯 Checklist for Stable Hover Effects

- [ ] Use two-layer structure (container + content)
- [ ] Pre-allocate border space in container (`highlightthickness`)
- [ ] Match container border color to parent background (invisible by default)
- [ ] Only change `highlightbackground` color on hover
- [ ] Never change `highlightthickness`, `borderwidth`, or `relief` on hover
- [ ] Use fixed heights where possible (`height=X`, `grid_propagate(False)`)
- [ ] Bind hover events to all child widgets
- [ ] Test with rapid mouse movement

## 🚫 Properties to NEVER Change on Hover

| Property | Why Not | Alternative |
|----------|---------|-------------|
| `highlightthickness` | Adds/removes space | Pre-allocate, change color only |
| `borderwidth` | Changes relief size | Use highlight instead |
| `relief` | Adds implicit borders | Use flat + highlight |
| `width`/`height` | Obvious size change | Fixed size with `propagate(False)` |
| `padx`/`pady` | Changes spacing | Use fixed padding |
| Font weight to bold | Text width changes | Use same weight or minimal change |

## ✅ Properties Safe to Change on Hover

| Property | Effect | Example |
|----------|--------|---------|
| `highlightbackground` | Border color | Gray → Blue |
| `bg` (background) | Fill color | Light → Dark |
| `fg` (foreground) | Text color | Black → White |
| `cursor` | Mouse cursor | 'arrow' → 'hand2' |

## 📐 Layout Stability Best Practices

### 1. Fixed Dimensions
```python
frame = tk.Frame(parent, height=120, width=200)
frame.pack_propagate(False)  # or grid_propagate(False)
```

### 2. Pre-Allocated Space
```python
# Always reserve border space
frame = tk.Frame(parent, highlightthickness=2, ...)
```

### 3. Color-Only Changes
```python
def on_enter(e):
    widget.config(highlightbackground='blue')  # ✅ Color only
    # widget.config(highlightthickness=2)      # ❌ Don't do this
```

### 4. Uniform Sizing
```python
# Use uniform option for consistent column widths
parent.columnconfigure(0, weight=1, uniform="day")
parent.columnconfigure(1, weight=1, uniform="day")
```

## 🐛 Debugging Shaking Issues

If you still see shaking, check:

1. **Is anything changing size on hover?**
   ```python
   # Add print statements
   def on_enter(e):
       print(f"Before: {widget.winfo_width()}x{widget.winfo_height()}")
       widget.config(highlightbackground='blue')
       widget.update()
       print(f"After: {widget.winfo_width()}x{widget.winfo_height()}")
   ```

2. **Are child widgets causing reflow?**
   - Check if labels change from normal to bold
   - Check if text wraps differently
   - Use fixed `width` on labels

3. **Is grid/pack recalculating?**
   - Use `propagate(False)` on parent
   - Set fixed dimensions
   - Use `uniform` for columns/rows

4. **Are multiple widgets competing?**
   - Ensure only color changes, not sizes
   - Check adjacent widgets aren't affected

## 📚 Real-World Example: Google Calendar Clone

This pattern was used to fix shaking in an AI Schedule Agent calendar UI:

**Problem**: Event widgets in month view would shake when hovering.

**Solution**:
```python
# Before (shaking)
event_frame = tk.Frame(parent, bg=color, relief='flat')
event_frame.pack(fill='x', pady=1)

def on_enter(e):
    event_frame.config(relief='raised', borderwidth=2)  # ❌ Shakes!

# After (stable)
event_container = tk.Frame(parent, bg=parent['bg'],
                          highlightthickness=1,
                          highlightbackground=parent['bg'])
event_container.pack(fill='x', pady=1)

event_frame = tk.Frame(event_container, bg=color, relief='flat')
event_frame.pack(fill='both', expand=True)

def on_enter(e):
    event_container.config(highlightbackground='white')  # ✅ Stable!
```

**Result**: Ultra-stable hover effects with clear visual feedback, no layout shift.

---

## 🎓 Key Takeaways

1. **Pre-allocate space** for borders/effects before hover
2. **Only change colors** on hover, never dimensions
3. **Two-layer structure** separates border from content
4. **Fixed sizes** prevent propagation issues
5. **Bind all widgets** for smooth interaction

**Remember**: Layout stability > fancy effects. Users notice jitter more than subtle effects!

---

**Last Updated**: November 6, 2025
**Related**: [CALENDAR_UI_BUG_FIXES.md](CALENDAR_UI_BUG_FIXES.md)
