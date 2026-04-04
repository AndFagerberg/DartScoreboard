# Dart Scoreboard (Raspberry Pi)

Touchscreen dart scoreboard (480x320).

## Features
- 1-4 players
- 301 / 501 / 701
- Score per dart
- Touch UI

## Run
python3 main.py

## Autostart (Raspberry Pi)

Edit:
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart

Add:
@python3 /home/pi/dart-scoreboard/main.py
