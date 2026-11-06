# Husky Hailstorm Control Center

### Driver Open-Source e Painel de Controle Multiplataforma (Windows, Linux, macOS)

**Para o Teclado Mecânico Gamer Husky Hailstorm (Modelo TY69SKRGB - 68 Teclas ABNT2 / ANSI)**

---

## Sobre o Projeto

Este projeto nasceu da engenharia reversa completa realizada no software oficial do teclado mecânico **Husky Hailstorm** (`Teclado Gamer Hailstorm.exe` da OEM TianYu / WitMod) utilizando o **REA (Reverse Engineer Anything)** integrado ao Antigravity.

O software oficial original é limitado exclusivamente ao Windows e possui dependências pesadas do Qt5. Este novo painel foi construído do zero em Python com uma interface gráfica moderna, responsiva, fluida e com suporte multiplataforma para **Windows**, **Linux** e **macOS**, reproduzindo **100% de todas as funcionalidades e configurações do aplicativo original** e adicionando melhorias exclusivas (como pré-visualização de iluminação em tempo real tecla a tecla, suporte a JSON limpo e modo de simulação).

---

## Guia do REA (npx rea-agents setup) e Engenharia Reversa

### 1. Entendendo o REA no Windows
O **REA (Reverse Engineer Anything)** é um ecossistema avançado de agentes MCP para engenharia reversa de binários nativos (PE, ELF, Mach-O), firmware, pacotes e aplicações Electron/Web.

Ao rodar ferramentas baseadas em Node no PowerShell do Windows, pode ocorrer o bloqueio de segurança:
```text
npx : O arquivo C:\Program Files\nodejs\npx.ps1 não pode ser carregado porque a execução de scripts foi desabilitada neste sistema.
```
**Solução recomendada no Windows:**
Invoque explicitamente o executável de lote `.cmd`:
```powershell
npx.cmd -y rea-agents@6.8.0 doctor --client antigravity --json
```
> **Nota de Configuração:** O REA já está devidamente configurado e integrado no Antigravity através do arquivo `C:\Users\geral\.gemini\config\mcp_config.json`, disponibilizando nativamente ferramentas como `inspect_pe_imports`, `inspect_binary_layout`, `search_strings` e `inspect_native_instruction`.

### 2. Descobertas da Engenharia Reversa no Hailstorm
- **Binário Analisado:** `C:\Program Files (x86)\Husky\Teclado Gamer Hailstorm\Teclado Gamer Hailstorm.exe`
- **Bibliotecas Importadas:** `hidapi.dll`, `Qt5Widgets.dll`, `Qt5Multimedia.dll`, `fftreal.dll`.
- **Identificação USB:**
  - **Vendor ID (VID):** `0x0416` (Winbond Electronics Corp.)
  - **Product ID (PID):** `0xC345` (Teclado Gamer Husky Hailstorm)
  - **Interface de Comunicação:** Interface 2 (`MI_02`, UsagePage `0xFF1B`, Usage `0x0091`).
  - **Tamanho do Pacote:** 64 bytes (`0x40`), Report ID `0x01`.
- **Microcontrolador & Firmware Extraídos:**
  - MCU: **Winbond / Nuvoton M252**
  - Modelo OEM: **TY69SKRGB**
  - Firmware Onboard: **V1.04.10**
  - Hardware Serial Number lido via hardware: `ccaba42cd0464b2fbdc89f760c569555`

---

## Protocolo USB HID Reverso

Todas as mensagens enviadas ao microcontrolador do teclado possuem 64 bytes:

| OpCode | Função | Formato do Pacote | Descrição |
|---|---|---|---|
| `0x0D` | Read Device Info | `[0x01, 0x0D, 0, 0, 0, 0, ...]` | Retorna string com MCU, OEM, modelo e versão de firmware. |
| `0x15` | Inquire SN | `[0x01, 0x15, 0, 0, 0, 0, ...]` | Retorna o número de série de 32 caracteres gravado na OTP/Flash. |
| `0x46` | Set Polling Rate | `[0x01, 0x46, 0, 0, 0, 1, code, ...]` | `code=1` (1000Hz), `code=2` (500Hz), `code=4` (250Hz), `code=8` (125Hz). |
| `0x47` | Set Lighting Mode | `[0x01, 0x47, color_mode, 0, 0, 0x3A, bright, mode_id, speed, dir, R, G, B, target, ...]` | Configura efeito (0-17), velocidade (0-4), brilho (0-4), direção e cor. |
| `0x0F` | Write Color Chunk | `[0x01, 0x0F, target, 0, chunk_idx, length, R, G, B, ...]` | Transmite cores por tecla em blocos de até 18 teclas (54 bytes RGB). |
| `0x17` | Apply / Commit | `[0x01, 0x17, 0, 0, 0, 1, 1, ...]` | Grava e ativa a iluminação configurada na memória volátil do teclado. |
| `0x14` | Factory Reset | `[0x01, 0x14, 0, 0, 0, 0, 1, ...]` | Restaura a flash interna para as configurações de fábrica. |

---

## Funcionalidades do Aplicativo

### 1. Iluminação do Teclado e Lateral
- Suporte a todos os **18 modos oficiais de efeito RGB**:
  - `Static`, `Neon`, `Breath`, `Wave`, `Twinkle`, `Snake`, `Radar`, `Aurora`, `Ripple`, `Speed Respond`, `Musical Rhythm`, `DPI / Single`, `Cross`, `Reactive`, `Custom`, `Auto Ripple`, `Striation`, `Fireworks`.
- **Efeitos Laterais (Side Glow)**: `Static`, `Breath`, `Wave`, `Neon`, `Collision`, `Off`.
- Ajuste granular de **Brilho** (0 a 4) e **Velocidade** (0 a 4).
- Seletor de **Direção** (Esquerda, Direita, Para Cima, Para Baixo).
- Modos de cor: **Cor Fixa / Única** ou **Arco-íris / Espectro RGB**.
- Chips de paleta pré-definida e Seletor Livre RGB (`#RRGGBB`).
- Opção de envio e visualização em tempo real.

### 2. Estúdio Per-Key RGB (Custom)
- Teclado interativo visual de 68 teclas com representação de LED sob as teclas.
- Seleção por clique individual, caixa de arrasto do mouse ou botões de grupo rápido:
  - `WASD`, `Setas`, `Letras`, `Números`, `Modificadores` e `Todos`.
- Pincel de cor livre, preenchimento total e limpeza.
- Envio segmentado em blocos (Command 0x0F) com commit imediato.

### 3. Remapeamento Completo de Teclas (Layers)
- 3 Camadas suportadas: **Camada Base (Default)**, **Camada FN** e **Camada FN1**.
- Atribuições possíveis:
  - Teclado padrão (Letras, Números, Teclas F1-F12, Modificadores, Navegação).
  - Ações do Mouse (Clique Esquerdo, Direito, Meio, Avançar, Voltar, Scroll).
  - Teclas Multimídia (Play, Pause, Stop, Próxima, Anterior, Volume+, Volume-, Mute).
  - Atalhos do Sistema (Calculadora, Meu Computador, Navegador, E-mail, Busca, Bloquear PC, Área de Trabalho).
  - Vinculação direta a Macros gravadas.
  - Desativação individual de teclas (`Desativar`).
  - Restauração individual para o padrão de fábrica.

### 4. Gravador e Editor de Macros
- Gravação de digitação em tempo real com captura de intervalos milissegundos precisos.
- Inserção manual de eventos: **Tecla Pressionada (Down)**, **Tecla Solta (Up)** e **Delay (ms)**.
- Reordenação de eventos (Mover para Cima / Mover para Baixo).
- Modos de execução:
  - Executar uma vez.
  - Repetir enquanto pressionada.
  - Alternar repetição contínua (Toggle loop).
  - Repetir N vezes.

### 5. Parâmetros de Hardware & Gerenciamento de Perfis
- Ajuste de **Polling Rate**: 1000Hz (1ms), 500Hz (2ms), 250Hz (4ms) e 125Hz (8ms).
- **Win Lock**: Trava da tecla Windows para evitar saídas acidentais em jogos.
- Diagnóstico ao vivo: Número de Série, Modelo, Versão do Firmware e MCU.
- Gerenciamento de Perfis ilimitados.
- **Compatibilidade 100% com o aplicativo oficial:**
  - Exportação e Importação de XML oficial (`witmodProFile.xml`).
  - Exportação e Importação de JSON legível.
- **Reset de Fábrica Onboard** com diálogo de segurança.

---

## Como Executar

### Pré-requisitos
- Python 3.10 ou superior instalado.
- Instale as dependências:
```bash
pip install -r requirements.txt
```

### Execução no Windows
```bash
python main.py
```

### Execução no Linux
No Linux, o subsistema HID requer permissão de acesso ao dispositivo raw em `/dev/hidraw*`. Crie uma regra udev:
```bash
sudo nano /etc/udev/rules.d/99-husky-hailstorm.rules
```
Adicione a seguinte linha:
```text
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="c345", MODE="0666"
```
Recarregue as regras:
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
python3 main.py
```

### Execução no macOS
```bash
python3 main.py
```
*(Nota: Certifique-se de que o Terminal ou seu ambiente Python possua permissão em Preferências do Sistema -> Segurança e Privacidade -> Monitoramento de Entrada).*

---

## Estrutura do Código

```text
husky-storm/
├── assets/                  # Ícones oficiais e imagens extraídas da OEM
│   ├── AppLogo.ico
│   └── Keyboard_TY69SKRGB.png
├── core/                    # Núcleo de comunicação e engenharia reversa
│   ├── device.py            # Gerenciador USB HID (hidapi) e modo simulação
│   ├── keycodes.py          # Mapeamento do layout 68 teclas e códigos HID
│   ├── lighting.py          # Definições de efeitos, modos, cores e paletas
│   ├── profiles.py          # Serialização/Deserialização de perfis (JSON & XML)
│   └── protocol.py          # Construtores de pacotes binários do protocolo USB
├── docs/                    # Relatórios e strings da engenharia reversa
├── gui/                     # Interface Gráfica CustomTkinter
│   ├── app.py               # Janela principal e barra de status
│   ├── keyboard_view.py     # Canvas vetorial interativo do teclado 68 teclas
│   ├── tab_lighting.py      # Aba de efeitos de iluminação e side glow
│   ├── tab_macros.py        # Aba de criação e gravação de macros
│   ├── tab_perkey.py        # Aba do estúdio de pintura Per-Key RGB
│   ├── tab_remap.py         # Aba de remapeamento de camadas (Default/FN/FN1)
│   └── tab_settings.py      # Aba de polling rate, perfis e firmware
├── profiles/                # Armazenamento local de perfis de usuário
├── main.py                  # Ponto de entrada do executável
└── requirements.txt         # Dependências do projeto
```

---

## Licença
Distribuído sob a licença MIT. Criado como substituto livre e de código aberto para a comunidade de teclados mecânicos.
#   t e c l a d o - h u s k y - h a i l s t o r m 
 
 
