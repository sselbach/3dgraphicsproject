#!/usr/bin/env python3
import sys
from itertools import cycle
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from core import Shader, Viewer, Mesh, Node, load
from texture import Texture, Textured
from transform import Trackball, translate
from procedural import ProceduralGroundGPU


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """
    def __init__(self, shader, length=1):
        pos = ((0, 0, 0), (length, 0, 0), (0, 0, 0), (0, length, 0), (0, 0, 0), (0, 0, length))
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

    viewer = FixedCameraViewer(trackball=trackball, width=1920, height=1080)
    shader = Shader("texture.vert", "texture.frag")
    shader_axes = Shader("axes.vert", "axes.frag")

    ground = ProceduralGroundGPU(shader, "grass.png", grid_size=100, amplitude=10)
    ground_node = Node(children=[ground], transform=translate(z=-10))

    viewer.add(ground_node)
    viewer.add(Axis(shader_axes, length=10))
    
    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
