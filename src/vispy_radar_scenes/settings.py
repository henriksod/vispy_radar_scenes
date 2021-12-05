#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Settings dataclass. Holds settings for the visualization tool during runtime.
"""

from dataclasses import dataclass

@dataclass
class Settings:
    program_title: str = "Radar Data Viewer"
    dark_mode: bool = True
    dark_stylesheet: str = ":/dark/stylesheet.qss"
    light_stylesheet: str = ":/light/stylesheet.qss"
    canvas_light_mode_clear_color: tuple = (0.05, 0.05, 0.08, 1.0)
    canvas_dark_mode_clear_color: tuple = (0.05, 0.05, 0.08, 1.0)
    grid_circle_color: tuple = (0.15, 0.15, 0.18, 1.0)
    doppler_arrow_scale: float = 0.2
    draw_doppler_arrows: bool = True
