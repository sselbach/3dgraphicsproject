#!/usr/bin/env python3
import sys
from itertools import cycle
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from core import Shader, Viewer, Mesh, load
from texture import Texture, Textured
from procedural import ProceduralGround


# -------------- Example textured plane class ---------------------------------
class TexturedPlane(Textured):
    """ Simple first textured object """
    def __init__(self, shader, tex_file, tex_file_2):
        # prepare texture modes cycling variables for interactive toggling
        self.wraps = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                            GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filters = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                              (GL.GL_LINEAR, GL.GL_LINEAR),
                              (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap, self.filter = next(self.wraps), next(self.filters)
        self.file = tex_file
        self.file_2 = tex_file_2

        # setup plane mesh to be textured
        base_coords = ((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0))
        tex_coord = np.array(((0, 0), (0, 1), (1, 1), (1, 0)), np.float32)
        normals = np.array(((0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)), np.float32)
        scaled = 100 * np.array(base_coords, np.float32)
        indices = np.array((0, 1, 2, 0, 2, 3), np.uint32)
        mesh = Mesh(shader, attributes={"position": scaled, "normal": normals, "tex_coord": tex_coord}, index=indices)


        # setup & upload texture to GPU, bind it to shader name 'diffuse_map'
        texture_1 = Texture(tex_file, self.wrap, *self.filter)
        texture_2 = Texture(tex_file_2, self.wrap, *self.filter)
        super().__init__(mesh, diffuse_map=texture_1, flower_overlay=texture_2)

    def key_handler(self, key):
        # cycle through texture modes on keypress of F6 (wrap) or F7 (filtering)
        self.wrap = next(self.wraps) if key == glfw.KEY_F6 else self.wrap
        self.filter = next(self.filters) if key == glfw.KEY_F7 else self.filter
        if key in (glfw.KEY_F6, glfw.KEY_F7):
            texture = Texture(self.file, self.wrap, *self.filter)
            texture_2 = Texture(self.file_2, self.wrap, *self.filter)
            self.textures.update(diffuse_map=texture, flower_overlay=texture_2)


# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    shader = Shader("texture.vert", "texture.frag")

    ground = ProceduralGround(shader, "grass.png", grid_size=10, amplitude=0.5)

    viewer.add(ground)
    
    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
