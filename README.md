# Dart Scoreboard

Touch-vänlig dartpoängräknare för Raspberry Pi med 480x320 pekskärm.

## Funktioner

### Speltyper
- **X01** (301, 501, 701) - Klassiskt dart med valfri Double Out
- **Cricket** - Stäng 15-20 och Bull, samla poäng
- **Around the Clock** - Träffa 1-20 i ordning, sedan Bull
- **Killer** - Bli Killer (double), eliminera andras liv
- **Triple Killer** - Samma som Killer men med trippel istället för dubbel
- **Hits Killer** - 3 träffar för att bli Killer, träffa andras nummer före = eliminerad
- **Shanghai** - 20 rundor, runda = mål. Single+Double+Triple = direkt vinst!
- **Halve It** - 9 mål, missa = poängen halveras
- **High Score** - 10 rundor, högst totalpoäng vinner
- **Golf** - 9 hål, lägst poäng vinner

### Övrigt
- 1-4 spelare
- Touch-vänligt gränssnitt (inga tangentbord behövs)
- Fördefinierade spelarnamn
- Checkout-förslag för X01
- Ångra-funktion
- Statistik (snitt per runda)
- Mörkt tema optimerat för skärm
- **Resultatlagring** — alla färdigspelade matcher sparas automatiskt till `results.json`
- **Statistik-rapporter** — topplista, senaste matcher och detaljerad spelarstatistik per speltyp

## Filstruktur

```
dartscoreboard/
├── main.py           # Entry point
├── app.py            # Huvudapplikation
├── constants.py      # Färger, namn, checkouts
├── results_store.py  # Sparar & läser matchresultat (JSON)
├── results.json      # Matchhistorik (skapas automatiskt)
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
**utan** fullständigt Desktop OS. Använder Raspberry Pi OS Lite + LCD-show-drivrutin.

LCD-show-skriptet sätter automatiskt upp auto-login och `startx` vid boot.
Vi behöver bara tala om för X *vad* den ska starta (vår app via `~/.xinitrc`).

### Krav
- Raspberry Pi (testad på Pi 4, fungerar även på Pi 3)
- 3.5" SPI TFT pekskärm 480x320 (t.ex. Waveshare, Elegoo, Goodtft)
- Micro SD-kort (8 GB+)
- Strömförsörjning
- Dator med SSH-klient (för att konfigurera Pi:n)

---

### Steg 1: Installera Raspberry Pi OS Lite

1. Ladda ner och installera [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Välj **Raspberry Pi OS Lite (32-bit)** (inget skrivbord)
3. Klicka kugghjulet (⚙) och konfigurera:
   - **Hostname:** dart-pi
   - **Aktivera SSH:** ja
   - **Användarnamn:** dart (eller valfritt)
   - **Lösenord:** valfritt
   - **WiFi:** fyll i SSID + lösenord
4. Skriv till SD-kortet och sätt i Pi:n

---

### Steg 2: Anslut via SSH och uppdatera

```bash
ssh dart@dart-pi.local
sudo apt update && sudo apt upgrade -y
```

---

### Steg 3: Installera beroenden

```bash
sudo apt install -y git xserver-xorg xinit x11-xserver-utils python3-tk unclutter
```

---

### Steg 4: Installera 3.5" pekskärm-drivrutin

```bash
cd ~
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
chmod +x LCD35-show
sudo ./LCD35-show
```

> **Waveshare-skärm?** Byt URL till `https://github.com/waveshare/LCD-show.git`
>
> **Skärmen upp-och-ner?** Kör `sudo ./LCD35-show 180` istället.

Pi:n startar om automatiskt. LCD-show gör följande åt oss:
- Installerar rätt device tree overlay för skärmen (fb1)
- Sätter upp auto-login på tty1
- Lägger till `startx` i `~/.bash_profile`

> **OBS:** LCD-show konfigurerar *inte* Xorg att använda fb1 — det fixar vi i steg 5.

SSH:a in igen:

```bash
ssh dart@dart-pi.local
```

---

### Steg 5: Konfigurera X-server för SPI-skärmen

LCD-show lägger `startx` i `.bash_profile` men den:
- Pekar X på HDMI (fb0) istället för SPI-skärmen (fb1)
- Blockerar SSH-prompten

**5a.** Fixa ägaren på `.bash_profile` (LCD-show skapar den som root):

```bash
sudo chown $USER:$USER ~/.bash_profile
```

**5b.** Skriv över `.bash_profile` — peka på fb1 och skydda SSH:

```bash
cat > ~/.bash_profile << 'PROFILE'
export FRAMEBUFFER=/dev/fb1
if [ -z "$SSH_CLIENT" ] && [ -z "$SSH_TTY" ]; then
    startx 2> /tmp/log_output.txt
fi
PROFILE
```

**5c.** Tillåt X-server att startas:

```bash
sudo bash -c 'cat > /etc/X11/Xwrapper.config << XWRAP
allowed_users=anybody
needs_root_rights=yes
XWRAP'
```

**5d.** Skapa Xorg-config som pekar X på SPI-skärmens framebuffer:

```bash
sudo bash -c 'cat > /etc/X11/xorg.conf.d/99-fbdev.conf << CONF
Section "Device"
    Identifier "LCD"
    Driver "fbdev"
    Option "fbdev" "/dev/fb1"
EndSection
CONF'
```

---

### Steg 6: Klona appen

```bash
cd ~
git clone <repo-url> dart-scoreboard
```

---

### Steg 7: Skapa ~/.xinitrc (talar om för X att starta appen)

`startx` läser `~/.xinitrc` för att veta vad den ska köra.
Utan den filen startas en vanlig xterm. Vi skapar filen så appen startas istället:

```bash
cat > ~/.xinitrc << 'EOF'
#!/bin/sh
# Hämta senaste versionen vid varje start
cd ~/dart-scoreboard && git pull --ff-only 2>/dev/null

xset s off
xset -dpms
xset s noblank
unclutter -idle 0 &
exec python3 ~/dart-scoreboard/main.py --fullscreen
EOF
```

---

### Steg 8: Testa

```bash
sudo reboot
```

Appen ska nu starta automatiskt på 3.5"-skärmen vid boot.

**Om du vill testa manuellt** (utan reboot):

```bash
# Döda eventuell redan-igång X-server
sudo killall Xorg 2>/dev/null
sudo rm -f /tmp/.X0-lock
# Starta
startx
```

---

### Steg 8: Valfria inställningar

#### Inaktivera skärmblankning

```bash
sudo nano /boot/cmdline.txt
```

Lägg till i slutet av raden (samma rad, separerat med mellanslag):

```
consoleblank=0
```

#### Rotera skärm (om behövs)

```bash
cd ~/LCD-show
sudo ./LCD35-show 90   # 90, 180 eller 270 grader
```

#### Snabbare boot

```bash
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
sudo systemctl disable triggerhappy
```

#### Kalibrera touchscreen (om pek-koordinater är fel)

```bash
sudo apt install -y xinput-calibrator
# Döda appen, starta kalibreringsverktyg i X
sudo killall python3
DISPLAY=:0 xinput_calibrator
```

Notera värdena och spara:

```bash
sudo mkdir -p /etc/X11/xorg.conf.d
sudo nano /etc/X11/xorg.conf.d/99-calibration.conf
```

```
Section "InputClass"
    Identifier "calibration"
    MatchProduct "ADS7846 Touchscreen"
    Option "Calibration" "XXXX XXXX XXXX XXXX"
    Option "SwapAxes" "0"
EndSection
```

#### SSH-åtkomst medan appen kör

Appen tar bara över 3.5"-skärmen. SSH fungerar alltid:

```bash
ssh dart@dart-pi.local
```

#### Stoppa/starta om appen via SSH

```bash
# Stoppa appen (tar dig tillbaka till konsol)
sudo killall python3

# Starta appen igen
startx
```

---

### Felsökning

| Problem | Lösning |
|---|---|
| Skärmen visar ingenting | Kolla att LCD-drivrutinen installerades: `ls /dev/fb*` ska visa fb0 och/eller fb1 |
| Konsol på HDMI, inte 3.5" | Kör `cd ~/LCD-show && sudo ./LCD35-show` igen |
| "no display name" fel | Kör inte `python main.py` direkt — använd `startx` |
| Touch fungerar inte | `sudo raspi-config` → Interface → SPI → Enable, sedan reboot |
| Touch spegelvänd | Kalibrera (se ovan) eller `sudo ./LCD35-show 180` |
| "No module named tkinter" | `sudo apt install python3-tk` |
| Appen syns på HDMI | Skapa `/etc/X11/xorg.conf.d/99-fbdev.conf` med `Option "fbdev" "/dev/fb1"` (se steg 5d) |
| Vill ha prompt istället för app | Ta bort `~/.xinitrc`: `rm ~/.xinitrc && sudo reboot` |

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
