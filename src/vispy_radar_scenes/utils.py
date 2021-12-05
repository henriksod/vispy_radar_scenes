#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utils, holds util functions not coupled to a specific class
"""

import os
import enum

from pkg_resources import resource_filename
from PyQt5 import QtCore, QtWidgets


package_module_name = __name__.split('.')[:-1][0]


class ColorOpts(enum.Enum):
    """
    An enum containing the possible coloring options for the detections. This enum is used to fill the option list
    in the gui.
    """
    DOPPLER = "Doppler Velocity"
    RCS = "RCS"
    SENSORID = "Sensor ID"


class Colors:
    """
    Helper class for colors. Provides mappings from sensor ids to colors as well as colors for the individual classes.
    """
    red = "#f02b2b"
    blue = "#4763ff"
    green = "#47ff69"
    light_green = "#73ff98"
    orange = "#ff962e"
    violet = "#c561d4"
    indigo = "#8695e3"
    grey = "#7f8c8d"
    yellow = "#ffff33"
    lime = "#c6ff00"
    amber = "#ffd54f"
    teal = "#19ffd2"
    pink = "#ff6eba"
    brown = "#c97240"
    black = "#1e272e"
    midnight_blue = "#34495e"
    deep_orange = "#e64a19"
    light_blue = "#91cded"
    light_gray = "#dedede"
    gray = "#888888"

    sensor_id_to_color = {
        1: red,
        2: blue,
        3: green,
        4: pink
    }

    @staticmethod
    def color_gradient(from_color: tuple, to_color: tuple, val: float):
        return tuple(map(lambda a, b: a + (b - a) * val, from_color, to_color))

    @staticmethod
    def hex_to_rgba(hex_string: str) -> tuple:
        h = hex_string.lstrip('#').upper()
        return (tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))) + (1,)

def set_stylesheet(path):
    """
    Set the stylesheet to use the desired path in the Qt resource
    system (prefixed by `:/`) or generically (a path to a file on
    system).

    :path:      A full path to a resource or file on system
    """

    # get the QApplication instance,  or crash if not set
    app = QtWidgets.QApplication.instance()
    if app is None:
        raise RuntimeError("No Qt Application found.")

    file = QtCore.QFile(path)
    file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    stream = QtCore.QTextStream(file)
    app.setStyleSheet(stream.readAll())


def package_resource_path(sub_module, file) -> str:
    filepath = resource_filename(f'{package_module_name}.{sub_module}', file)
    filepath = os.path.abspath(filepath)
    return filepath


def load_resource_from_package(sub_module, file) -> str:
    filepath = package_resource_path(sub_module, file)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'{file} could not be found in package {package_module_name}')

    with open(filepath) as f:
        data = f.read()

    return data


def load_shader(file) -> str:
    return load_resource_from_package('gl_objects.shaders', file)

