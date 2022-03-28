from tempfile import NamedTemporaryFile
import OpenGL.GL as GL
import numpy as np
import matplotlib.pyplot as plt

from texture import Textured, Texture
from core import Mesh

from itertools import product

class ProceduralGround(Textured):
    def __init__(self, shader, tex_file, grid_size=10, amplitude=1):
        self.wrap = GL.GL_REPEAT
        self.filter = (GL.GL_NEAREST, GL.GL_NEAREST)

        self.tex_file = tex_file

        xx, yy = list(np.meshgrid(np.arange(grid_size), np.arange(grid_size)))
        zz = np.random.normal(0, amplitude, size=(grid_size, grid_size))

        grid = np.stack((xx, yy, zz)).reshape(3, grid_size**2).T
        grid = grid.astype(np.float32)

        tex_coords = grid / grid_size
        tex_coords = tex_coords[:, (0, 1)]

        print(tex_coords)

        normals = np.zeros(grid.shape, dtype=np.float32)
        normals[:, 1] = 1
        
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


def _interpolate_smoothstep(a, b, w):
    return (b - a) * (3 - 2*w) * w**2 + a


def perlin_grid_2d(rows, cols, grid_size):
    grid_rows, grid_cols = grid_shape = (rows // grid_size + 1, cols // grid_size + 1)
    grid = 2 * np.pi * np.random.random(size=grid_shape)

    grid = np.stack([np.cos(grid), np.sin(grid)]).reshape(*grid_shape, 2)

    print(grid)

    output = np.zeros((rows, cols, 2))

    for row, col in product(range(rows), range(cols)):
        bottom_row = row // grid_rows
        left_col = col // grid_cols

        corners = [(bottom_row, left_col), (bottom_row + 1, left_col), (bottom_row + 1, left_col + 1), (bottom_row, left_col + 1)]

        closest = [grid[corner] for corner in corners]


        offsets = [np.array(corner) * (grid_size+1) - (row, col) for corner in corners]

        # print((row, col))
        # print((bottom_row, left_col))
        # print(offsets)
        # input("===================")

        dot_products = [np.dot(offset, gradient) for offset, gradient in zip(offsets, closest)]

        wx = (row - bottom_row) / grid_size
        wy = (col - left_col) / grid_size

        interpolation = _interpolate_smoothstep(
            _interpolate_smoothstep(dot_products[0], dot_products[1], wx),
            _interpolate_smoothstep(dot_products[2], dot_products[3], wx),
            wy
        )

        output[row, col] = interpolation

    return output






if __name__ == "__main__":
    plt.matshow(np.linalg.norm(perlin_grid_2d(100, 100, 10), axis=2))
    plt.show()
