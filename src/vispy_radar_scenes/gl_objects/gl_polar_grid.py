#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GL_RadarDetections inherits GL_ObjectBuffer and provides a way to visualize detections
"""

import numpy as np

from ..settings import Settings

from .gl_object_buffer import GLObjectBuffer
from .gl_circle import GLCircle


class GLPolarGrid(GLObjectBuffer):
    vertex_shader_file: str = 'line_vertex.glsl'
    fragment_shader_file: str = 'line_fragment.glsl'

    u_linewidth: float = 1.0

    def __init__(self, settings: Settings, buffer_size: int = 2000):
        super().__init__(buffer_size)
        self.settings = settings

        self.load_program(self.vertex_shader_file,
                          self.fragment_shader_file)

        self.program['u_linewidth'] = self.u_linewidth

        min_circle_range = 10
        max_circle_range = 100
        num_circles = 5
        for i in range(num_circles + 1):
            circle = GLCircle()
            circle_range = min_circle_range + (max_circle_range - min_circle_range) * (i / float(num_circles))
            circle.radius = circle_range
            circle.data['a_color'] = self.settings.grid_circle_color
            self.add_child(f'circle_{i}', circle)
            circle.update()

    @property
    def type(self):
        return 'points'

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = \
                np.zeros(self.buffer_size, [('a_position', np.float32, 3),
                                            ('a_color', np.float32, 4)])
        return self._data