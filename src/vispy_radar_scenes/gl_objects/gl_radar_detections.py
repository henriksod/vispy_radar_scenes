#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GL_RadarDetections inherits GL_ObjectBuffer and provides a way to visualize detections
"""

import numpy as np

from .gl_object_buffer import GLObjectBuffer


class GLRadarDetections(GLObjectBuffer):
    vertex_shader_file: str = 'detection_vertex.glsl'
    fragment_shader_file: str = 'detection_fragment.glsl'

    u_linewidth: float = 0.1
    u_antialias: float = 1.0
    u_linewidth_selected: float = 2.0
    a_fg_color: tuple = (0.05, 0.05, 0.08, 1.0)
    a_fg_color_selected: tuple = (0.2, 0.2, 1, 1.0)

    def __init__(self, buffer_size: int = 50000):
        super().__init__(buffer_size)

        self.load_program(self.vertex_shader_file,
                          self.fragment_shader_file)

        self.program['u_linewidth'] = self.u_linewidth
        self.program['u_antialias'] = self.u_antialias
        self.program['u_linewidth_selected'] = self.u_linewidth_selected
        self.data['a_fg_color'] = self.a_fg_color
        self.data['a_fg_color_selected'] = self.a_fg_color_selected

    @property
    def type(self):
        return 'points'

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = \
                np.zeros(self.buffer_size, [('a_position', np.float32, 3),
                                            ('a_bg_color', np.float32, 4),
                                            ('a_fg_color', np.float32, 4),
                                            ('a_fg_color_selected', np.float32, 4),
                                            ('a_size', np.float32),
                                            ('a_selected', np.float32)])
        return self._data