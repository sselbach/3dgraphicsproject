""" collection of procedurally generated drawable objects """

import OpenGL.GL as GL
import numpy as np
import matplotlib.pyplot as plt
from perlin_numpy import generate_perlin_noise_2d, generate_fractal_noise_2d

from texture import Textured, Texture
from core import Mesh
from utils import displacement_to_normal_map

class ProceduralWaterGPU(Textured):
    """ Procedural water is a mesh grid.
        Translation according to some wave function can be applied in the vertex shader.
    """
    def __init__(self, shader, size, n_vertices, amplitude=1):
        # possible values for coordinates
        arange = np.arange(0, n_vertices, dtype=np.float32) * size/n_vertices - size/2

        # meshgrid returns all possible combinations of coordinates in a slightly weird format
        # --> 2-tuple of 2D arrays
        xx, yy = np.meshgrid(arange, arange)

        # z component is always 0
        zz = np.zeros(xx.shape, dtype=np.float32)

        # reshape into (n_vertices, 3)
        vertices = np.stack([xx, yy, zz]).reshape(3, -1).T

        # create index array by adding 2 triangles per vertex except those that lie on the top/right border
        index_list = []
        for x in range(n_vertices - 1):
            for y in range(n_vertices - 1):
                index_list.extend((x + y*n_vertices, (x+1) + (y+1) * n_vertices, x + (y+1) * n_vertices))
                index_list.extend((x + y*n_vertices, (x+1) + y * n_vertices, (x+1) + (y+1) * n_vertices))

        index = np.array(index_list, dtype=np.int32)

        # create mesh, pass amplitude as uniform to the shaders
        mesh = Mesh(shader,{
            "position": vertices
        }, uniforms={"amplitude": amplitude}, index=index)

        super().__init__(mesh)


class ProceduralGroundGPU(Textured):
    """ Similar to procedural water, except that displacement is given by a texture of perlin noise.
        Normals are also given by a precomputed texture.
    """
    def __init__(self, shader, tex_file, grid_size=100, perlin_size=(5, 5), amplitude=1):
        # position array (called grid here) similar to the procedural water
        xx, yy = list(np.meshgrid(np.arange(grid_size, dtype=np.float32), np.arange(grid_size, dtype=np.float32)))

        xx -= grid_size / 2
        yy -= grid_size / 2

        zz = np.zeros(xx.shape)

        grid = np.stack((xx, yy, zz)).reshape(3, -1).T
        grid = grid.astype(np.float32)

        # placeholder normals (real normals given by texture, see below)
        normals = np.zeros(grid.shape, dtype=np.float32)
        normals[:, 2] = 1

        # tangents are required so that we can apply a normal map correctly
        tangents = np.zeros(grid.shape, dtype=np.float32)
        tangents[:, 0] = 1

        # texture coordinates are different for displacement/normal map (map_coords)
        # and diffuse map (tex_coords)
        map_coords = (grid / grid_size) - 0.5
        map_coords = map_coords[:, (0, 1)]

        tex_coords = map_coords * 50

        # index array creation similar to procedural water
        index_list = []
        for x in range(grid_size-1):
            for z in range(grid_size-1):
                index_list.extend((x + z*grid_size, (x+1) + (z+1) * grid_size, x + (z+1) * grid_size))
                index_list.extend((x + z*grid_size, (x+1) + z * grid_size, (x+1) + (z+1) * grid_size))

        index = np.array(index_list, dtype=np.int32)

        # displacement map 2x the size of the vertex grid for more accurate normals
        #displacement_map = generate_perlin_noise_2d((grid_size*2, grid_size*2), perlin_size).astype(np.float32) * amplitude
        displacement_map = generate_fractal_noise_2d((grid_size*2, grid_size*2), perlin_size, 6).astype(np.float32) * amplitude
        
        # compute normals from displacement map
        normal_map = displacement_to_normal_map(displacement_map, scale=2)

        # uncomment below for a plot of the displacement/normal maps
        # fig, axs = plt.subplots(1, 2, dpi=200)
        # axs[0].imshow(displacement, cmap="gray")
        # axs[1].imshow(normals)
        # plt.show()
        
        # generate mesh
        mesh = Mesh(shader, attributes={
            "position": grid,
            "tex_coord": tex_coords,
            "map_coord": map_coords,
            "normal": normals,
            "tangent": tangents
        }, uniforms={
            "apply_displacement": 1, 
            "reflectiveness": 0, 
            "k_s": (0, 0, 0), 
            "apply_skinning": 0,
            "use_separate_map_coords": 1
        }, index=index)

        # generate textures
        # note that the displacement map is passed as float, which required some modification to the texture class
        diffuse_map = Texture(tex_file, GL.GL_REPEAT, GL.GL_NEAREST, GL.GL_NEAREST)
        displacement_map = Texture(displacement_map, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR, 
            internal_format=GL.GL_R32F, format=GL.GL_RED, data_type=GL.GL_FLOAT)
        normal_map = Texture(normal_map, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR,
            internal_format=GL.GL_RGB, format=GL.GL_RGB, data_type=GL.GL_UNSIGNED_BYTE)

        super().__init__(mesh, diffuse_map=diffuse_map, displacement_map=displacement_map, normal_map=normal_map)

if __name__ == "__main__":
    pass
