import OpenGL.GL as GL
import numpy as np
import matplotlib.pyplot as plt
from perlin_numpy import generate_perlin_noise_2d, generate_fractal_noise_2d

from texture import Textured, Texture, CubeMap
from core import Mesh
from utils import displacement_to_normal_map

class TexturedPlane(Textured):
    def __init__(self, shader, tex_file, normal_file=None, shape=(100, 100)):
        size_x, size_y = shape

        vertices = np.array([(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)], dtype=np.float32)
        vertices[:, 0] *= size_x
        vertices[:, 1] *= size_y

        normals = np.array([(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)], dtype=np.float32)
        tangents = np.array([(1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0)], dtype=np.float32)

        tex_coords = np.array([(0, 0), (1, 0), (0, 1), (1, 1)], dtype=np.float32)
        tex_coords *= size_x / 20

        indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

        mesh = Mesh(shader, {
            "position": vertices,
            "tex_coord": tex_coords,
            "map_coord": tex_coords.copy(),
            "normal": normals,
            "tangent": tangents
        }, uniforms={"use_normal_map": 1, "reflectiveness": 0.5}, index=indices)

        diffuse_map = Texture(tex_file)

        if not normal_file:
            normal_map = Texture(np.array([127, 127, 255], np.uint8).reshape((1, 1, 3)))

        else:
            normal_map = Texture(normal_file)

        super().__init__(mesh, diffuse_map=diffuse_map, normal_map=normal_map)


class Bridge(Textured):
    def __init__(self, shader, diffuse_map, normal_map, specular_map):
        A = (-1, -1, -1)
        B = (1, -1, -1)
        C = (1, -1, 1)
        D = (-1, -1, 1)
        E = (-1, 1, -1)
        F = (1, 1, -1)
        G = (1, 1, 1)
        H = (-1, 1, 1)

        x = np.array((1, 0, 0))
        y = np.array((0, 1, 0))
        z = np.array((0, 0, 1))
        
        vertices = np.array([
            A, B, C, D,     # front
            B, F, G, C,     # right
            F, E, H, G,     # back
            E, A, D, H,     # left
            C, G, H, D,     # top
            E, F, B, A      # bottom
        ], np.float32)

        vertices = vertices * (500, 2, 0.1)

        normals = np.array([
            -y, -y, -y, -y,
            x, x, x, x,
            y, y, y, y,
            -x, -x, -x, -x,
            z, z, z, z,
            -z, -z, -z, -z
        ], np.float32)

        tangents = np.array([
            z, z, z, z,
            z, z, z, z,
            z, z, z, z,
            z, z, z, z,
            x, x, x, x,
            -x, -x, -x, -x
        ], np.float32)

        tex_coords = np.array([
            vertices[0:4, (0, 2)],
            vertices[4:8, (1, 2)],
            vertices[8:12, (0, 2)],
            vertices[12:16, (1, 2)],
            vertices[16:20, (0, 1)],
            vertices[20:24, (0, 1)]
        ], np.float32).reshape(24, 2)
        tex_coords /= 5

        index = np.array([
            0, 1, 2, 0, 2, 3,
            4, 5, 6, 4, 6, 7,
            8, 9, 10, 8, 10, 11,
            12, 13, 14, 12, 14, 15,
            16, 17, 18, 16, 18, 19,
            20, 21, 22, 20, 22, 23
        ], np.uint32)

        mesh = Mesh(shader, {
            "position": vertices,
            "tex_coord": tex_coords,
            "map_coord": tex_coords,
            "normal": normals,
            "tangent": tangents
        }, uniforms={"apply_displacement": 0, "reflectiveness": 1}, index=index)

        diffuse_map = Texture(diffuse_map)
        normal_map = Texture(normal_map)
        specular_map = Texture(specular_map)

        super().__init__(mesh, diffuse_map=diffuse_map, normal_map=normal_map, specular_map=specular_map)


class ProceduralGroundGPU(Textured):
    def __init__(self, shader, tex_file, grid_size=100, perlin_size=(5, 5), amplitude=1):
        xx, yy = list(np.meshgrid(np.arange(grid_size, dtype=np.float32), np.arange(grid_size, dtype=np.float32)))

        xx -= grid_size / 2
        yy -= grid_size / 2

        zz = np.zeros(xx.shape)

        grid = np.stack((xx, yy, zz)).reshape(3, grid_size**2).T
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
        }, uniforms={"apply_displacement": 1, "reflectiveness": 0}, index=index)

        diffuse_map = Texture(tex_file, GL.GL_REPEAT, GL.GL_NEAREST, GL.GL_NEAREST)
        displacement_map = Texture(displacement_map, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR, 
            internal_format=GL.GL_R32F, format=GL.GL_RED, data_type=GL.GL_FLOAT)
        normal_map = Texture(normal_map, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR,
            internal_format=GL.GL_RGB, format=GL.GL_RGB, data_type=GL.GL_UNSIGNED_BYTE)

        super().__init__(mesh, diffuse_map=diffuse_map, displacement_map=displacement_map, normal_map=normal_map)

if __name__ == "__main__":
    pass
