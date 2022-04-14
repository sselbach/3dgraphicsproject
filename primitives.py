import OpenGL.GL as GL
from core import Mesh

import numpy as np

class InvertedCube(Mesh):
    def __init__(self, shader):
        vertices = np.array([
            (0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1),     # front
            (0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)],    # back
        np.float32)

        vertices = vertices * 500 - 250

        index = np.array([
            (0, 2, 1), (0, 3, 2),
            (1, 6, 5), (1, 2, 6),
            (5, 7, 4), (5, 6, 7),
            (4, 3, 0), (4, 7, 3),
            (3, 6, 2), (3, 7, 6),
            (0, 5, 4), (0, 1, 5)
        ], np.uint32)

        super().__init__(shader, {"position": vertices}, index=index)

    def draw(self, **uniforms):
        GL.glDepthMask(GL.GL_FALSE)
        super().draw(**uniforms)
        GL.glDepthMask(GL.GL_TRUE)

