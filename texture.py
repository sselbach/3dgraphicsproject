import OpenGL.GL as GL              # standard Python OpenGL wrapper
from PIL import Image               # load texture maps
import numpy as np


# -------------- OpenGL Texture Wrapper ---------------------------------------
class Texture:
    """ Helper class to create and automatically destroy textures
        Modified to allow loading Texture from numpy array,
        as well as textures of any internal format (e.g. single-channel textures)
    """
    def __init__(self, tex_file, wrap_mode=GL.GL_REPEAT,
                 mag_filter=GL.GL_LINEAR, min_filter=GL.GL_LINEAR_MIPMAP_LINEAR,
                 tex_type=GL.GL_TEXTURE_2D, internal_format=GL.GL_RGBA, format=GL.GL_RGBA,
                 data_type=GL.GL_UNSIGNED_BYTE):
        self.glid = GL.glGenTextures(1)
        self.type = tex_type

        if type(tex_file) is np.ndarray:
            tex_bytes = tex_file.tobytes()
            tex_string = str(type(tex_file))

            height, width = tex_file.shape[:2]

        else:
            try:
                # imports image as a numpy array in exactly right format
                tex = Image.open(tex_file).convert('RGBA')
                tex_bytes = tex.tobytes()
                tex_string = tex_file

                width, height = tex.width, tex.height
            except FileNotFoundError:
                print("ERROR: unable to load texture file %s" % tex_file)

        GL.glBindTexture(tex_type, self.glid)
        GL.glTexImage2D(tex_type, 0, internal_format, width, height,
                        0, format, data_type, tex_bytes)
        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_S, wrap_mode)
        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_T, wrap_mode)
        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_MIN_FILTER, min_filter)
        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_MAG_FILTER, mag_filter)
        GL.glGenerateMipmap(tex_type)
        print(f'Loaded texture {tex_string} ({width}x{height}'
                f' wrap={str(wrap_mode).split()[0]}'
                f' min={str(min_filter).split()[0]}'
                f' mag={str(mag_filter).split()[0]})')

    def bind(self, texture_unit):
        GL.glActiveTexture(texture_unit)
        GL.glBindTexture(self.type, self.glid)

    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)


class CubeMap:
    def __init__(self, cube):
        """ cube should be tuple of np.ndarray (dtype=np.uint8) like
            (right, left, top, bottom, back, front)
        """
        self.glid = GL.glGenTextures(1)
        tex_type = GL.GL_TEXTURE_CUBE_MAP
        self.type = tex_type

        GL.glBindTexture(tex_type, self.glid)

        for i, face in enumerate(cube):
            width, height = face.shape[:2]
            GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGB, width, height, 0,
                GL.GL_RGB, GL.GL_UNSIGNED_BYTE, face.tobytes())

        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(tex_type, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        print("loaded a cubemap :)")

    def bind(self):
        """ Method to globally bind texture to the shaders
        """
        GL.glActiveTexture(GL.GL_TEXTURE20)
        GL.glBindTexture(self.type, self.glid)


    def __del__(self):
        GL.glDeleteTextures(self.glid)


# -------------- Textured mesh decorator --------------------------------------
class Textured:
    """ Drawable mesh decorator that activates and binds OpenGL textures """
    def __init__(self, drawable, **textures):
        self.drawable = drawable
        self.textures = textures

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        for index, (name, texture) in enumerate(self.textures.items()):
            GL.glActiveTexture(GL.GL_TEXTURE0 + index)
            GL.glBindTexture(texture.type, texture.glid)
            uniforms[name] = index
        self.drawable.draw(primitives=primitives, **uniforms)
