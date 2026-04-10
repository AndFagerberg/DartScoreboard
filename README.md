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

## Raspberry Pi Installation (Lite OS, utan skrivbord)

Komplett guide för att köra Dart Scoreboard på Raspberry Pi med 3.5" pekskärm
**utan** fullständigt Desktop OS. Använder Raspberry Pi OS Lite + minimal X-server.

### Krav
- Raspberry Pi (testad på Pi 4, fungerar även på Pi 3)
- 3.5" SPI TFT pekskärm 480x320 (t.ex. Waveshare, Elegoo, KeDei)
- Micro SD-kort (8 GB+)
- Strömförsörjning

---

### Steg 1: Installera Raspberry Pi OS Lite

1. Ladda ner och installera [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Välj **Raspberry Pi OS Lite (64-bit)** (inget skrivbord)
3. Klicka kugghjulet (⚙) och konfigurera:
   - **Hostname:** dart-pi
   - **Aktivera SSH:** ja
   - **Användarnamn/lösenord:** valfritt (standard: pi)
   - **WiFi:** fyll i SSID + lösenord
4. Skriv till SD-kortet och sätt i Pi:n

---

### Steg 2: Anslut via SSH och uppdatera

```bash
ssh pi@dart-pi.local
sudo apt update && sudo apt upgrade -y
```

---

### Steg 3: Installera 3.5" pekskärm-drivrutin

De flesta 3.5" SPI-skärmar (Waveshare, Elegoo, Goodtft m.fl.) använder samma drivrutin:

```bash
# Installera git
sudo apt install -y git

# Klona LCD-drivrutinen (fungerar för de flesta 3.5" SPI-skärmar)
cd ~
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
chmod +x LCD35-show

# Installera drivrutinen (startar om Pi:n automatiskt)
sudo ./LCD35-show
```

> **Waveshare-skärm?** Använd istället:
> ```bash
> git clone https://github.com/waveshare/LCD-show.git
> cd LCD-show
> sudo ./LCD35-show
> ```

> **Om din skärm är upp-och-ner**, kör:
> ```bash
> cd ~/LCD-show
> sudo ./LCD35-show 180
> ```

Efter omstart ska skärmen visa konsol-text. Logga in via SSH igen.

---

### Steg 4: Installera X-server och beroenden (utan skrivbord)

```bash
sudo apt install -y xserver-xorg xinit x11-xserver-utils python3-tk unclutter
```

Det är allt — ingen skrivbordsmiljö behövs.

---

### Steg 5: Klona och testa appen

```bash
cd ~
git clone <repo-url> dart-scoreboard
cd dart-scoreboard/dartscoreboard

# Testa (kör från konsolen på Pi:n eller via SSH med DISPLAY-variabel)
xinit /usr/bin/python3 /home/pi/dart-scoreboard/dartscoreboard/main.py -- -nocursor
```

Appen ska nu visa sig på pekskärmen.

---

### Steg 6: Kalibrera touchscreen (om pek-koordinater är fel)

```bash
sudo apt install -y xinput-calibrator

# Starta X med kalibreringsverktyget
xinit /usr/bin/xinput_calibrator

# Notera värdena som visas och spara dem:
sudo nano /etc/X11/xorg.conf.d/99-calibration.conf
```

Fyll i med värdena du fick:

```
Section "InputClass"
    Identifier "calibration"
    MatchProduct "ADS7846 Touchscreen"
    Option "Calibration" "XXXX XXXX XXXX XXXX"
    Option "SwapAxes" "0"
EndSection
```

---

### Steg 7: Autostart vid boot

Skapa startskriptet:

```bash
sudo nano /home/pi/start-dartboard.sh
```

Innehåll:

```bash
#!/bin/sh
xset s off
xset -dpms
xset s noblank
unclutter -idle 0 &
exec python3 /home/pi/dart-scoreboard/dartscoreboard/main.py --fullscreen
```

Gör körbart:

```bash
chmod +x /home/pi/start-dartboard.sh
```

Skapa en systemd-service:

```bash
sudo nano /etc/systemd/system/dartboard.service
```

Innehåll:

```ini
[Unit]
Description=Dart Scoreboard
After=multi-user.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
ExecStart=/usr/bin/xinit /home/pi/start-dartboard.sh -- :0 -nocursor
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktivera servicen:

```bash
sudo systemctl enable dartboard.service
sudo systemctl start dartboard.service
```

---

### Steg 8: Valfria inställningar

#### Inaktivera konsolens skärmsläckare (blankning)

```bash
sudo nano /boot/cmdline.txt
```

Lägg till i slutet av raden (samma rad):

```
consoleblank=0
```

#### Rotera skärm (om behövs)

```bash
cd ~/LCD-show
sudo ./LCD35-show 90   # 90, 180 eller 270 grader
```

#### Snabbare boot (valfritt)

```bash
# Inaktivera onödiga tjänster
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
sudo systemctl disable triggerhappy
```

---

### Felsökning

| Problem | Lösning |
|---|---|
| Vit/svart skärm | Kontrollera att LCD-drivrutinen installerades korrekt, kör `sudo ./LCD35-show` igen |
| Touch fungerar inte | Kontrollera SPI: `ls /dev/spi*` ska visa enheter. Kör `sudo raspi-config` → Interface → SPI → Enable |
| Touch är spegelvänd | Kalibrera med `xinput_calibrator` (steg 6) eller kör `sudo ./LCD35-show 180` |
| Appen startar inte | Kolla loggar: `journalctl -u dartboard.service -f` |
| "No module named tkinter" | `sudo apt install python3-tk` |

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
