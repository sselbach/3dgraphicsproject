""" collection of simple drawable objects """

import OpenGL.GL as GL
import numpy as np

from core import Mesh
from texture import Textured, Texture

class Skybox(Mesh):
    """ Mesh for the skybox. Basically just a centered inverted cube that is drawn without depth mask.
        The real magic happens in the vertex shader, where the translation component of the modelview matrix
        is removed.
    """
    def __init__(self, shader):
        # unit cube. 8 vertices is enough since position is the only attribute
        vertices = np.array([
            (0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1),     # front
            (0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)],    # back
        np.float32)

        # transform coordinates to [-1, 1]
        vertices = vertices * 2 - 1

        # index array
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
        """ draw without depth mask to have everything else appear in front of the skybox """
        GL.glDepthMask(GL.GL_FALSE)
        super().draw(**uniforms)
        GL.glDepthMask(GL.GL_TRUE)

class Bridge(Textured):
    """ The bridge is just a box with some textures. """
    def __init__(self, shader, diffuse_map, normal_map, specular_map):
        # points in space
        A = (-1, -1, -1)
        B = (1, -1, -1)
        C = (1, -1, 1)
        D = (-1, -1, 1)
        E = (-1, 1, -1)
        F = (1, 1, -1)
        G = (1, 1, 1)
        H = (-1, 1, 1)

        # direction vectors
        x = np.array((1, 0, 0))
        y = np.array((0, 1, 0))
        z = np.array((0, 0, 1))
        
        # duplicated vertices per face
        vertices = np.array([
            A, B, C, D,     # front
            B, F, G, C,     # right
            F, E, H, G,     # back
            E, A, D, H,     # left
            C, G, H, D,     # top
            E, F, B, A      # bottom
        ], np.float32)

        # re-scale to dimensions of the bridge
        vertices = vertices * (500, 2, 0.1)

        # face normals
        normals = np.array([
            -y, -y, -y, -y,
            x, x, x, x,
            y, y, y, y,
            -x, -x, -x, -x,
            z, z, z, z,
            -z, -z, -z, -z
        ], np.float32)

        # face tangents
        tangents = np.array([
            z, z, z, z,
            z, z, z, z,
            z, z, z, z,
            z, z, z, z,
            x, x, x, x,
            -x, -x, -x, -x
        ], np.float32)

        # texture coordinates are the vertex components that are parallel with the face they are in...
        tex_coords = np.array([
            vertices[0:4, (0, 2)],
            vertices[4:8, (1, 2)],
            vertices[8:12, (0, 2)],
            vertices[12:16, (1, 2)],
            vertices[16:20, (0, 1)],
            vertices[20:24, (0, 1)]
        ], np.float32).reshape(24, 2)

        # ... with some scaling applied
        tex_coords /= 5

        # index array, one line = two triangles per face
        index = np.array([
            0, 1, 2, 0, 2, 3,
            4, 5, 6, 4, 6, 7,
            8, 9, 10, 8, 10, 11,
            12, 13, 14, 12, 14, 15,
            16, 17, 18, 16, 18, 19,
            20, 21, 22, 20, 22, 23
        ], np.uint32)

        # construct mesh...
        mesh = Mesh(shader, {
            "position": vertices,
            "tex_coord": tex_coords,
            "map_coord": tex_coords,
            "normal": normals,
            "tangent": tangents
        }, uniforms={"apply_displacement": 0, "reflectiveness": 1, "k_s": (1, 1, 1), "s": 20}, index=index)

        # ... and textures
        diffuse_map = Texture(diffuse_map)
        normal_map = Texture(normal_map)
        specular_map = Texture(specular_map)

        # and finally construct parent Textured object
        super().__init__(mesh, diffuse_map=diffuse_map, normal_map=normal_map, specular_map=specular_map)

