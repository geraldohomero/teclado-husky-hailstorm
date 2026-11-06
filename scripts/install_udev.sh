#!/usr/bin/env bash
# Husky Hailstorm - Linux udev rules installer
# Grants non-root users access to the keyboard's vendor-specific USB HID interface (VID: 0416, PID: c345)

set -e

RULES_FILE="/etc/udev/rules.d/99-husky-hailstorm.rules"

echo "=== Configurando regras de udev para o Husky Hailstorm ==="

if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute este script com sudo: sudo ./scripts/install_udev.sh"
  exit 1
fi

cat << 'EOF' > "$RULES_FILE"
# Teclado Gamer Husky Hailstorm (TY69SKRGB)
# Vendor: 0416 (Winbond Electronics Corp.), Product: c345
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="c345", MODE="0666", TAG+="uaccess"
KERNEL=="hidraw*", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="c345", MODE="0666", TAG+="uaccess"
EOF

echo "Regra criada em $RULES_FILE"

echo "Recarregando regras do udev..."
udevadm control --reload-rules
udevadm trigger

echo "Pronto! Se o teclado já estiver conectado, desconecte e conecte novamente o cabo USB."
