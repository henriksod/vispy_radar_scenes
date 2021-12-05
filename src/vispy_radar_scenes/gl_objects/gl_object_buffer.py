#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GL_ObjectBuffer is an abstract class that contains common functionality for objects using VertexBuffer
"""

import numpy as np

from abc import ABC, abstractmethod
from vispy import gloo

from ..utils import load_shader


class GLObjectBuffer(ABC):
    @abstractmethod
    def __init__(self, buffer_size: int):
        self.buffer_size = buffer_size
        self._program = None

    def load_program(self, vert_file, frag_file, geom_file=None):
        vertex_shader = load_shader(vert_file)
        fragment_shader = load_shader(frag_file)

        self._program = gloo.Program(vertex_shader, fragment_shader)
        if geom_file:
            geometry_shader = load_shader(geom_file)
            self._program.set_shaders(vertex_shader, fragment_shader, geometry_shader)
        self._program.bind(self.vbo)

    def update(self):
        self.vbo.set_data(self.data)

    @property
    def program(self):
        return self._program

    @property
    def visible(self):
        if not hasattr(self, '_visible'):
            self._visible = True
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    @property
    def model(self):
        if not hasattr(self, '_model'):
            self._model = np.eye(4, dtype=np.float32)
            self.program['u_model'] = self._model
        return self._model

    @model.setter
    def model(self, value):
        self._model = value
        self.program['u_model'] = self._model

    @property
    def view(self):
        if not hasattr(self, '_view'):
            self._view = np.eye(4, dtype=np.float32)
            self.program['u_view'] = self._view
        return self._view

    @view.setter
    def view(self, value):
        self._view = value
        self.program['u_view'] = self._view

    @property
    def projection(self):
        if not hasattr(self, '_projection'):
            self._projection = np.eye(4, dtype=np.float32)
            self.program['u_projection'] = self._projection
        return self._projection

    @projection.setter
    def projection(self, value):
        self._projection = value
        self.program['u_projection'] = self._projection

    @property
    def scale(self):
        if not hasattr(self, '_scale'):
            self._scale = 1
            self.program['u_scale'] = self._scale
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.program['u_scale'] = self._scale

    @property
    @abstractmethod
    def type(self) -> str:
        """Type of primitive to draw in shader program"""
        pass

    @property
    @abstractmethod
    def data(self) -> np.ndarray:
        """Data property which is used by the VertexBuffer"""
        pass

    @property
    def vbo(self):
        """Vertex Buffer Object"""
        if not hasattr(self, '_vbo'):
            self._vbo = gloo.VertexBuffer(self.data)
        return self._vbo