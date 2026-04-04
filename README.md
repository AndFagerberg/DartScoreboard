# Dart Scoreboard

Touch-vänlig dartpoängräknare för Raspberry Pi med 480x320 pekskärm.

## Funktioner

### Speltyper
- **X01** (301, 501, 701) - Klassiskt dart med valfri Double Out
- **Cricket** - Stäng 15-20 och Bull, samla poäng
- **Around the Clock** - Träffa 1-20 i ordning, sedan Bull

### Övrigt
- 1-4 spelare
- Touch-vänligt gränssnitt (inga tangentbord behövs)
- Fördefinierade spelarnamn
- Checkout-förslag för X01
- Ångra-funktion
- Statistik (snitt per runda)
- Mörkt tema optimerat för skärm

## Filstruktur

```
dartscoreboard/
├── main.py           # Entry point
├── app.py            # Huvudapplikation
├── constants.py      # Färger, namn, checkouts
└── games/
    ├── __init__.py
    ├── x01.py        # X01-spel
    ├── cricket.py    # Cricket
    └── clock.py      # Around the Clock
```

## Kör lokalt (utveckling)

```bash
# Fönsterläge 480x320
python main.py

# Fullskärm
python main.py --fullscreen
python main.py -f
```

## Raspberry Pi Installation

### Krav
- Raspberry Pi (testad på Pi 4, fungerar även på Pi 3)
- 480x320 pekskärm (t.ex. 3.5" TFT)
- Raspberry Pi OS med desktop

### Installera

```bash
# Klona repot
cd ~
git clone <repo-url> dart-scoreboard
cd dart-scoreboard/dartscoreboard

# Testa att det fungerar
python3 main.py --fullscreen
```

### Autostart vid boot

Redigera autostart-filen:

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Lägg till i slutet:

```
@python3 /home/pi/dart-scoreboard/dartscoreboard/main.py --fullscreen
```

### Inaktivera skärmsläckare

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Lägg till:

```
@xset s off
@xset -dpms
@xset s noblank
```

### Dölj muspekare (valfritt)

```bash
sudo apt install unclutter
```

Lägg till i autostart:

```
@unclutter -idle 0
```

### Rotera skärm (om behövs)

Redigera config:

```bash
sudo nano /boot/config.txt
```

Lägg till:

```
display_rotate=1  # 90 grader
# eller
display_rotate=3  # 270 grader
```

## Anpassa

### Lägg till spelarnamn

Redigera `constants.py`:

```python
PRESET_NAMES = [
    "Spelare 1", "Spelare 2", ...
    "Ditt Namn", "Annat Namn",
]
```

### Ändra färger

Redigera `COLORS` i `constants.py`:

```python
COLORS = {
    'bg': '#1a1a2e',        # Bakgrund
    'accent': '#e94560',    # Accentfärg
    'text': '#eaeaea',      # Text
    ...
}
```

## Licens

MIT
