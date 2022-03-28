import OpenGL.GL as GL
import numpy as np
import matplotlib.pyplot as plt
from perlin_numpy import generate_perlin_noise_2d

from texture import Textured, Texture
from core import Mesh

from itertools import product

class ProceduralGround(Textured):
    def __init__(self, shader, tex_file, grid_size=10, amplitude=1):
        self.wrap = GL.GL_REPEAT
        self.filter = (GL.GL_NEAREST, GL.GL_NEAREST)

        self.tex_file = tex_file

        xx, yy = list(np.meshgrid(np.arange(grid_size, dtype=np.float32), np.arange(grid_size, dtype=np.float32)))

        xx -= grid_size / 2
        yy -= grid_size / 2

        zz = np.random.normal(0, amplitude, size=(grid_size, grid_size))
        zz = generate_perlin_noise_2d((grid_size, grid_size), (5, 5)) * amplitude

        grid = np.stack((xx, yy, zz)).reshape(3, grid_size**2).T
        grid = grid.astype(np.float32)

        tex_coords = grid / grid_size
        tex_coords = tex_coords[:, (0, 1)]

        normals = np.zeros(grid.shape, dtype=np.float32)
        normals[:, 2] = 1
        
        index_list = []

        for x in range(grid_size-1):
            for z in range(grid_size-1):
                index_list.extend((x + z*grid_size, (x+1) + (z+1) * grid_size, x + (z+1) * grid_size))
                index_list.extend((x + z*grid_size, (x+1) + z * grid_size, (x+1) + (z+1) * grid_size))

        index = np.array(index_list, dtype=np.int32)
        
        mesh = Mesh(shader, attributes={
            "position": grid,
            "normal": normals,
            "tex_coord": tex_coords
        }, index=index)

        texture = Texture(tex_file, self.wrap, *self.filter)

        super().__init__(mesh, diffuse_map=texture)


if __name__ == "__main__":
    plt.matshow(perlin_grid_2d(100, 100, 10))
    plt.show()
