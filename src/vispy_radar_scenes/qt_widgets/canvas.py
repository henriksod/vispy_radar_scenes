#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Vispy Canvas which draws data using Open GL
"""

import numpy as np

from typing import Dict
from vispy import app, gloo

from vispy.util.transforms import perspective, translate, rotate

from ..settings import Settings
from ..utils import ColorOpts, Colors
from ..gl_objects import GLObjectBuffer, GLRadarDetections, GLRadarDopplerLines, GLCircle

from radar_scenes.sensors import get_mounting

#gloo.gl.use_gl('gl+')


class Canvas(app.Canvas):

    gl_object_buffer: Dict[str, GLObjectBuffer] = {}

    def __init__(self, settings: Settings):
        app.Canvas.__init__(self, keys='interactive', size=(800, 600))
        self.settings = settings

        self.gl_object_buffer['detection_points'] = GLRadarDetections()
        self.gl_object_buffer['detection_vel_lines'] = GLRadarDopplerLines()

        min_circle_range = 10
        max_circle_range = 100
        num_circles = 5
        for i in range(num_circles+1):
            circle = GLCircle()
            circle_range = min_circle_range + (max_circle_range - min_circle_range) * (i/float(num_circles))
            circle.radius = circle_range
            circle.data['a_color'] = self.settings.grid_circle_color
            circle.update()
            self.gl_object_buffer[str(f'circle_{i}')] = circle

        # Move back camera (zoom)
        # TODO: This is probably not the right way to zoom.
        self.translate = 100

        for obj in self.gl_object_buffer.values():
            obj.model = rotate(90, (0, 0, 1))

        self.update_object_scaling()
        self.apply_zoom()

        if self.settings.dark_mode:
            gloo.set_state('translucent', clear_color=self.settings.canvas_dark_mode_clear_color)
        else:
            gloo.set_state('translucent', clear_color=self.settings.canvas_light_mode_clear_color)

    def on_toggle_dark_mode(self):
        if self.settings.dark_mode:
            gloo.set_state('translucent', clear_color=self.settings.canvas_light_mode_clear_color)
        else:
            gloo.set_state('translucent', clear_color=self.settings.canvas_dark_mode_clear_color)

    """
    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()
    """

    def on_resize(self, event):
        self.apply_zoom()

    def on_mouse_wheel(self, event):
        self.translate -= event.delta[1] * 5
        self.translate = max(2, self.translate)

        self.update_object_scaling()

        self.update()

    def on_draw(self, event):
        gloo.clear()
        for obj in self.gl_object_buffer.values():
            obj.program.draw(obj.type)

    def apply_zoom(self):
        gloo.set_viewport(0, 0, self.physical_size[0], self.physical_size[1])
        for obj in self.gl_object_buffer.values():
            obj.projection = perspective(45.0, self.size[0] /
                                         float(self.size[1]), 1.0, 1000.0)

    def update_object_scaling(self):
        for obj in self.gl_object_buffer.values():
            obj.view = translate((0, 0, -self.translate))
            obj.scale = max(1/100.0, (1/self.translate) * min(500, self.translate)/500)

    def update_scene(self, radar_data, color_by):
        n = len(radar_data["x_cc"])

        sensor_id = radar_data["sensor_id"]
        azimuth_sc = radar_data["azimuth_sc"]
        rcs = radar_data["rcs"]
        x_cc = radar_data["x_cc"]
        y_cc = radar_data["y_cc"]
        velocity_compensated = radar_data["vr_compensated"]

        sensor_yaw = np.array([get_mounting(s_id)["yaw"] for s_id in sensor_id])

        detections = self.gl_object_buffer['detection_points']
        lines = self.gl_object_buffer['detection_vel_lines']

        detections.data['a_position'] = np.zeros((detections.buffer_size, 3))
        detections.data['a_position'][:n, 0] = x_cc
        detections.data['a_position'][:n, 1] = y_cc
        # TODO: Move these to settings
        standard_size = 300
        rcs_scaling = 10
        detections.data['a_size'][:n] = \
            self.pixel_scale * (standard_size + rcs_scaling*(rcs-np.min(rcs)))

        if self.settings.dark_mode:
            detections.data['a_fg_color'] = self.settings.canvas_dark_mode_clear_color
        else:
            detections.data['a_fg_color'] = self.settings.canvas_light_mode_clear_color

        detections.data['a_fg_color'][n:][-1] = 0

        if color_by == ColorOpts.SENSORID.value:
            colors = [Colors.hex_to_rgba(Colors.sensor_id_to_color[x['sensor_id']]) for x in radar_data]
            detections.data['a_bg_color'][:n] = colors
            lines.data['a_color'][:n * 2:2] = colors
            lines.data['a_color'][1:n * 2:2] = colors
        elif color_by == ColorOpts.DOPPLER.value:
            base_color_positive = Colors.hex_to_rgba(Colors.red)
            base_color_negative = Colors.hex_to_rgba(Colors.blue)
            doppler_vals = radar_data["vr_compensated"]
            doppler_vals = np.clip(doppler_vals, -10, 10)
            doppler_vals = 1 / 20.0 * (doppler_vals + 10)
            colors = list(map(lambda val: Colors.color_gradient(
                            base_color_negative, base_color_positive, val), doppler_vals))
            detections.data['a_bg_color'][:n] = colors
            lines.data['a_color'][:n * 2:2] = colors
            lines.data['a_color'][1:n * 2:2] = colors
        elif color_by == ColorOpts.RCS.value:
            base_color = Colors.hex_to_rgba(Colors.green)
            rcs_vals = radar_data["rcs"]
            rcs_vals = np.clip(rcs_vals, -20, 20)
            rcs_vals = 1 / 40.0 * (rcs_vals + 20)
            colors = list(map(lambda val: tuple(val*x for x in base_color), rcs_vals))
            detections.data['a_bg_color'][:n] = colors
            lines.data['a_color'][:n * 2:2] = colors
            lines.data['a_color'][1:n * 2:2] = colors
        else:
            detections.data['a_bg_color'] = 0.95, 0.95, 1, 1
            lines.data['a_color'] = 0.95, 0.95, 1, 1

        detections.data['a_bg_color'][n:][-1] = 0
        lines.data['a_color'][n * 2:][-1] = 0


        if self.settings.draw_doppler_arrows:
            lines.visible = True
            lines.data['a_position'] = np.zeros((detections.buffer_size, 3))
            lines.data['a_position'][:n*2:2, 0] = x_cc
            lines.data['a_position'][:n*2:2, 1] = y_cc

            vx = velocity_compensated * np.cos(azimuth_sc + sensor_yaw)
            vy = velocity_compensated * np.sin(azimuth_sc + sensor_yaw)

            scale = self.settings.doppler_arrow_scale
            lines.data['a_position'][1:n*2:2, 0] = x_cc + scale * vx
            lines.data['a_position'][1:n*2:2, 1] = y_cc + scale * vy
        else:
            lines.visible = False

        #circle_20m.update()
        lines.update()
        detections.update()

        self.update()
