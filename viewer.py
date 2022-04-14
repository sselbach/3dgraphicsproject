#!/usr/bin/env python3
import sys
from itertools import cycle
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from core import Shader, Viewer, Mesh, Node, load
from texture import Texture, Textured, CubeMap
from transform import Trackball, translate
from procedural import TexturedPlane, ProceduralGroundGPU, Bridge
from utils import load_cubemap_from_directory
from primitives import InvertedCube


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

    trackball = Trackball(pitch=0, roll=88, yaw=90, distance=75)

    red = np.array([255, 0, 0], dtype=np.uint8).reshape(1, 1, 3)
    blue = np.array([0, 0, 255], dtype=np.uint8).reshape(1, 1, 3)

    #viewer = FixedCameraViewer(trackball=trackball, width=1920, height=1080)
    viewer = Viewer(trackball=trackball, width=1920, height=1080)

    environment = CubeMap(load_cubemap_from_directory("textures/interstellar", format="tga", correct_rotation=False))
    viewer.set_environment(environment)

    shader = Shader("texture.vert", "texture.frag")
    shader_axes = Shader("axes.vert", "axes.frag")
    shader_skybox = Shader("skybox.vert", "skybox.frag")

    ground = ProceduralGroundGPU(shader, "grass.png", grid_size=512, perlin_size=(16, 16), amplitude=20)
    ground_node = Node([ground], transform=translate(z=-20))

    water = TexturedPlane(shader, "water 0342.jpg", normal_file="textures/lava_normal.jpg", shape=(500, 500))
    water_node = Node([water], transform=translate(z=-3))

    ground_node.add(water_node)

    bridge = Bridge(shader, "textures/bridge/diffuse.jpg", "textures/bridge/normal.jpg", "textures/bridge/specular.jpg")
    bridge_node = Node([bridge])

    skybox = InvertedCube(shader_skybox)

    viewer.add(skybox)

    viewer.add(ground_node)
    viewer.add(bridge_node)
    viewer.add(Axis(shader_axes, length=10))
    
    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
