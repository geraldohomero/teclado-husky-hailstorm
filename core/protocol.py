"""
Protocol definitions and USB HID packet constructors for Husky Hailstorm.
Matches the reverse engineered WitMod / TianYu (TY69SKRGB) peripheral specification.
"""

# USB Identification
VENDOR_ID = 0x0416
PRODUCT_ID = 0xC345
INTERFACE_NUM = 2
USAGE_PAGE = 0xFF1B
USAGE = 0x0091

# Packet dimensions
PACKET_SIZE = 64
REPORT_ID = 0x01

# Command OpCodes
CMD_READ_INFO = 0x0D          # Returns firmware version and device model
CMD_INQUIRE_SN = 0x15         # Returns 32-character hardware serial number
CMD_FACTORY_RESET = 0x14      # Restores keyboard to onboard factory defaults
CMD_SET_POLLING_RATE = 0x46   # Changes USB report polling rate (125Hz - 1000Hz)
CMD_SET_LIGHT_MODE = 0x47     # Configures active lighting effect, brightness, speed, color
CMD_WRITE_COLOR_CHUNK = 0x0F  # Streams per-key RGB colors (up to 18 keys / 54 bytes per packet)
CMD_APPLY_LIGHTING = 0x17     # Commits and activates lighting configuration
CMD_CUSTOM_RGB_MAP = 0x41     # Custom per-key RGB profile map


def pad_packet(data: bytearray | bytes, size: int = PACKET_SIZE) -> bytes:
    """Ensures packet is exactly `size` bytes long by right-padding with 0x00."""
    if len(data) >= size:
        return bytes(data[:size])
    return bytes(data) + bytes(size - len(data))


def build_inquire_sn() -> bytes:
    """Builds packet to query keyboard hardware serial number."""
    pkt = bytearray(PACKET_SIZE)
    pkt[0] = REPORT_ID
    pkt[1] = CMD_INQUIRE_SN
    return bytes(pkt)


def build_read_info() -> bytes:
    """Builds packet to query device model and firmware version."""
    pkt = bytearray(PACKET_SIZE)
    pkt[0] = REPORT_ID
    pkt[1] = CMD_READ_INFO
    return bytes(pkt)


def build_factory_reset() -> bytes:
    """Builds packet to restore factory default configuration."""
    pkt = bytearray(PACKET_SIZE)
    pkt[0] = REPORT_ID
    pkt[1] = CMD_FACTORY_RESET
    pkt[2] = 0x00
    pkt[3] = 0x00
    pkt[4] = 0x00
    pkt[5] = 0x00
    pkt[6] = 0x01
    return bytes(pkt)


def build_polling_rate(rate_hz: int) -> bytes:
    """
    Builds packet to set USB report polling rate.
    Supported: 125Hz, 250Hz, 500Hz, 1000Hz.
    """
    # Firmware codes: 8 = 125Hz (8ms), 4 = 250Hz (4ms), 2 = 500Hz (2ms), 1 = 1000Hz (1ms)
    mapping = {
        125: 8,
        250: 4,
        500: 2,
        1000: 1
    }
    code = mapping.get(rate_hz, 1)

    pkt = bytearray(PACKET_SIZE)
    pkt[0] = REPORT_ID
    pkt[1] = CMD_SET_POLLING_RATE
    pkt[2] = 0x00
    pkt[3] = 0x00
    pkt[4] = 0x00
    pkt[5] = 0x01
    pkt[6] = code
    return bytes(pkt)


def build_lighting_packet(
    mode_id: int,
    brightness: int = 3,       # 0 to 4
    speed: int = 3,            # 0 to 4
    direction: int = 0,        # 0 = Backward/Left, 1 = Forward/Right
    color_mode: int = 1,       # 1 = Single color, 2 = RGB Spectrum/Full Color
    r: int = 255,
    g: int = 0,
    b: int = 0,
    target: int = 0            # 0 = Keyboard, 1 = Side light
) -> bytes:
    """
    Builds Command 0x47 packet configuring the active lighting mode and parameters.
    """
    pkt = bytearray(PACKET_SIZE)
    pkt[0] = REPORT_ID
    pkt[1] = CMD_SET_LIGHT_MODE
    pkt[2] = color_mode & 0xFF
    pkt[3] = 0x00
    pkt[4] = 0x00
    pkt[5] = 0x3A              # Command payload tag
    pkt[6] = brightness & 0xFF # Brightness / Speed profile
    
    # Write payload parameters
    pkt[7] = mode_id & 0xFF
    pkt[8] = speed & 0xFF
    pkt[9] = direction & 0xFF
    pkt[10] = r & 0xFF
    pkt[11] = g & 0xFF
    pkt[12] = b & 0xFF
    pkt[13] = target & 0xFF
    return bytes(pkt)


def build_color_chunk(chunk_index: int, rgb_data: bytes, target: int = 0) -> bytes:
    """
    Builds Command 0x0F packet carrying a chunk of per-key RGB colors.
    Each chunk contains up to 18 keys (54 RGB bytes).
    """
    length = min(len(rgb_data), 54)
    pkt = bytearray(PACKET_SIZE)
    pkt[0] = REPORT_ID
    pkt[1] = CMD_WRITE_COLOR_CHUNK
    pkt[2] = target & 0xFF     # 0 = Keyboard, 1 = Side
    pkt[3] = 0x00
    pkt[4] = chunk_index & 0xFF
    pkt[5] = length & 0xFF
    pkt[6:6 + length] = rgb_data[:length]
    return bytes(pkt)


def build_apply_lighting() -> bytes:
    """
    Builds Command 0x17 packet committing the lighting settings.
    """
    pkt = bytearray(PACKET_SIZE)
    pkt[0] = REPORT_ID
    pkt[1] = CMD_APPLY_LIGHTING
    pkt[2] = 0x00
    pkt[3] = 0x00
    pkt[4] = 0x00
    pkt[5] = 0x01
    pkt[6] = 0x01
    return bytes(pkt)


def parse_serial_number(response: bytes | list[int]) -> str | None:
    """Parses response packet from Command 0x15."""
    if len(response) < 6:
        return None
    if response[0] == REPORT_ID and response[1] == CMD_INQUIRE_SN:
        length = response[5]
        sn_bytes = bytes(response[6:6 + length]).rstrip(b'\x00')
        return sn_bytes.decode('ascii', errors='ignore')
    return None


def parse_firmware_info(response: bytes | list[int]) -> dict | None:
    """
    Parses response packet from Command 0x0D (e.g. 'M252,01,KB,TY,TY69SKRGB,V1.04.10').
    """
    if len(response) < 6:
        return None
    if response[0] == REPORT_ID and response[1] == CMD_READ_INFO:
        length = response[5]
        info_bytes = bytes(response[6:6 + length]).rstrip(b'\x00')
        info_str = info_bytes.decode('ascii', errors='ignore')
        parts = info_str.split(',')
        return {
            "raw": info_str,
            "mcu": parts[0] if len(parts) > 0 else "Unknown",
            "type": parts[2] if len(parts) > 2 else "KB",
            "oem": parts[3] if len(parts) > 3 else "TY",
            "model": parts[4] if len(parts) > 4 else "TY69SKRGB",
            "firmware": parts[5] if len(parts) > 5 else "V1.0.0"
        }
    return None
