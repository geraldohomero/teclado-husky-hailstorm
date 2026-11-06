"""
Keycodes and physical matrix layout definition for Husky Hailstorm (TY69SKRGB).
Supports 65% / 68-key layout with ABNT2/ISO and ANSI mappings.
"""

# Standard USB HID Usage IDs for keyboard
HID_KEYCODES = {
    # Letters
    'A': 4, 'B': 5, 'C': 6, 'D': 7, 'E': 8, 'F': 9, 'G': 10, 'H': 11,
    'I': 12, 'J': 13, 'K': 14, 'L': 15, 'M': 16, 'N': 17, 'O': 18, 'P': 19,
    'Q': 20, 'R': 21, 'S': 22, 'T': 23, 'U': 24, 'V': 25, 'W': 26, 'X': 27,
    'Y': 28, 'Z': 29,

    # Numbers (Top row)
    '1!': 30, '2@': 31, '3#': 32, '4$': 33, '5%': 34,
    '6^': 35, '7&': 36, '8*': 37, '9(': 38, '0)': 39,

    # Common controls
    'Enter': 40, 'Esc': 41, 'Back': 42, 'Tab': 43, 'Space': 44,
    '-_': 45, '=+': 46, '[{': 47, ']}': 48, '\\|': 49,
    '#~': 50, '; :': 51, '\' "': 52, '`~': 53, ',<': 54, '.>': 55, '/?': 56,
    'Caps': 57,

    # Function keys
    'F1': 58, 'F2': 59, 'F3': 60, 'F4': 61, 'F5': 62, 'F6': 63,
    'F7': 64, 'F8': 65, 'F9': 66, 'F10': 67, 'F11': 68, 'F12': 69,

    # Navigation & Edit
    'Print': 70, 'ScrollLock': 71, 'Pause': 72, 'Insert': 73,
    'Home': 74, 'PageUp': 75, 'Delete': 76, 'End': 77, 'PageDn': 78,
    'Right': 79, 'Left': 80, 'Down': 81, 'Up': 82,

    # ISO / ABNT Extra key (between Left Shift and Z)
    '\\| (ISO)': 100,

    # Modifiers
    'LCtrl': 224, 'LShift': 225, 'LAlt': 226, 'LWin': 227,
    'RCtrl': 228, 'RShift': 229, 'RAlt': 230, 'RWin': 231,
    'Fn': -10
}

# Reverse lookup: keyCode -> Name
CODE_TO_NAME = {v: k for k, v in HID_KEYCODES.items()}

# Multimedia and System special commands
SPECIAL_ACTIONS = {
    'NONE': 0,
    # Mouse Actions
    'MOUSE_LEFT': 1001,
    'MOUSE_RIGHT': 1002,
    'MOUSE_MIDDLE': 1003,
    'MOUSE_BACK': 1004,
    'MOUSE_FORWARD': 1005,
    'WHEEL_UP': 1006,
    'WHEEL_DOWN': 1007,

    # Multimedia Actions
    'MEDIA_PLAY_PAUSE': 2001,
    'MEDIA_STOP': 2002,
    'MEDIA_PREV': 2003,
    'MEDIA_NEXT': 2004,
    'MEDIA_VOL_UP': 2005,
    'MEDIA_VOL_DOWN': 2006,
    'MEDIA_MUTE': 2007,
    'MEDIA_PLAYER': 2008,

    # System / Productivity Shortcuts
    'SYS_CALCULATOR': 3001,
    'SYS_MY_COMPUTER': 3002,
    'SYS_BROWSER': 3003,
    'SYS_EMAIL': 3004,
    'SYS_SEARCH': 3005,
    'SYS_DESKTOP': 3006,
    'SYS_LOCK_PC': 3007,
    'SYS_COPY': 3008,
    'SYS_PRINT': 3009,

    # Custom Functions
    'DISABLE_KEY': 4001,
    'LAUNCH_APP': 4002,
    'RUN_MACRO': 4003,
    'CUSTOM_TEXT': 4004
}

# Physical 68-Key Layout definition for Husky Hailstorm
# Each entry: { 'id': slot_id, 'label': default_label, 'code': default_code, 'row': 0..4, 'col': col_pos, 'width': 1.0..6.25, 'x': x_unit, 'y': y_unit }
KEYBOARD_LAYOUT = [
    # --- ROW 0 (Numbers & Esc) ---
    {'slot': 22, 'label': 'Esc', 'code': 41, 'row': 0, 'width': 1.0, 'x': 0.0, 'y': 0.0, 'fn_label': '`~'},
    {'slot': 23, 'label': '1', 'code': 30, 'row': 0, 'width': 1.0, 'x': 1.0, 'y': 0.0, 'fn_label': 'F1'},
    {'slot': 24, 'label': '2', 'code': 31, 'row': 0, 'width': 1.0, 'x': 2.0, 'y': 0.0, 'fn_label': 'F2'},
    {'slot': 25, 'label': '3', 'code': 32, 'row': 0, 'width': 1.0, 'x': 3.0, 'y': 0.0, 'fn_label': 'F3'},
    {'slot': 26, 'label': '4', 'code': 33, 'row': 0, 'width': 1.0, 'x': 4.0, 'y': 0.0, 'fn_label': 'F4'},
    {'slot': 27, 'label': '5', 'code': 34, 'row': 0, 'width': 1.0, 'x': 5.0, 'y': 0.0, 'fn_label': 'F5'},
    {'slot': 28, 'label': '6', 'code': 35, 'row': 0, 'width': 1.0, 'x': 6.0, 'y': 0.0, 'fn_label': 'F6'},
    {'slot': 29, 'label': '7', 'code': 36, 'row': 0, 'width': 1.0, 'x': 7.0, 'y': 0.0, 'fn_label': 'F7'},
    {'slot': 30, 'label': '8', 'code': 37, 'row': 0, 'width': 1.0, 'x': 8.0, 'y': 0.0, 'fn_label': 'F8'},
    {'slot': 31, 'label': '9', 'code': 38, 'row': 0, 'width': 1.0, 'x': 9.0, 'y': 0.0, 'fn_label': 'F9'},
    {'slot': 32, 'label': '0', 'code': 39, 'row': 0, 'width': 1.0, 'x': 10.0, 'y': 0.0, 'fn_label': 'F10'},
    {'slot': 33, 'label': '-_', 'code': 45, 'row': 0, 'width': 1.0, 'x': 11.0, 'y': 0.0, 'fn_label': 'F11'},
    {'slot': 34, 'label': '=+', 'code': 46, 'row': 0, 'width': 1.0, 'x': 12.0, 'y': 0.0, 'fn_label': 'F12'},
    {'slot': 36, 'label': '⌫ Back', 'code': 42, 'row': 0, 'width': 2.0, 'x': 13.0, 'y': 0.0, 'fn_label': ''},
    {'slot': 37, 'label': 'Del', 'code': 76, 'row': 0, 'width': 1.0, 'x': 15.2, 'y': 0.0, 'fn_label': 'Ins'},

    # --- ROW 1 (QWERTY) ---
    {'slot': 44, 'label': 'Tab', 'code': 43, 'row': 1, 'width': 1.5, 'x': 0.0, 'y': 1.0, 'fn_label': ''},
    {'slot': 45, 'label': 'Q', 'code': 20, 'row': 1, 'width': 1.0, 'x': 1.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 46, 'label': 'W', 'code': 26, 'row': 1, 'width': 1.0, 'x': 2.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 47, 'label': 'E', 'code': 8, 'row': 1, 'width': 1.0, 'x': 3.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 48, 'label': 'R', 'code': 21, 'row': 1, 'width': 1.0, 'x': 4.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 49, 'label': 'T', 'code': 23, 'row': 1, 'width': 1.0, 'x': 5.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 50, 'label': 'Y', 'code': 28, 'row': 1, 'width': 1.0, 'x': 6.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 51, 'label': 'U', 'code': 24, 'row': 1, 'width': 1.0, 'x': 7.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 52, 'label': 'I', 'code': 12, 'row': 1, 'width': 1.0, 'x': 8.5, 'y': 1.0, 'fn_label': 'Prnt'},
    {'slot': 53, 'label': 'O', 'code': 18, 'row': 1, 'width': 1.0, 'x': 9.5, 'y': 1.0, 'fn_label': 'ScLk'},
    {'slot': 54, 'label': 'P', 'code': 19, 'row': 1, 'width': 1.0, 'x': 10.5, 'y': 1.0, 'fn_label': 'Paus'},
    {'slot': 55, 'label': '[{', 'code': 47, 'row': 1, 'width': 1.0, 'x': 11.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 56, 'label': ']}', 'code': 48, 'row': 1, 'width': 1.0, 'x': 12.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 78, 'label': '\\|', 'code': 52, 'row': 1, 'width': 1.5, 'x': 13.5, 'y': 1.0, 'fn_label': ''},
    {'slot': 59, 'label': 'Home', 'code': 74, 'row': 1, 'width': 1.0, 'x': 15.2, 'y': 1.0, 'fn_label': ''},

    # --- ROW 2 (ASDF) ---
    {'slot': 66, 'label': 'Caps', 'code': 57, 'row': 2, 'width': 1.75, 'x': 0.0, 'y': 2.0, 'fn_label': ''},
    {'slot': 68, 'label': 'A', 'code': 4, 'row': 2, 'width': 1.0, 'x': 1.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 69, 'label': 'S', 'code': 22, 'row': 2, 'width': 1.0, 'x': 2.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 70, 'label': 'D', 'code': 7, 'row': 2, 'width': 1.0, 'x': 3.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 71, 'label': 'F', 'code': 9, 'row': 2, 'width': 1.0, 'x': 4.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 72, 'label': 'G', 'code': 10, 'row': 2, 'width': 1.0, 'x': 5.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 73, 'label': 'H', 'code': 11, 'row': 2, 'width': 1.0, 'x': 6.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 74, 'label': 'J', 'code': 13, 'row': 2, 'width': 1.0, 'x': 7.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 75, 'label': 'K', 'code': 14, 'row': 2, 'width': 1.0, 'x': 8.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 76, 'label': 'L', 'code': 15, 'row': 2, 'width': 1.0, 'x': 9.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 77, 'label': '; :', 'code': 51, 'row': 2, 'width': 1.0, 'x': 10.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 79, 'label': '\' "', 'code': 50, 'row': 2, 'width': 1.0, 'x': 11.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 80, 'label': 'Enter ↵', 'code': 40, 'row': 2, 'width': 2.25, 'x': 12.75, 'y': 2.0, 'fn_label': ''},
    {'slot': 81, 'label': 'PgUp', 'code': 75, 'row': 2, 'width': 1.0, 'x': 15.2, 'y': 2.0, 'fn_label': ''},

    # --- ROW 3 (ZXCV) ---
    {'slot': 88, 'label': '⇧ Shift', 'code': 225, 'row': 3, 'width': 2.25, 'x': 0.0, 'y': 3.0, 'fn_label': ''},
    {'slot': 90, 'label': 'Z', 'code': 29, 'row': 3, 'width': 1.0, 'x': 2.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 91, 'label': 'X', 'code': 27, 'row': 3, 'width': 1.0, 'x': 3.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 92, 'label': 'C', 'code': 6, 'row': 3, 'width': 1.0, 'x': 4.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 93, 'label': 'V', 'code': 25, 'row': 3, 'width': 1.0, 'x': 5.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 94, 'label': 'B', 'code': 5, 'row': 3, 'width': 1.0, 'x': 6.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 95, 'label': 'N', 'code': 17, 'row': 3, 'width': 1.0, 'x': 7.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 96, 'label': 'M', 'code': 16, 'row': 3, 'width': 1.0, 'x': 8.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 97, 'label': ',<', 'code': 54, 'row': 3, 'width': 1.0, 'x': 9.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 98, 'label': '.>', 'code': 55, 'row': 3, 'width': 1.0, 'x': 10.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 99, 'label': '/?', 'code': 56, 'row': 3, 'width': 1.0, 'x': 11.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 101, 'label': '⇧ Shift', 'code': 229, 'row': 3, 'width': 1.75, 'x': 12.25, 'y': 3.0, 'fn_label': ''},
    {'slot': 102, 'label': '▲', 'code': 82, 'row': 3, 'width': 1.0, 'x': 14.1, 'y': 3.0, 'fn_label': 'Bright+'},
    {'slot': 103, 'label': 'PgDn', 'code': 78, 'row': 3, 'width': 1.0, 'x': 15.2, 'y': 3.0, 'fn_label': 'End'},

    # --- ROW 4 (Bottom Row) ---
    {'slot': 110, 'label': 'Ctrl', 'code': 224, 'row': 4, 'width': 1.25, 'x': 0.0, 'y': 4.0, 'fn_label': ''},
    {'slot': 111, 'label': 'Win', 'code': 227, 'row': 4, 'width': 1.25, 'x': 1.25, 'y': 4.0, 'fn_label': 'Lock'},
    {'slot': 112, 'label': 'Alt', 'code': 226, 'row': 4, 'width': 1.25, 'x': 2.5, 'y': 4.0, 'fn_label': ''},
    {'slot': 116, 'label': 'Space', 'code': 44, 'row': 4, 'width': 6.25, 'x': 3.75, 'y': 4.0, 'fn_label': ''},
    {'slot': 120, 'label': 'AltGr', 'code': 230, 'row': 4, 'width': 1.0, 'x': 10.0, 'y': 4.0, 'fn_label': ''},
    {'slot': 121, 'label': 'Fn', 'code': -10, 'row': 4, 'width': 1.0, 'x': 11.0, 'y': 4.0, 'fn_label': ''},
    {'slot': 122, 'label': 'Ctrl', 'code': 228, 'row': 4, 'width': 1.0, 'x': 12.0, 'y': 4.0, 'fn_label': ''},
    {'slot': 123, 'label': '◀', 'code': 80, 'row': 4, 'width': 1.0, 'x': 13.1, 'y': 4.0, 'fn_label': 'Speed-'},
    {'slot': 124, 'label': '▼', 'code': 81, 'row': 4, 'width': 1.0, 'x': 14.1, 'y': 4.0, 'fn_label': 'Bright-'},
    {'slot': 125, 'label': '▶', 'code': 79, 'row': 4, 'width': 1.0, 'x': 15.1, 'y': 4.0, 'fn_label': 'Speed+'}
]

# Quick group selectors for Per-Key lighting studio
KEY_GROUPS = {
    'Todos': [k['slot'] for k in KEYBOARD_LAYOUT],
    'WASD': [46, 68, 69, 70],          # W, A, S, D
    'Setas': [102, 123, 124, 125],     # Up, Left, Down, Right
    'Letras': [k['slot'] for k in KEYBOARD_LAYOUT if k['label'] in 'QWERTYUIOPASDFGHJKLZXCVBNM'],
    'Números': [23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    'Modificadores': [44, 66, 88, 101, 110, 111, 112, 120, 121, 122]
}
