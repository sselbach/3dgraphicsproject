#!/usr/bin/env python3
import sys
from itertools import cycle
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from core import Shader, Viewer, Mesh, load
from texture import Texture, Textured
from transform import Trackball
from procedural import ProceduralGround


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """
    def __init__(self, shader):
        pos = ((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, attributes=dict(position=pos, color=col))

    def draw(self, primitives=GL.GL_LINES, **uniforms):
        super().draw(primitives=primitives, **uniforms)

class FixedCameraViewer(Viewer):
    def on_mouse_move(self, win, xpos, ypos):
        pass

    def on_scroll(self, win, _deltax, deltay):
        pass
# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """

    trackball = Trackball(pitch=0, roll=60, yaw=90, distance=150)

    viewer = FixedCameraViewer(trackball=trackball)
    shader = Shader("texture.vert", "texture.frag")

    ground = ProceduralGround(shader, "grass.png", grid_size=100, amplitude=10)

    viewer.add(ground)
    viewer.add(Axis(shader))
    
    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
