#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GLObjectBuffer is an abstract class that contains common functionality for objects using VertexBuffer
   GLObjectBuffer can belong to a parent and hold children. Operations on an instance of GLObjectBuffer
   also affects its children.
"""

from __future__ import annotations

import numpy as np

from abc import ABC, abstractmethod
from vispy import gloo
from vispy.util.transforms import rotate, scale, transform

from ..utils import load_shader
from ..custom_types import maybe


class NoParentError(Exception):
    """Raised when trying to access undefined parent"""


class NoShaderProgramError(Exception):
    """Raised when trying to access undefined parent"""


class GLObjectBuffer(ABC):

    _children_dict: dict = {}

    @abstractmethod
    def __init__(self, buffer_size: int):
        self.buffer_size = buffer_size

    def load_program(self, vert_file, frag_file, geom_file=None):
        vertex_shader = load_shader(vert_file)
        fragment_shader = load_shader(frag_file)

        self._program = gloo.Program(vertex_shader, fragment_shader)
        if geom_file:
            geometry_shader = load_shader(geom_file)
            self._program.set_shaders(vertex_shader, fragment_shader, geometry_shader)
        self._program.bind(self.vbo)

        # Ensure properties are defined
        model = self.model
        view = self.view
        projection = self.projection
        scale = self.scale

    def update(self):
        if self.visible:
            self.vbo.set_data(self.data)
        for child in self.children:
            child.update()

    def draw(self):
        if self.visible:
            self.program.draw(self.type)
        for child in self.children:
            child.draw()

    def add_child(self, tag: str, child: GLObjectBuffer):
        child.parent = self
        self.children.append(child)
        self.add_child_to_lookup(tag, child)

    def add_child_to_lookup(self, tag: str, child: GLObjectBuffer):
        self._children_dict[tag] = child
        if hasattr(self, '_parent'):
            self.parent.add_child_to_lookup(tag, child)

    def lookup_child(self, lookup_tag: str) -> maybe(GLObjectBuffer):
        if lookup_tag not in self._children_dict:
            return None
        return self._children_dict[lookup_tag]

    def rotate_by(self, degrees, vector):
        self.model = np.dot(self.parent.model, np.dot(self.model, rotate(degrees, vector)))
    
    def scale_by(self, x, y, z):
        self.model = np.dot(self.parent.model, np.dot(self.model, scale([x, y, z])))
    
    def translate_by(self, x, y, z):
        self.model = np.dot(self.parent.model, np.dot(self.model, translate([x, y, z])))

    @property
    def program(self):
        if not hasattr(self, '_program'):
            raise NoShaderProgramError(f"Trying to access shader program that doesn't exist for {self}")
        return self._program

    @property
    def visible(self):
        if not hasattr(self, '_visible'):
            self._visible = True
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        for child in self.children:
            child.visible = value

    @property
    def parent(self):
        if not hasattr(self, '_parent'):
            raise NoParentError(f"Trying to access parent that doesn't exist for {self}")
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def children(self):
        if not hasattr(self, '_children'):
            self._children = []
        return self._children

    @children.setter
    def children(self, value):
        self._children = value

    @property
    def model(self):
        if not hasattr(self, '_model'):
            if hasattr(self, '_parent'):
                self._model = self.parent.model
            else:
                self._model = np.eye(4, dtype=np.float32)
            self.program['u_model'] = self._model

        return self._model

    @model.setter
    def model(self, value):
        self._model = value
        self.program['u_model'] = self._model
        for child in self.children:
            child.model = value

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
        for child in self.children:
            child.view = value

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
        for child in self.children:
            child.projection = value

    @property
    def uniform_scale(self):
        if not hasattr(self, '_uniform_scale'):
            self._uniform_scale = 1
            self.program['u_scale'] = self._uniform_scale
        return self._uniform_scale

    @uniform_scale.setter
    def uniform_scale(self, value):
        self._uniform_scale = value
        self.program['u_scale'] = self._uniform_scale
        for child in self.children:
            child.uniform_scale = value

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