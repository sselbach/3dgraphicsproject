import OpenGL.GL as GL
import numpy as np
import matplotlib.pyplot as plt
from perlin_numpy import generate_perlin_noise_2d, generate_fractal_noise_2d

from texture import Textured, Texture, CubeMap
from core import Mesh
from utils import displacement_to_normal_map

class ProceduralWaterGPU(Textured):
    def __init__(self, shader, size, n_vertices, amplitude=1):
        arange = np.arange(0, n_vertices, dtype=np.float32) * size/n_vertices - size/2

        xx, yy = np.meshgrid(arange, arange)
        zz = np.zeros(xx.shape, dtype=np.float32)

        vertices = np.stack([xx, yy, zz]).reshape(3, -1).T

        normals = np.zeros(vertices.shape, dtype=np.float32)
        normals[:, 2] = 1

        tangents = np.zeros(vertices.shape, dtype=np.float32)
        tangents[:, 0] = 1

        tex_coords = vertices[:, (0, 1)]

        index_list = []

        for x in range(n_vertices - 1):
            for z in range(n_vertices - 1):
                index_list.extend((x + z*n_vertices, (x+1) + (z+1) * n_vertices, x + (z+1) * n_vertices))
                index_list.extend((x + z*n_vertices, (x+1) + z * n_vertices, (x+1) + (z+1) * n_vertices))

        index = np.array(index_list, dtype=np.int32)

        mesh = Mesh(shader,{
            "position": vertices,
            "normal": normals,
            "tangent": tangents,
            "tex_coord": tex_coords,
            "map_coord": tex_coords
        }, uniforms={"amplitude": amplitude}, index=index)

        super().__init__(mesh)


class ProceduralGroundGPU(Textured):
    def __init__(self, shader, tex_file, grid_size=100, perlin_size=(5, 5), amplitude=1):
        xx, yy = list(np.meshgrid(np.arange(grid_size, dtype=np.float32), np.arange(grid_size, dtype=np.float32)))

        xx -= grid_size / 2
        yy -= grid_size / 2

        zz = np.zeros(xx.shape)

        grid = np.stack((xx, yy, zz)).reshape(3, -1).T
        grid = grid.astype(np.float32)

        normals = np.zeros(grid.shape, dtype=np.float32)
        normals[:, 2] = 1

        tangents = np.zeros(grid.shape, dtype=np.float32)
        tangents[:, 0] = 1

        map_coords = (grid / grid_size) - 0.5
        map_coords = map_coords[:, (0, 1)]

        tex_coords = map_coords * 50

        index_list = []

        for x in range(grid_size-1):
            for z in range(grid_size-1):
                index_list.extend((x + z*grid_size, (x+1) + (z+1) * grid_size, x + (z+1) * grid_size))
                index_list.extend((x + z*grid_size, (x+1) + z * grid_size, (x+1) + (z+1) * grid_size))

        index = np.array(index_list, dtype=np.int32)

        # displacement map 4x the size of the vertex grid for better normals
        displacement_map = generate_perlin_noise_2d((grid_size*4, grid_size*4), perlin_size).astype(np.float32) * amplitude
        displacement_map = generate_fractal_noise_2d((grid_size*4, grid_size*4), perlin_size, 6).astype(np.float32) * amplitude
        
        normal_map = displacement_to_normal_map(displacement_map, scale=4)

        # fig, axs = plt.subplots(1, 2, dpi=200)
        # axs[0].imshow(displacement, cmap="gray")
        # axs[1].imshow(normals)
        # plt.show()
        
        mesh = Mesh(shader, attributes={
            "position": grid,
            "tex_coord": tex_coords,
            "map_coord": map_coords,
            "normal": normals,
            "tangent": tangents
        }, uniforms={"apply_displacement": 1, "reflectiveness": 0, "k_s": (0, 0, 0)}, index=index)

        diffuse_map = Texture(tex_file, GL.GL_REPEAT, GL.GL_NEAREST, GL.GL_NEAREST)
        displacement_map = Texture(displacement_map, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR, 
            internal_format=GL.GL_R32F, format=GL.GL_RED, data_type=GL.GL_FLOAT)
        normal_map = Texture(normal_map, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR,
            internal_format=GL.GL_RGB, format=GL.GL_RGB, data_type=GL.GL_UNSIGNED_BYTE)

        super().__init__(mesh, diffuse_map=diffuse_map, displacement_map=displacement_map, normal_map=normal_map)

if __name__ == "__main__":
    pass
