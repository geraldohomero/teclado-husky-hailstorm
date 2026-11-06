"""
USB HID Device interface for Husky Hailstorm keyboard.
Handles connection, read/write queueing, thread synchronization, and simulation mode.
"""

import time
import threading
from typing import Callable, Optional

try:
    import hid
    HID_AVAILABLE = True
except ImportError:
    HID_AVAILABLE = False

from core.protocol import (
    VENDOR_ID,
    PRODUCT_ID,
    INTERFACE_NUM,
    USAGE_PAGE,
    build_inquire_sn,
    build_read_info,
    build_polling_rate,
    build_lighting_packet,
    build_color_chunk,
    build_apply_lighting,
    build_factory_reset,
    parse_serial_number,
    parse_firmware_info,
    PACKET_SIZE
)


class HuskyDevice:
    """Manages HID communications with Husky Hailstorm Keyboard."""

    def __init__(self, on_status_change: Optional[Callable[[bool, str], None]] = None):
        self._dev: Optional[object] = None
        self._lock = threading.Lock()
        self._is_connected = False
        self._is_simulated = False
        self._serial_number: Optional[str] = None
        self._device_info: Optional[dict] = None
        self._on_status_change = on_status_change
        self._poll_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def is_simulated(self) -> bool:
        return self._is_simulated

    @property
    def serial_number(self) -> str:
        return self._serial_number or ("SIMULATED-HAILSTORM-68" if self._is_simulated else "Desconectado")

    @property
    def device_info(self) -> dict:
        return self._device_info or {
            "model": "TY69SKRGB (Hailstorm)",
            "firmware": "V1.04.10" if not self._is_simulated else "V1.04.10 (Simulado)",
            "mcu": "M252",
            "oem": "TY"
        }

    def find_device_path(self) -> Optional[bytes]:
        """Finds the vendor-defined HID interface path (Interface 2) for Husky Hailstorm."""
        if not HID_AVAILABLE:
            return None

        try:
            for d in hid.enumerate():
                vid = d.get('vendor_id', 0)
                pid = d.get('product_id', 0)
                iface = d.get('interface_number', -1)
                usage_page = d.get('usage_page', 0)
                path = d.get('path', b'')

                # Match VID: 0x0416, PID: 0xC345
                if vid == VENDOR_ID and pid == PRODUCT_ID:
                    # Look for Interface 2 or Vendor Usage Page 0xFF1B
                    path_str = path.decode('utf-8', errors='ignore').lower()
                    if iface == INTERFACE_NUM or "mi_02" in path_str or usage_page == USAGE_PAGE:
                        return path
        except Exception as e:
            print(f"[HuskyDevice] Erro ao enumerar dispositivos HID: {e}")

        return None

    def connect(self, allow_simulation: bool = True) -> bool:
        """Attempts to open the keyboard HID interface."""
        with self._lock:
            if self._is_connected and self._dev is not None:
                return True

            path = self.find_device_path()
            if path and HID_AVAILABLE:
                try:
                    dev = hid.device()
                    dev.open_path(path)
                    dev.set_nonblocking(False)
                    self._dev = dev
                    self._is_connected = True
                    self._is_simulated = False
                    print(f"[HuskyDevice] Conectado com sucesso via HID: {path}")

                    # Read initial device metadata
                    self._read_initial_metadata()

                    if self._on_status_change:
                        self._on_status_change(True, f"Conectado: {self.device_info.get('model', 'Hailstorm')}")
                    return True
                except Exception as e:
                    print(f"[HuskyDevice] Falha ao abrir dispositivo HID: {e}")
                    self._dev = None

            # Fallback to simulation mode if real device is absent
            if allow_simulation:
                self._is_connected = True
                self._is_simulated = True
                self._serial_number = "ccaba42cd0464b2fbdc89f760c569555"
                self._device_info = {
                    "raw": "M252,01,KB,TY,TY69SKRGB,V1.04.10",
                    "mcu": "M252",
                    "type": "KB",
                    "oem": "TY",
                    "model": "TY69SKRGB",
                    "firmware": "V1.04.10 (Simulado)"
                }
                print("[HuskyDevice] Operando em modo de simulação.")
                if self._on_status_change:
                    self._on_status_change(True, "Modo Simulação (Hardware não detectado)")
                return True

            self._is_connected = False
            self._is_simulated = False
            if self._on_status_change:
                self._on_status_change(False, "Teclado Desconectado")
            return False

    def disconnect(self):
        """Closes the HID connection."""
        with self._lock:
            if self._dev is not None:
                try:
                    self._dev.close()
                except Exception:
                    pass
                self._dev = None
            self._is_connected = False
            self._is_simulated = False
            if self._on_status_change:
                self._on_status_change(False, "Desconectado")

    def _read_initial_metadata(self):
        """Queries SN and Firmware Version on initial connection."""
        try:
            # Inquire SN
            self._write_raw(build_inquire_sn())
            resp = self._read_raw(timeout_ms=500)
            if resp:
                sn = parse_serial_number(resp)
                if sn:
                    self._serial_number = sn

            # Read Info
            self._write_raw(build_read_info())
            resp = self._read_raw(timeout_ms=500)
            if resp:
                info = parse_firmware_info(resp)
                if info:
                    self._device_info = info
        except Exception as e:
            print(f"[HuskyDevice] Erro ao ler metadados: {e}")

    def _write_raw(self, packet: bytes) -> int:
        """Sends a 64-byte raw HID report."""
        if self._is_simulated or self._dev is None:
            return len(packet)
        return self._dev.write(packet)

    def _read_raw(self, timeout_ms: int = 500) -> Optional[bytes]:
        """Reads a response packet from the keyboard."""
        if self._is_simulated or self._dev is None:
            return None
        res = self._dev.read(PACKET_SIZE, timeout_ms)
        return bytes(res) if res else None

    def send_packet_sync(self, packet: bytes, wait_response: bool = False, timeout_ms: int = 300) -> Optional[bytes]:
        """Synchronously sends a packet and optionally awaits response."""
        with self._lock:
            if not self._is_connected:
                if not self.connect():
                    return None

            try:
                self._write_raw(packet)
                if wait_response:
                    return self._read_raw(timeout_ms)
                return b'\x00' * PACKET_SIZE
            except Exception as e:
                print(f"[HuskyDevice] Erro de comunicação USB: {e}")
                self._is_connected = False
                return None

    def close(self):
        """Closes the HID connection."""
        self.disconnect()

    def get_firmware_info(self) -> dict:
        """Returns firmware information dictionary."""
        return self.device_info

    def get_serial_number(self) -> str:
        """Returns keyboard hardware serial number."""
        return self.serial_number

    def write_color_chunk(self, chunk_index: int, rgb_data: bytes, target: int = 0) -> bool:
        """Sends a single chunk of per-key RGB colors."""
        pkt = build_color_chunk(chunk_index, rgb_data, target)
        return self.send_packet_sync(pkt) is not None

    def apply_lighting(self) -> bool:
        """Commits lighting settings to keyboard."""
        pkt = build_apply_lighting()
        return self.send_packet_sync(pkt) is not None

    def set_lighting(
        self,
        mode_id: int,
        brightness: int = 3,
        speed: int = 3,
        direction: int = 0,
        color_mode: int = 1,
        r: int = 255,
        g: int = 0,
        b: int = 0,
        target: int = 0,
        auto_apply: bool = True
    ) -> bool:
        """Sends lighting mode command to the keyboard or side light."""
        pkt = build_lighting_packet(
            mode_id=mode_id,
            brightness=brightness,
            speed=speed,
            direction=direction,
            color_mode=color_mode,
            r=r,
            g=g,
            b=b,
            target=target
        )
        res = self.send_packet_sync(pkt)
        if res is not None and auto_apply:
            time.sleep(0.01)
            self.send_packet_sync(build_apply_lighting())
            return True
        return res is not None

    def set_per_key_colors(self, key_rgb_dict: dict[int, tuple[int, int, int]]) -> bool:
        """
        Streams per-key RGB colors to the keyboard.
        key_rgb_dict: dict mapping slot_index (0..131) -> (R, G, B)
        """
        # Pack RGB bytes for up to 132 slots
        # Slots are chunked into 18 keys (54 bytes) each
        slots = sorted(key_rgb_dict.keys())
        all_bytes = bytearray()
        for s in range(132):
            color = key_rgb_dict.get(s, (0, 0, 0))
            all_bytes.extend(color)

        chunk_size = 54
        total_chunks = (len(all_bytes) + chunk_size - 1) // chunk_size

        success = True
        for chunk_idx in range(total_chunks):
            chunk_data = all_bytes[chunk_idx * chunk_size : (chunk_idx + 1) * chunk_size]
            pkt = build_color_chunk(chunk_idx, bytes(chunk_data))
            if self.send_packet_sync(pkt) is None:
                success = False
            time.sleep(0.005)

        # Commit lighting
        self.send_packet_sync(build_apply_lighting())
        return success

    def set_polling_rate(self, rate_hz: int) -> bool:
        """Configures the USB polling rate (125, 250, 500, or 1000 Hz)."""
        pkt = build_polling_rate(rate_hz)
        return self.send_packet_sync(pkt) is not None

    def factory_reset(self) -> bool:
        """Restores the keyboard to factory default onboard settings."""
        pkt = build_factory_reset()
        res = self.send_packet_sync(pkt)
        if res is not None:
            time.sleep(0.1)
            self._read_initial_metadata()
            return True
        return False
