import os

import numpy as np
from skimage import filters
from PIL import Image

import matplotlib.pyplot as plt

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


def load_cubemap_from_directory(path, format="png", correct_rotation=False):
    right = np.array(Image.open(os.path.join(path, "right." + format)).convert("RGB"))
    left = np.array(Image.open(os.path.join(path, "left." + format)).convert("RGB"))
    top = np.array(Image.open(os.path.join(path, "top." + format)).convert("RGB"))
    bottom = np.array(Image.open(os.path.join(path, "bottom." + format)).convert("RGB"))
    back = np.array(Image.open(os.path.join(path, "back." + format)).convert("RGB"))
    front = np.array(Image.open(os.path.join(path, "front." + format)).convert("RGB"))


    if correct_rotation:
        left = left[:, ::-1]
        front = front[:, ::-1]
        right = right[:, ::-1]
        back = back[:, ::-1]
        top = top[::-1, :]
        bottom = bottom[::-1, :]

    top = np.rot90(top)

    #right[:, :] = (255, 0, 0)

    return right, left, top, bottom, back, front


def load_cubemap_from_image(path):
    img = np.array(Image.open(path).convert("RGB"))

    height, width = img.shape[:2]
    grid_x = width // 4
    grid_y = height // 3

    left = img[grid_y : 2*grid_y, : grid_x]
    front = img[grid_y : 2*grid_y, grid_x : 2*grid_x]
    right = img[grid_y : 2*grid_y, 2*grid_x : 3*grid_x]
    back = img[grid_y : 2*grid_y, 3*grid_x : 4*grid_x]
    top = img[: grid_y, grid_x : 2*grid_x]
    bottom = img[2*grid_y : 3*grid_y, grid_x : 2*grid_x]

    left = left[:, ::-1]
    front = front[:, ::-1]
    right = right[:, ::-1]
    back = back[:, ::-1]
    top = top[::-1, :]
    bottom = bottom[::-1, :]

    return right, left, top, bottom, back, front


if __name__ == "__main__":
    pass