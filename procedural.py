import OpenGL.GL as GL
import numpy as np

from texture import Textured

class ProceduralGround(Textured):
    def __init__(self, shader, tex_file, grid_size=10):
        self.wrap = GL.GL_REPEAT
        self.filter = (GL.GL_NEAREST, GL.GL_NEAREST)

        self.tex_file = tex_file

        xx, zz = list(np.meshgrid(np.arange(grid_size), np.arange(grid_size)))
        yy = np.random.normal(0, 1, size=(grid_size, grid_size))

        grid = np.stack((xx, yy, zz)).reshape(3, grid_size**2).T
        grid = grid.astype(np.float32)
        
        index_list = []

        for x in range(grid_size):
            for z in range(grid_size):
                index_list.extend((x + z*grid_size, (x+1) + (z+1) * grid_size, x + (z+1) * grid_size))
                index_list.extend((x + z*grid_size, (x+1) + z * grid_size, (x+1) + (z+1) * grid_size))

        index = np.array(index_list, dtype=np.int32)
        print(index)


if __name__ == "__main__":
    p = ProceduralGround("bla", "blub", 3)

