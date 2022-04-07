import OpenGL.GL as GL
import numpy as np
import matplotlib.pyplot as plt
from perlin_numpy import generate_perlin_noise_2d

from texture import Textured, Texture
from core import Mesh
from utils import displacement_to_normal_map

from itertools import product


class ProceduralGroundGPU(Textured):
    def __init__(self, shader, tex_file, grid_size=100, amplitude=1):
        xx, yy = list(np.meshgrid(np.arange(grid_size, dtype=np.float32), np.arange(grid_size, dtype=np.float32)))

        xx -= grid_size / 2
        yy -= grid_size / 2

        zz = np.zeros(xx.shape)

        grid = np.stack((xx, yy, zz)).reshape(3, grid_size**2).T
        grid = grid.astype(np.float32)

        tex_coords = (grid / grid_size) - 0.5
        tex_coords = tex_coords[:, (0, 1)]

        index_list = []

        for x in range(grid_size-1):
            for z in range(grid_size-1):
                index_list.extend((x + z*grid_size, (x+1) + (z+1) * grid_size, x + (z+1) * grid_size))
                index_list.extend((x + z*grid_size, (x+1) + z * grid_size, (x+1) + (z+1) * grid_size))

        index = np.array(index_list, dtype=np.int32)

        # displacement map 4x the size of the vertex grid for better normals
        displacement = generate_perlin_noise_2d((grid_size*4, grid_size*4), (5, 5)).astype(np.float32) * amplitude
        normals = displacement_to_normal_map(displacement, scale=4)

        fig, axs = plt.subplots(1, 2, dpi=200)
        axs[0].imshow(displacement, cmap="gray")
        axs[1].imshow(normals)
        plt.show()
        
        mesh = Mesh(shader, attributes={
            "position": grid,
            "tex_coord": tex_coords
        }, index=index)

        diffuse_map = Texture(tex_file, GL.GL_REPEAT, GL.GL_NEAREST, GL.GL_NEAREST)
        displacement_map = Texture(displacement, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR, 
            internal_format=GL.GL_R32F, format=GL.GL_RED, data_type=GL.GL_FLOAT)
        normal_map = Texture(normals, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR,
            internal_format=GL.GL_RGB, format=GL.GL_RGB, data_type=GL.GL_UNSIGNED_BYTE)

        super().__init__(mesh, diffuse_map=diffuse_map, displacement_map=displacement_map, normal_map=normal_map)

if __name__ == "__main__":
    pass
