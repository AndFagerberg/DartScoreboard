#!/usr/bin/env python3
"""
Dart Scoreboard - Touch-vänlig dartpoängräknare för Raspberry Pi

Användning:
    python main.py                        # Fönsterläge (480x320)
    python main.py --fullscreen           # Fullskärm (för Raspberry Pi)
    python main.py -f                     # Fullskärm (kortform)
    python main.py -f --resolution 800x480  # Fullskärm med explicit upplösning
"""
import sys
import tkinter as tk
from app import DartApp


def main():
    root = tk.Tk()
    fullscreen = "--fullscreen" in sys.argv or "-f" in sys.argv

    resolution = None
    for i, arg in enumerate(sys.argv):
        if arg == "--resolution" and i + 1 < len(sys.argv):
            try:
                w, h = sys.argv[i + 1].split("x")
                resolution = (int(w), int(h))
            except ValueError:
                pass

    app = DartApp(root, fullscreen=fullscreen, resolution=resolution)
    root.mainloop()


if __name__ == "__main__":
    main()

