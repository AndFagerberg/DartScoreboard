#!/usr/bin/env python3
"""
Dart Scoreboard - Touch-vänlig dartpoängräknare för Raspberry Pi

Användning:
    python main.py              # Fönsterläge (480x320)
    python main.py --fullscreen # Fullskärm (för Raspberry Pi)
    python main.py -f           # Fullskärm (kortform)
"""
import sys
import tkinter as tk
from app import DartApp


def main():
    root = tk.Tk()
    fullscreen = "--fullscreen" in sys.argv or "-f" in sys.argv
    app = DartApp(root, fullscreen=fullscreen)
    root.mainloop()


if __name__ == "__main__":
    main()

