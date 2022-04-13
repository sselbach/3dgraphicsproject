#!/usr/bin/env python3
import sys
from itertools import cycle
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from core import Shader, Viewer, Mesh, Node, load
from texture import Texture, Textured
from transform import Trackball, rotate, scale, translate
from procedural import TexturedPlane, ProceduralGroundGPU

from math import pi


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """
    def __init__(self, shader, length=1):
        pos = ((0, 0, 0), (length, 0, 0), (0, 0, 0), (0, length, 0), (0, 0, 0), (0, 0, length))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, attributes=dict(position=pos, color=col))

        GL.glClearColor(0.8, 0.8, 0.8, 1)

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
    shader_skinning = Shader("skinning.vert", "skinning.frag")

    ground = ProceduralGroundGPU(shader, "grass.png", grid_size=500, perlin_size=(20, 20), amplitude=20)
    ground_node = Node([ground], transform=translate(z=-10))

    water = TexturedPlane(shader, "water 0342.jpg", normal_file="water 0342normal.jpg", size=500)
    water_node = Node([water], transform=translate(z=-13))

    golem = load("animations/Golem_jump.fbx", shader_skinning)
    golem_node = Node(golem, transform=scale(0.001))

    knight = load("animations/Knight_attack_2.fbx", shader_skinning)
    knight_node = Node(knight)
    
    viewer.add(ground_node)
    viewer.add(water_node)
    viewer.add(golem_node)

    print(golem)

    #viewer.add(knight_node)


    #viewer.add(*[m for file in sys.argv[1:] for m in load(file, shader)])
    #viewer.add(Axis(shader_axes, length=10))
    
    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
