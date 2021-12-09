#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GL_RadarDetections inherits GL_ObjectBuffer and provides a way to visualize detections
"""

import numpy as np

from .gl_object_buffer import GLObjectBuffer


class GLParentObject(GLObjectBuffer):
    vertex_shader_file: str = 'line_vertex.glsl'
    fragment_shader_file: str = 'line_fragment.glsl'

    u_linewidth: float = 1.0

    def __init__(self, buffer_size: int = 1):
        super().__init__(buffer_size)

        self.load_program(self.vertex_shader_file,
                          self.fragment_shader_file)

        self.program['u_linewidth'] = self.u_linewidth

    @property
    def type(self):
        return 'lines'

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = \
                np.zeros(self.buffer_size, [('a_position', np.float32, 3),
                                            ('a_color', np.float32, 4)])
        return self._data