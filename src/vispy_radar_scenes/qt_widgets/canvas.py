#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Vispy Canvas which draws data using Open GL
"""

import numpy as np

from typing import Dict
from vispy import app, gloo

from vispy.util.transforms import perspective, translate, rotate

from ..settings import Settings
from ..utils import ColorOpts, Colors, package_resource_path
from ..gl_objects import GLRadarDetections, GLRadarDopplerLines, GLPolarGrid, GLParentObject, GLMeshObject, GLLine

from radar_scenes.sensors import get_mounting

#gloo.gl.use_gl('gl+')


class Canvas(app.Canvas):

    gl_parent = GLParentObject()

    label_id_to_display_name = {
        0: "Car",
        1: "Large Veh.",
        2: "Truck",
        3: "Bus",
        4: "Train",
        5: "Bicycle",
        6: "Motorbike",
        7: "Pedestrian",
        8: "Ped. Group",
        9: "Animal",
        10: "Other",
        11: "Static"
    }

    def __init__(self, settings: Settings):
        app.Canvas.__init__(self, keys='interactive', size=(800, 600))
        self.settings = settings
        self.radar_data = None
        self.info_label = None

        self.gl_parent.add_child('detection_points', GLRadarDetections())
        self.gl_parent.add_child('detection_vel_lines', GLRadarDopplerLines())
        self.gl_parent.add_child('polar_grid', GLPolarGrid(settings=self.settings))
        self.gl_parent.add_child('car', GLMeshObject(model_path=package_resource_path('res', 'car.stl')))

        # Move back camera (zoom)
        # TODO: This is probably not the right way to zoom.
        self.translate = 100
        self.prev_translate = 0

        self.gl_parent.view = self.gl_parent.view @ rotate(90, (0, 0, 1))

        self.update_object_scaling()
        self.apply_zoom()
        self.gl_parent.update()
        self.update()

        gloo.set_state(depth_test=True, blend=False, cull_face=True)

        self.events.mouse_press.connect(self.mouse_press_event)
        self.events.mouse_release.connect(self.mouse_release_event)

        if self.settings.dark_mode:
            gloo.set_state('translucent', clear_color=self.settings.canvas_dark_mode_clear_color)
        else:
            gloo.set_state('translucent', clear_color=self.settings.canvas_light_mode_clear_color)

    def on_toggle_dark_mode(self):
        if self.settings.dark_mode:
            gloo.set_state('translucent', clear_color=self.settings.canvas_light_mode_clear_color)
        else:
            gloo.set_state('translucent', clear_color=self.settings.canvas_dark_mode_clear_color)

    def mouse_press_event(self, event):
        mouse_ray, camera_pos = self.screen_to_world(event.pos)
        num_detections = len(self.radar_data["x_cc"])
        detections = self.gl_parent.lookup_child('detection_points')
        detections.data['a_selected'] = 0
        min_d = 1
        min_i = 0
        for i, point in enumerate(detections.data['a_position'][:num_detections]):
            d = self.point_to_line_distance(point, camera_pos, mouse_ray)
            if d < min_d:
                min_d = d
                min_i = i
        if min_d < 1:
            detections.data['a_selected'][min_i] = 1
            if self.info_label:
                tr_id = self.radar_data["track_id"][min_i].decode()
                if len(tr_id) == 0:
                    tr_id = "<None>"
                info_text = (
                    "UUID = {}\nSensor ID = {}\nTimestamp = {}\nRange = {:.3f} m\nAzimuth = {:.3f}°\nRCS = {:.3f} dBsm\n"
                    "x (cc) = {:.3f} m\ny (cc) = {:.3f} m\nRadial Velocity = {:.3f} m/s\n"
                    "Compensated Rad. Vel. = {:.3f} m/s\n"
                    "Label ID = {} ({})\nTrack ID = {}").format(
                    self.radar_data["uuid"][min_i].decode(), self.radar_data["sensor_id"][min_i], self.radar_data["timestamp"][min_i], self.radar_data["range_sc"][min_i],
                    np.rad2deg(self.radar_data["azimuth_sc"][min_i]), self.radar_data["rcs"][min_i], self.radar_data["x_cc"][min_i], self.radar_data["y_cc"][min_i],
                    self.radar_data["vr"][min_i], self.radar_data["vr_compensated"][min_i], self.radar_data["label_id"][min_i],
                    self.label_id_to_display_name[self.radar_data["label_id"][min_i]], tr_id
                )
                self.info_label.setText(info_text)
        elif self.info_label:
            self.info_label.setText("No detection selected.")
        self.gl_parent.update()
        self.update()

    def mouse_release_event(self, event):
        pass
        #mouse_ray, camera_pos = self.screen_to_world(event.pos)
        #print(f'mouse release! {mouse_ray}')

    def point_to_line_distance(self, point, line_origin, line_direction):
        return np.linalg.norm(np.cross(line_origin - point, line_direction)) / np.linalg.norm(line_direction)

    def screen_to_world(self, point: tuple):
        invV = np.linalg.inv(self.gl_parent.view)
        invP = np.linalg.inv(self.gl_parent.projection)
        w, h = self.size
        x, y = point
        ray_clip = np.array([(2 * x) / w - 1, 1 - (2 * y) / h, 1, 1])
        ray_eye = invP @ ray_clip
        ray_eye = np.array([ray_eye[0], ray_eye[1], 1, 1])
        ray_wor = invV @ ray_eye
        camera_pos = np.array([0, 0, 0, 1]) @ invV
        return -ray_wor[:3]/np.linalg.norm(ray_wor[:3]), camera_pos[:3]

    def on_key_press(self, event):

        if event.text == 'q':
            self.gl_parent.view = self.gl_parent.view @ rotate(.5, (0, 0, 1))
        elif event.text == 'e':
            self.gl_parent.view = self.gl_parent.view @ rotate(-.5, (0, 0, 1))

        self.gl_parent.update()
        self.update()

    def on_resize(self, event):
        self.apply_zoom()

    def on_mouse_wheel(self, event):
        self.translate -= event.delta[1] * 5
        self.translate = max(2, self.translate)

        self.update_object_scaling()
        self.gl_parent.update()
        self.update()

    def on_draw(self, event):
        gloo.clear()
        self.gl_parent.draw()

    def apply_zoom(self):
        gloo.set_viewport(0, 0, self.physical_size[0], self.physical_size[1])
        self.gl_parent.projection = perspective(45.0, self.size[0] /
                                                float(self.size[1]), 1.0, 1000.0)

    def update_object_scaling(self):
        self.gl_parent.view = self.gl_parent.view @ translate((0, 0, self.prev_translate-self.translate))
        self.prev_translate = self.translate
        #TODO: Only modify uniform scale for detections?
        self.gl_parent.uniform_scale = max(1 / 100.0, (1 / self.translate) * min(500, self.translate) / 500)

    def update_scene(self, radar_data, color_by):
        self.radar_data = radar_data
        n = len(radar_data["x_cc"])

        sensor_id = radar_data["sensor_id"]
        azimuth_sc = radar_data["azimuth_sc"]
        rcs = radar_data["rcs"]
        x_cc = radar_data["x_cc"]
        y_cc = radar_data["y_cc"]
        velocity_compensated = radar_data["vr_compensated"]

        sensor_yaw = np.array([get_mounting(s_id)["yaw"] for s_id in sensor_id])

        detections = self.gl_parent.lookup_child('detection_points')
        lines = self.gl_parent.lookup_child('detection_vel_lines')

        detections.data['a_position'] = np.zeros((detections.buffer_size, 3))
        detections.data['a_position'][:n, 0] = x_cc
        detections.data['a_position'][:n, 1] = y_cc
        # TODO: Move these to settings
        standard_size = 300
        rcs_scaling = 10
        detections.data['a_size'][:n] = \
            self.pixel_scale * (standard_size + rcs_scaling*(rcs-np.min(rcs)))

        detections.data['a_selected'] = 0
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

        self.gl_parent.update()
        self.update()
