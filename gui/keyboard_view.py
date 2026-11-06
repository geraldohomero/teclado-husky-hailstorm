"""
Interactive 68-Key Keyboard Canvas Widget for Husky Hailstorm.
Provides real-time visualization of keycaps, legends, LED lighting colors,
and supports multi-key selection for remapping and per-key RGB coloring.
"""

import tkinter as tk
from typing import Dict, List, Set, Callable, Optional
from core.keycodes import KEYBOARD_LAYOUT, HID_KEYCODES, CODE_TO_NAME


class KeyboardCanvas(tk.Canvas):
    """
    High-DPI capable interactive canvas rendering the physical TY69SKRGB keyboard layout.
    """
    def __init__(
        self,
        parent,
        width: int = 860,
        height: int = 280,
        on_key_selected: Optional[Callable[[int, dict], None]] = None,
        on_selection_change: Optional[Callable[[List[int]], None]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg="#14151B",
            highlightthickness=0,
            **kwargs
        )
        self.on_key_selected = on_key_selected
        self.on_selection_change = on_selection_change

        self.unit_size: float = 50.0  # Pixels per standard 1U key
        self.key_margin: float = 3.5  # Gap between keys
        self.offset_x: float = 24.0
        self.offset_y: float = 20.0

        self.selected_slots: Set[int] = set()
        self.key_colors: Dict[int, str] = {}
        self.key_remaps: Dict[int, dict] = {}
        self.active_layer: str = "default"  # "default", "fn", "fn1"

        # Initialize default colors (Husky Red / Cyan)
        for k in KEYBOARD_LAYOUT:
            self.key_colors[k['slot']] = "#FF0033"

        # Slot-to-canvas item mapping for fast redraws
        self.slot_items: Dict[int, dict] = {}

        # Drag selection state
        self.drag_start_x: Optional[float] = None
        self.drag_start_y: Optional[float] = None
        self.drag_rect_id: Optional[int] = None

        # Bindings
        self.bind("<Button-1>", self._on_mouse_down)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.bind("<Configure>", self._on_resize)

        self._draw_keyboard()

    def _on_resize(self, event):
        """Dynamically scales layout to fit canvas width."""
        target_width = max(600, event.width)
        # Total layout width is ~16.5 U units
        new_unit = (target_width - 50) / 16.5
        self.unit_size = max(32.0, min(56.0, new_unit))
        self.offset_x = (target_width - (16.5 * self.unit_size)) / 2
        self.offset_y = 15.0
        self._draw_keyboard()

    def _draw_keyboard(self):
        """Draws keyboard body bezel and all 68 keycaps."""
        self.delete("all")
        self.slot_items.clear()

        # Keyboard bezel / case outline
        total_w = 16.5 * self.unit_size
        total_h = 5.25 * self.unit_size
        x0 = self.offset_x - 10
        y0 = self.offset_y - 10
        x1 = x0 + total_w + 20
        y1 = y0 + total_h + 20

        # Bezel base
        self._draw_rounded_rect(x0, y0, x1, y1, radius=12, fill="#1C1E26", outline="#2A2D3A", width=2)
        # Inner plate
        self._draw_rounded_rect(x0 + 4, y0 + 4, x1 - 4, y1 - 4, radius=8, fill="#121318", outline="#1A1C24", width=1)

        # Draw keys
        for key in KEYBOARD_LAYOUT:
            slot = key['slot']
            w_units = key['width']
            kx = self.offset_x + (key['x'] * self.unit_size)
            ky = self.offset_y + (key['y'] * self.unit_size)
            kw = (w_units * self.unit_size) - (self.key_margin * 2)
            kh = self.unit_size - (self.key_margin * 2)

            is_selected = slot in self.selected_slots
            led_color = self.key_colors.get(slot, "#FF0033")

            # Determine key label depending on active layer
            label = key['label']
            sub_label = key.get('fn_label', '')

            if self.active_layer == "fn" and sub_label:
                primary_text = sub_label
                secondary_text = label
            elif slot in self.key_remaps:
                remap_data = self.key_remaps[slot]
                primary_text = remap_data.get('name', label)
                secondary_text = f"[{label}]"
            else:
                primary_text = label
                secondary_text = sub_label

            items = self._draw_keycap(
                slot=slot,
                x=kx + self.key_margin,
                y=ky + self.key_margin,
                w=kw,
                h=kh,
                label=primary_text,
                sub_label=secondary_text,
                led_color=led_color,
                is_selected=is_selected
            )
            self.slot_items[slot] = {
                "bbox": (kx + self.key_margin, ky + self.key_margin, kx + self.key_margin + kw, ky + self.key_margin + kh),
                "items": items,
                "key_data": key
            }

    def _draw_keycap(
        self,
        slot: int,
        x: float,
        y: float,
        w: float,
        h: float,
        label: str,
        sub_label: str,
        led_color: str,
        is_selected: bool
    ) -> List[int]:
        """Renders an individual keycap with backlight glow, cap shading, and legends."""
        ids = []

        # 1. Underglow / LED illumination halo
        glow_id = self._draw_rounded_rect(
            x - 1, y - 1, x + w + 1, y + h + 1,
            radius=6,
            fill=led_color,
            outline=""
        )
        ids.append(glow_id)

        # 2. Keycap body
        cap_fill = "#2B2E3A" if is_selected else "#1F212A"
        cap_border = "#FFFFFF" if is_selected else "#363A4B"
        border_w = 2 if is_selected else 1

        body_id = self._draw_rounded_rect(
            x + 1, y + 1, x + w - 1, y + h - 1,
            radius=5,
            fill=cap_fill,
            outline=cap_border,
            width=border_w
        )
        ids.append(body_id)

        # 3. LED indicator strip at the top of the key
        strip_y1 = y + 3
        strip_y2 = y + 5
        strip_id = self._draw_rounded_rect(
            x + 6, strip_y1, x + w - 6, strip_y2,
            radius=2,
            fill=led_color,
            outline=""
        )
        ids.append(strip_id)

        # 4. Primary Legend Text
        font_size = max(8, int(self.unit_size * 0.22))
        text_color = "#FFFFFF" if is_selected else "#E0E2EC"
        
        # Center-align or adjust for long keys
        txt_y = y + (h * 0.45)
        text_id = self.create_text(
            x + (w / 2),
            txt_y,
            text=label,
            fill=text_color,
            font=("Segoe UI", font_size, "bold"),
            justify=tk.CENTER
        )
        ids.append(text_id)

        # 5. Secondary/FN Legend Text (small in bottom corner)
        if sub_label:
            sub_font_size = max(7, int(font_size * 0.72))
            sub_id = self.create_text(
                x + (w / 2),
                y + (h * 0.78),
                text=sub_label,
                fill="#FF9933" if self.active_layer == "fn" else "#7E8398",
                font=("Segoe UI", sub_font_size),
                justify=tk.CENTER
            )
            ids.append(sub_id)

        return ids

    def _draw_rounded_rect(self, x0, y0, x1, y1, radius=6, **kwargs) -> int:
        """Helper to create a smooth polygon simulating a rounded rectangle."""
        points = [
            x0 + radius, y0,
            x1 - radius, y0,
            x1, y0,
            x1, y0 + radius,
            x1, y1 - radius,
            x1, y1,
            x1 - radius, y1,
            x0 + radius, y1,
            x0, y1,
            x0, y1 - radius,
            x0, y0 + radius,
            x0, y0,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _find_slot_at(self, px: float, py: float) -> Optional[int]:
        """Returns slot ID if mouse coordinate is inside a keycap."""
        for slot, data in self.slot_items.items():
            bx0, by0, bx1, by1 = data["bbox"]
            if bx0 <= px <= bx1 and by0 <= py <= by1:
                return slot
        return None

    def _on_mouse_down(self, event):
        slot = self._find_slot_at(event.x, event.y)
        shift_held = bool(event.state & 0x0001) or bool(event.state & 0x0004)  # Shift or Ctrl

        if slot is not None:
            if shift_held:
                if slot in self.selected_slots:
                    self.selected_slots.remove(slot)
                else:
                    self.selected_slots.add(slot)
            else:
                self.selected_slots = {slot}

            self._draw_keyboard()

            if self.on_key_selected:
                key_info = next((k for k in KEYBOARD_LAYOUT if k['slot'] == slot), None)
                if key_info:
                    self.on_key_selected(slot, key_info)

            if self.on_selection_change:
                self.on_selection_change(list(self.selected_slots))
        else:
            # Clicked on empty space: start drag-select box
            if not shift_held:
                self.selected_slots.clear()
                self._draw_keyboard()
                if self.on_selection_change:
                    self.on_selection_change([])

            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def _on_mouse_drag(self, event):
        if self.drag_start_x is not None and self.drag_start_y is not None:
            if self.drag_rect_id:
                self.delete(self.drag_rect_id)
            self.drag_rect_id = self.create_rectangle(
                self.drag_start_x, self.drag_start_y,
                event.x, event.y,
                outline="#00F0FF",
                dash=(3, 3),
                width=1
            )

    def _on_mouse_up(self, event):
        if self.drag_start_x is not None and self.drag_start_y is not None and self.drag_rect_id:
            x_min = min(self.drag_start_x, event.x)
            x_max = max(self.drag_start_x, event.x)
            y_min = min(self.drag_start_y, event.y)
            y_max = max(self.drag_start_y, event.y)

            # Check all keys inside the bounding box
            for slot, data in self.slot_items.items():
                bx0, by0, bx1, by1 = data["bbox"]
                if not (bx1 < x_min or bx0 > x_max or by1 < y_min or by0 > y_max):
                    self.selected_slots.add(slot)

            self.delete(self.drag_rect_id)
            self.drag_rect_id = None
            self.drag_start_x = None
            self.drag_start_y = None

            self._draw_keyboard()
            if self.on_selection_change:
                self.on_selection_change(list(self.selected_slots))

    # --- Public API methods ---

    def select_slots(self, slots: List[int]):
        """Sets the selected slots programmatically."""
        self.selected_slots = set(slots)
        self._draw_keyboard()
        if self.on_selection_change:
            self.on_selection_change(list(self.selected_slots))

    def set_key_color(self, slot: int, hex_color: str):
        """Updates color of a single key."""
        self.key_colors[slot] = hex_color
        self._draw_keyboard()

    def update_all_colors(self, colors: Dict[int, str]):
        """Updates colors for all keys at once."""
        self.key_colors.update(colors)
        self._draw_keyboard()

    def set_layer(self, layer_name: str, remaps: Optional[Dict[int, dict]] = None):
        """Switches layer view (default, fn, fn1) and updates legends."""
        self.active_layer = layer_name.lower()
        if remaps is not None:
            self.key_remaps = remaps
        self._draw_keyboard()
