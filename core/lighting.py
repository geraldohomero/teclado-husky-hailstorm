"""
Lighting effects, modes, and color definitions for Husky Hailstorm.
"""

# Complete list of official keyboard lighting effects
KEYBOARD_EFFECTS = [
    {"id": 0, "name": "Static", "desc": "Luz estática contínua", "has_speed": False, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 1, "name": "Neon", "desc": "Transição suave de espectro de cores", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": False, "has_dual": False},
    {"id": 2, "name": "Breath", "desc": "Efeito de respiração suave", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 3, "name": "Wave", "desc": "Onda de cores contínua", "has_speed": True, "has_bright": True, "has_dir": True, "has_color": True, "has_dual": False},
    {"id": 4, "name": "Twinkle", "desc": "Cintilação estelar aleatória", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 5, "name": "Snake", "desc": "Serpente percorrendo o teclado", "has_speed": True, "has_bright": True, "has_dir": True, "has_color": True, "has_dual": False},
    {"id": 6, "name": "Radar", "desc": "Varredura circular de radar", "has_speed": True, "has_bright": True, "has_dir": True, "has_color": True, "has_dual": False},
    {"id": 7, "name": "Aurora", "desc": "Luzes do norte em fluxo gradual", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 8, "name": "Ripple", "desc": "Ondas na água a cada tecla pressionada", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 9, "name": "Speed Respond", "desc": "Reativo à velocidade de digitação", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 10, "name": "Musical Rhythm", "desc": "Visualizador de áudio/música em tempo real", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 11, "name": "DPI / Single", "desc": "Iluminação de ponto único", "has_speed": False, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 12, "name": "Cross", "desc": "Expansão em cruz a partir da tecla", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 13, "name": "Reactive", "desc": "A tecla se acende e desvanece ao clicar", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": True},
    {"id": 14, "name": "Custom", "desc": "Personalização de cor tecla por tecla (Per-Key RGB)", "has_speed": False, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 15, "name": "Auto Ripple", "desc": "Ondas contínuas concêntricas automáticas", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False},
    {"id": 16, "name": "Striation", "desc": "Linhas de luz verticais ou horizontais", "has_speed": True, "has_bright": True, "has_dir": True, "has_color": True, "has_dual": False},
    {"id": 17, "name": "Fireworks", "desc": "Explosão de faíscas ao pressionar teclas", "has_speed": True, "has_bright": True, "has_dir": False, "has_color": True, "has_dual": False}
]

# Side light effects
SIDE_EFFECTS = [
    {"id": 0, "name": "Static", "desc": "Luz lateral estática"},
    {"id": 1, "name": "Breath", "desc": "Respiração lateral"},
    {"id": 2, "name": "Wave", "desc": "Onda de cores lateral"},
    {"id": 3, "name": "Neon", "desc": "Ciclagem neon nas laterais"},
    {"id": 4, "name": "Collision", "desc": "Colisão de luzes laterais"},
    {"id": 5, "name": "Off", "desc": "Desligado"}
]

# Color mode: Single Color (mono) vs Full Color (Rainbow RGB)
COLOR_MODES = [
    {"id": 1, "name": "Cor Fixa / Única"},
    {"id": 2, "name": "RGB Colorido / Arco-íris"}
]

# Direction options
DIRECTIONS = [
    {"id": 0, "name": "Esquerda / Trás (Backward)"},
    {"id": 1, "name": "Direita / Frente (Forward)"},
    {"id": 2, "name": "Para Cima (Up)"},
    {"id": 3, "name": "Para Baixo (Down)"}
]

# Curated palette presets
PALETTE_PRESETS = [
    ("#FF0033", "Vermelho Husky"),
    ("#FF4500", "Laranja"),
    ("#FFD700", "Amarelo Ouro"),
    ("#00FF66", "Verde Gamer"),
    ("#00F0FF", "Ciano Neon"),
    ("#0066FF", "Azul Elétrico"),
    ("#9900FF", "Roxo Profundo"),
    ("#FF0099", "Rosa Choque"),
    ("#FFFFFF", "Branco Frio"),
    ("#1A1A1A", "Apagado (Preto)")
]

def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Converts a hex color string ('#RRGGBB' or 'RRGGBB') to (R, G, B) tuple."""
    hex_clean = hex_str.lstrip('#')
    if len(hex_clean) == 3:
        hex_clean = ''.join(c * 2 for c in hex_clean)
    if len(hex_clean) != 6:
        return (255, 0, 0)
    try:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        return (r, g, b)
    except ValueError:
        return (255, 0, 0)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converts (R, G, B) integers (0-255) to '#RRGGBB'."""
    return f"#{max(0, min(255, r)):02X}{max(0, min(255, g)):02X}{max(0, min(255, b)):02X}"
