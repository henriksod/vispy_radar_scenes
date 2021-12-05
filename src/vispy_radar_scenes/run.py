#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Runs the visualization tool
"""

import sys
import argparse

from vispy import app

from .qt_widgets import MainWindow, Canvas
from .settings import Settings


# ----------------- MAIN ---------------------------------------
def main():
    parser = argparse.ArgumentParser(description='Radar Data Viewer.\nCopyright 2021 Ole Schumann')
    parser.add_argument("filename", nargs="?", default="", type=str,
                        help="Path to a *.json or *.h5 file of the radar data set.")

    args = parser.parse_args()
    
    settings = Settings()
    c = Canvas(settings)
    w = MainWindow(settings, c)
    w.show()
    
    w.load_sequence(args.filename)
    
    app.run()


if __name__ == '__main__':
    main()
