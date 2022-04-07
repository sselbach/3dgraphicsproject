import numpy as np
from skimage import filters

def np_float_to_gl_ubyte(array):
    return ((array + 1) * 127).astype(np.ubyte)

def gradient_image(img):
    gx = filters.sobel_h(img)
    gy = filters.sobel_v(img)

    return gx, gy

def displacement_to_normal_map(displacement_map, scale=1):
    """scale: """
    normal_map = np.ones((*displacement_map.shape, 3), dtype=np.float32)

    gx, gy = gradient_image(displacement_map)

    normal_map[:, :, 0] = gx * scale
    normal_map[:, :, 1] = gy * scale
    
    normal_map /= np.linalg.norm(normal_map, axis=2, ord=2)[:, :, None]

    print(np.min(normal_map), np.max(normal_map))

    return np_float_to_gl_ubyte(normal_map)