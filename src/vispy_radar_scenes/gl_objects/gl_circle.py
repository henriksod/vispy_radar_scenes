#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GL_RadarDetections inherits GL_ObjectBuffer and provides a way to visualize detections
"""

import numpy as np

from .gl_object_buffer import GLObjectBuffer


class GLCircle(GLObjectBuffer):
    vertex_shader_file: str = 'line_vertex.glsl'
    fragment_shader_file: str = 'line_fragment.glsl'

    u_linewidth: float = 1.0

    def __init__(self, buffer_size: int = 500):
        super().__init__(buffer_size)

        self.load_program(self.vertex_shader_file,
                          self.fragment_shader_file)

        self.program['u_linewidth'] = self.u_linewidth

    def update(self):
        self._construct_circle()
        super().update()

    def _construct_circle(self):
        num_segments = self.buffer_size
        for i in range(num_segments):
            theta = 2.0 * np.pi * float(i) / num_segments
            x = self.radius * np.cos(theta)
            y = self.radius * np.sin(theta)
            self.data['a_position'][i, 0] = x + self.center_position[0]
            self.data['a_position'][i, 1] = y + self.center_position[1]

    @property
    def radius(self):
        if not hasattr(self, '_radius'):
            self._radius = 1.0
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def center_position(self):
        if not hasattr(self, '_center_position'):
            self._center_position = (0, 0)
        return self._center_position

    @center_position.setter
    def center_position(self, value):
        self._center_position = value

    @property
    def type(self):
        return 'line_loop'

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = \
                np.zeros(self.buffer_size, [('a_position', np.float32, 3),
                                            ('a_color', np.float32, 4)])
        return self._data