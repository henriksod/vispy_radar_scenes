#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GL_RadarDetections inherits GL_ObjectBuffer and provides a way to visualize detections
"""

import numpy as np

from vispy.io import read_mesh

from .gl_object_buffer import GLObjectBuffer


class GLMeshObject(GLObjectBuffer):
    vertex_shader_file: str = 'model_vertex.glsl'
    fragment_shader_file: str = 'model_fragment.glsl'

    def __init__(self, model_path: str, buffer_size: int = 50000):
        super().__init__(buffer_size)

        vertices, faces, normals, texcoords = read_mesh(model_path)
        print(f'{vertices.shape}, {faces.shape}, {normals.shape}')

        new_vertices = np.zeros((faces.shape[0] * faces.shape[1], 3))
        new_normals = np.zeros((normals.shape[0] * normals.shape[1], 3))
        for i in range(faces.shape[0]):
            for j in range(faces.shape[1]):
                vertex = vertices[faces[i, j], :]
                new_vertices[i*3+j] = vertex
                normal = normals[i, :]
                new_normals[i*3+j] = normal

        """new_vertices = np.zeros((faces.shape[0] * faces.shape[1] + (faces.shape[0] * faces.shape[1]) // 2, 3))
        new_normals = np.zeros((faces.shape[0] * faces.shape[1] + (faces.shape[0] * faces.shape[1]) // 2, 3))
        for i in range(faces.shape[0]):
            triangle1 = [faces[i, 0], faces[i, 1], faces[i, 2]]
            triangle2 = [faces[i, 1], faces[i, 2], faces[i, 3]]
            triangles = [triangle1, triangle2]
            j = 0
            for tri in triangles:
                for index in tri:
                    vertex = vertices[index, :]
                    new_vertices[i * 6 + j] = vertex
                    normal = normals[index, :]
                    new_normals[i * 6 + j] = normal
                    j += 1"""

        #self.buffer_size = faces.shape[0] * faces.shape[1] + (faces.shape[0] * faces.shape[1]) // 2
        self.buffer_size = new_vertices.shape[0]
        self.data['a_position'] = new_vertices
        self.data['a_normals'] = new_normals
        self.data['a_color'] = 0.9, 0.9, 0.9, 1

        self.load_program(self.vertex_shader_file,
                          self.fragment_shader_file)
        
        self.rotate_by(90, (0, 0, 1))
        self.scale_by(0.1, 0.1, 0.1)

    @property
    def type(self):
        return 'triangles'

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = \
                np.zeros(self.buffer_size, [('a_position', np.float32, 3),
                                            ('a_normals', np.float32, 3),
                                            ('a_color', np.float32, 4)])
        return self._data