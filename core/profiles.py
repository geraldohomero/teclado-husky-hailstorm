"""
Profile management, persistence, and XML/JSON serialization for Husky Hailstorm.
Supports Default, FN, and FN1 layer remaps, Per-Key RGB lighting, and Macro definitions.
Fully compatible with official WitMod / Hailstorm XML profiles.
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from core.keycodes import KEYBOARD_LAYOUT, CODE_TO_NAME, HID_KEYCODES
from core.lighting import KEYBOARD_EFFECTS, hex_to_rgb, rgb_to_hex


class MacroItem:
    """Represents a single key press/release or delay event in a macro."""
    def __init__(self, event_type: str = "down", code: int = 0, key_name: str = "", delay_ms: int = 50):
        self.event_type = event_type  # "down", "up", "delay"
        self.code = code              # HID keycode
        self.key_name = key_name      # Human-readable name
        self.delay_ms = delay_ms      # Delay in milliseconds

    def to_dict(self) -> dict:
        return {
            "type": self.event_type,
            "code": self.code,
            "key": self.key_name,
            "delay_ms": self.delay_ms
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MacroItem':
        return cls(
            event_type=data.get("type", "down"),
            code=data.get("code", 0),
            key_name=data.get("key", ""),
            delay_ms=data.get("delay_ms", 50)
        )


class Macro:
    """Represents a macro sequence with trigger and playback rules."""
    def __init__(self, macro_id: str, name: str, repeat_mode: int = 1, repeat_count: int = 1):
        self.id = macro_id
        self.name = name
        self.repeat_mode = repeat_mode    # 1 = Once, 2 = Loop while pressed, 3 = Toggle loop, 4 = Repeat N times
        self.repeat_count = repeat_count
        self.events: List[MacroItem] = []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "repeat_mode": self.repeat_mode,
            "repeat_count": self.repeat_count,
            "events": [e.to_dict() for e in self.events]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Macro':
        m = cls(
            macro_id=data.get("id", "macro_1"),
            name=data.get("name", "Nova Macro"),
            repeat_mode=data.get("repeat_mode", 1),
            repeat_count=data.get("repeat_count", 1)
        )
        for ev in data.get("events", []):
            m.events.append(MacroItem.from_dict(ev))
        return m


class Profile:
    """Complete profile state for Husky Hailstorm keyboard."""
    def __init__(self, name: str = "Default Profile"):
        self.name = name

        # Keyboard Lighting Settings
        self.light_mode: int = 1        # 0=Static, 1=Neon, 2=Breath, 3=Wave...
        self.brightness: int = 3        # 0 to 4
        self.speed: int = 3             # 0 to 4
        self.direction: int = 0         # 0=Left/Back, 1=Right/Forward, 2=Up, 3=Down
        self.color_mode: int = 2        # 1=Single Color, 2=Rainbow/Spectrum
        self.color: str = "#FF0033"     # Default Husky Red

        # Side Light Settings
        self.side_mode: int = 0         # 0=Static, 1=Breath, 2=Wave, 3=Neon, 4=Collision, 5=Off
        self.side_brightness: int = 3
        self.side_speed: int = 3
        self.side_color: str = "#FF0033"

        # Hardware System Settings
        self.polling_rate: int = 1000   # 125, 250, 500, 1000 Hz
        self.win_lock: bool = False

        # Per-Key RGB (slot_id: str/int -> hex_color)
        self.per_key_colors: Dict[int, str] = {}
        for k in KEYBOARD_LAYOUT:
            self.per_key_colors[k['slot']] = "#FF0033"

        # Remap Layers: slot_id -> { "type": 0, "code": code, "name": label }
        self.layer_default: Dict[int, dict] = {}
        self.layer_fn: Dict[int, dict] = {}
        self.layer_fn1: Dict[int, dict] = {}

        # Initialize default layers from physical layout
        for k in KEYBOARD_LAYOUT:
            slot = k['slot']
            self.layer_default[slot] = {
                "type": 0,
                "code": k['code'],
                "name": k['label']
            }
            if k.get('fn_label'):
                self.layer_fn[slot] = {
                    "type": 0,
                    "code": HID_KEYCODES.get(k['fn_label'], k['code']),
                    "name": k['fn_label']
                }

        # Macros
        self.macros: List[Macro] = []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "lighting": {
                "mode": self.light_mode,
                "brightness": self.brightness,
                "speed": self.speed,
                "direction": self.direction,
                "color_mode": self.color_mode,
                "color": self.color
            },
            "side_lighting": {
                "mode": self.side_mode,
                "brightness": self.side_brightness,
                "speed": self.side_speed,
                "color": self.side_color
            },
            "settings": {
                "polling_rate": self.polling_rate,
                "win_lock": self.win_lock
            },
            "per_key_colors": {str(slot): col for slot, col in self.per_key_colors.items()},
            "layer_default": {str(slot): v for slot, v in self.layer_default.items()},
            "layer_fn": {str(slot): v for slot, v in self.layer_fn.items()},
            "layer_fn1": {str(slot): v for slot, v in self.layer_fn1.items()},
            "macros": [m.to_dict() for m in self.macros]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Profile':
        p = cls(name=data.get("name", "Perfil Carregado"))

        lighting = data.get("lighting", {})
        p.light_mode = lighting.get("mode", 1)
        p.brightness = lighting.get("brightness", 3)
        p.speed = lighting.get("speed", 3)
        p.direction = lighting.get("direction", 0)
        p.color_mode = lighting.get("color_mode", 2)
        p.color = lighting.get("color", "#FF0033")

        side = data.get("side_lighting", {})
        p.side_mode = side.get("mode", 0)
        p.side_brightness = side.get("brightness", 3)
        p.side_speed = side.get("speed", 3)
        p.side_color = side.get("color", "#FF0033")

        settings = data.get("settings", {})
        p.polling_rate = settings.get("polling_rate", 1000)
        p.win_lock = settings.get("win_lock", False)

        for slot_str, color in data.get("per_key_colors", {}).items():
            p.per_key_colors[int(slot_str)] = color

        for slot_str, mapping in data.get("layer_default", {}).items():
            p.layer_default[int(slot_str)] = mapping

        for slot_str, mapping in data.get("layer_fn", {}).items():
            p.layer_fn[int(slot_str)] = mapping

        for slot_str, mapping in data.get("layer_fn1", {}).items():
            p.layer_fn1[int(slot_str)] = mapping

        p.macros = [Macro.from_dict(m) for m in data.get("macros", [])]
        return p

    def save_json(self, file_path: str):
        """Saves profile to formatted JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_json(cls, file_path: str) -> 'Profile':
        """Loads profile from JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def export_xml(self, file_path: str):
        """
        Exports profile compatible with official WitMod / Husky Hailstorm XML structure.
        """
        root = ET.Element("Parameters", {"profileIndex": "1"})
        config = ET.SubElement(root, "config", {
            "index": "1",
            "name": self.name,
            "proFileAppName": "",
            "proFileAppIco": ""
        })

        # Main keyboard light
        r, g, b = hex_to_rgb(self.color)
        light0 = ET.SubElement(config, "light0", {
            "usingIndex": str(self.light_mode),
            "ledOpenOrClose": "0",
            "SynchronizeStatus": "0"
        })
        ET.SubElement(light0, "item", {
            "ledKeyboardOrSide": "0",
            "ledType": str(self.light_mode),
            "ledBrightness": str(self.brightness),
            "ledSpeed": str(self.speed),
            "ledModeR": str(r),
            "ledModeG": str(g),
            "ledModeB": str(b),
            "ledBgR": "0",
            "ledBgG": "0",
            "ledBgB": "0",
            "ledDirection": str(self.direction),
            "ledModeType": str(self.color_mode),
            "ledOpenOrClose": "0",
            "ledUpdate": "0"
        })

        # Side lights (light1 & light2)
        sr, sg, sb = hex_to_rgb(self.side_color)
        for i in [1, 2]:
            light_elem = ET.SubElement(config, f"light{i}", {"usingIndex": str(self.side_mode)})
            ET.SubElement(light_elem, "item", {
                "ledKeyboardOrSide": str(i),
                "ledType": str(self.side_mode),
                "ledBrightness": str(self.side_brightness),
                "ledSpeed": str(self.side_speed),
                "ledModeR": str(sr),
                "ledModeG": str(sg),
                "ledModeB": str(sb),
                "ledBgR": "0",
                "ledBgG": "0",
                "ledBgB": "0",
                "ledDirection": "0",
                "ledModeType": "1",
                "ledOpenOrClose": "0",
                "ledUpdate": "0"
            })

        # Custom Per-Key RGB
        custom_light = ET.SubElement(config, "customLight")
        custom_led = ET.SubElement(custom_light, "customLed", {
            "index": "0",
            "name": "Custom Profile",
            "isUsing": "Using",
            "usingFlagIndex": "0"
        })
        for key in KEYBOARD_LAYOUT:
            slot = key['slot']
            kr, kg, kb = hex_to_rgb(self.per_key_colors.get(slot, "#FF0033"))
            ET.SubElement(custom_led, "item", {
                "keyCode": str(key['code']),
                "codeName": key['label'],
                "indexX": str(key['row']),
                "indexY": str(int(key['x'])),
                "colorR": str(kr),
                "colorG": str(kg),
                "colorB": str(kb),
                "transparentNum": "128"
            })

        # Remap / Macro items
        macro_elem = ET.SubElement(config, "macro")
        for slot_idx in range(132):
            if slot_idx in self.layer_default:
                mapping = self.layer_default[slot_idx]
                ET.SubElement(macro_elem, "item", {
                    "keyCode": str(mapping.get("code", -1)),
                    "keyChar": mapping.get("name", ""),
                    "operateType": str(mapping.get("type", 0)),
                    "repeatNum": "1",
                    "mode": "1",
                    "Value": str(mapping.get("code", 0))
                })
            else:
                ET.SubElement(macro_elem, "item", {
                    "keyCode": "-1",
                    "keyChar": "-",
                    "operateType": "-1",
                    "repeatNum": "1",
                    "mode": "1",
                    "Value": "0"
                })

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    @classmethod
    def import_xml(cls, file_path: str) -> 'Profile':
        """
        Imports profile from official WitMod / Husky Hailstorm XML file.
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        config = root.find("config")
        name = config.get("name", "Perfil Importado") if config is not None else "Perfil Importado"
        profile = cls(name=name)

        if config is not None:
            # Read light0
            light0 = config.find("light0")
            if light0 is not None:
                item = light0.find("item")
                if item is not None:
                    profile.light_mode = int(item.get("ledType", "1"))
                    profile.brightness = int(item.get("ledBrightness", "3"))
                    profile.speed = int(item.get("ledSpeed", "3"))
                    profile.direction = int(item.get("ledDirection", "0"))
                    profile.color_mode = int(item.get("ledModeType", "2"))
                    r = int(item.get("ledModeR", "255"))
                    g = int(item.get("ledModeG", "0"))
                    b = int(item.get("ledModeB", "0"))
                    profile.color = rgb_to_hex(r, g, b)

            # Read customLight
            custom_light = config.find("customLight")
            if custom_light is not None:
                custom_led = custom_light.find("customLed")
                if custom_led is not None:
                    for item in custom_led.findall("item"):
                        code = int(item.get("keyCode", "0"))
                        r = int(item.get("colorR", "255"))
                        g = int(item.get("colorG", "0"))
                        b = int(item.get("colorB", "0"))
                        # Map code to slot
                        for k in KEYBOARD_LAYOUT:
                            if k['code'] == code:
                                profile.per_key_colors[k['slot']] = rgb_to_hex(r, g, b)

            # Read macro remap items
            macro_elem = config.find("macro")
            if macro_elem is not None:
                items = macro_elem.findall("item")
                for slot_idx, itm in enumerate(items):
                    op_type = int(itm.get("operateType", "-1"))
                    if op_type != -1 and slot_idx in profile.layer_default:
                        code = int(itm.get("keyCode", "-1"))
                        name_str = itm.get("keyChar", CODE_TO_NAME.get(code, f"Key_{code}"))
                        profile.layer_default[slot_idx] = {
                            "type": op_type,
                            "code": code,
                            "name": name_str
                        }

        return profile


class ProfileManager:
    """Manages profile loading, saving, and active selection."""
    def __init__(self, storage_dir: str = "profiles"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.profiles: List[Profile] = []
        self.active_index: int = 0
        self.load_all()

    def load_all(self):
        """Loads all profiles from storage_dir, or creates a default one."""
        self.profiles = []
        json_files = [f for f in os.listdir(self.storage_dir) if f.endswith(".json")]
        for f in sorted(json_files):
            try:
                prof = Profile.load_json(os.path.join(self.storage_dir, f))
                self.profiles.append(prof)
            except Exception as e:
                print(f"[ProfileManager] Falha ao carregar {f}: {e}")

        if not self.profiles:
            # Create default profile
            default_prof = Profile(name="Perfil Padrão")
            self.profiles.append(default_prof)
            default_prof.save_json(os.path.join(self.storage_dir, "profile_1.json"))

        self.active_index = 0

    @property
    def current(self) -> Profile:
        if 0 <= self.active_index < len(self.profiles):
            return self.profiles[self.active_index]
        return self.profiles[0]

    def add_profile(self, name: str) -> Profile:
        new_prof = Profile(name=name)
        self.profiles.append(new_prof)
        self.active_index = len(self.profiles) - 1
        self.save_current()
        return new_prof

    def delete_profile(self, index: int) -> bool:
        if len(self.profiles) <= 1:
            return False
        if 0 <= index < len(self.profiles):
            del self.profiles[index]
            self.active_index = max(0, min(self.active_index, len(self.profiles) - 1))
            return True
        return False

    def save_current(self):
        filename = f"profile_{self.active_index + 1}.json"
        self.current.save_json(os.path.join(self.storage_dir, filename))
