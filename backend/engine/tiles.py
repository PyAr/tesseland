from itertools import product
from math import ceil
from skimage import io
from skimage.transform import rescale
from skimage.util import slice_along_axes
import numpy as np
from PIL import Image
import logging


logger = logging.getLogger(__name__)

# Most smartphones featured a 16:9 aspect ratio.
multiplier = 40
DEFAULT_HEIGHT = 16 * multiplier  # rows
DEFAULT_WIDTH = 9 * multiplier  # columns


def compute_boxes(rows=None, columns=None):
    """
    Given an input image, compute the coordinates of tiles that would split the image in rows and columns.

    """
    if not rows or not columns:
        return []

    logger.info("Tiling: %i columns (of width %i), %i rows (of height %i)", columns, DEFAULT_WIDTH, rows, DEFAULT_HEIGHT)

    for i in range(columns):
        # TODO FIX THIS
        ul_x = i * DEFAULT_WIDTH
        lr_x = (i+1) * DEFAULT_WIDTH
        for j in range(rows):
            ul_y = j * DEFAULT_HEIGHT
            lr_y = (j+1) * DEFAULT_HEIGHT

            yield (
                (ul_x, ul_y),
                (lr_x, lr_y)
            )
            # Each box is represented with a tuple of its lower-left and upper-right corners: (ll_x, ll_y), (ur_x, ur_y)


def crop_image(img, rows=None, columns=None):
    if not rows or not columns:
        return []

    for ul, lr in compute_boxes(rows=rows, columns=columns):
        ul_x, ul_y = ul
        lr_x, lr_y = lr

        logger.info("tile slice_along_axes: x=%s, y=%s", str((ul_x, lr_x)), str((ul_y, lr_y)))
        cropped_img = slice_along_axes(img, [(ul_y, lr_y), (ul_x, lr_x)])
        yield cropped_img


def is_prime(n):
    """
    Return True if the given number is a prime bigger than 2.
    Hack. Only checks lower than 100. Fix it.
    """
    return n in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def factorize(n):
    for i in range(1, n+1):
        for j in range(1, n+1):
            if i * j == n:
                yield (i, j)


def get_factors(target, ratio):
    # search for the N and M whose ratio is closer to the image's aspect ratio
    min = 1_000_000.0  # Arbitrary big number.
    n = 1
    m = 1
    rows = n
    cols = m
    for n, m in factorize(target):
        print("N, M: %i, %i"%( n, m))
        print("aspect ratio: %f"%(n/m))
        if abs((16.0*n / 9.0 * m) - ratio) < min:
            rows = n
            cols = m
    return rows, cols

##

def find_best_tiling(img_height, img_width, total_tiles):
    """..."""
    scaling_factor = 0
    best_image_size = 0
    best_rows = 0
    best_columns = 0
    for rows, columns in factorize(total_tiles):
        # Configures a display with certain rows and columns
        display_height = rows * DEFAULT_HEIGHT
        display_width = columns * DEFAULT_WIDTH

        # Try scaling the image to match the display's height
        factor = display_height / img_height
        scaled_img_height  = img_height * factor
        scaled_img_width = img_width * factor

        if not (scaled_img_height <= display_height and scaled_img_width <= display_width):
            # The scaled image DOES NOT fit in the display.
            # Now scale the image to match the display's width
            factor = display_width / img_width
            scaled_img_height  = img_height * factor
            scaled_img_width = img_width * factor

        if scaled_img_height * scaled_img_width > best_image_size:
            best_image_size = scaled_img_height * scaled_img_width
            scaling_factor = factor
            best_rows = rows
            best_columns = columns

    return scaling_factor, best_rows, best_columns




def get_tiles(img, n_tiles):
    if n_tiles < 2:
        raise Exception("Tiles must be at least 2.")

    img_height, img_width, _ = img.shape
    print("img_height:", img_height, " img_width: ", img_width)

    total_tiles = n_tiles
    while is_prime(total_tiles):
        total_tiles += 1

    scaling_factor, rows, cols = find_best_tiling(img_height, img_width, total_tiles)
    print("Scaling factor:", scaling_factor, "Rows:", rows, ", Columns: ", cols)
    print("scaled img_height:", img_height * scaling_factor, ", scaled img_width: ", img_width * scaling_factor)
    print("Display height:", rows * DEFAULT_HEIGHT, ", display width: ", cols * DEFAULT_WIDTH)
    scaled_image = rescale(img, [scaling_factor, scaling_factor, 1])

    # TODO
    # crear imagen "vacía" del tamaño del display
    # meter la scaled_image dentro de esa caja y continuar
    current_H, current_W = img_height * scaling_factor, img_width * scaling_factor
    final_H, final_W = rows * DEFAULT_HEIGHT, cols * DEFAULT_WIDTH

    pil_scaled_img = Image.fromarray((scaled_image*255).astype(np.uint8))

    final_img = Image.new("RGBA", size=(final_W, final_H))

    offset_H = ceil((final_H - current_H) / 2)
    offset_W = ceil((final_W - current_W) / 2)
    print('OFFSETS', offset_H, offset_W)
    # print('TODO', )

    final_img.paste(pil_scaled_img, (offset_W, offset_H))
    # import ipdb; ipdb.set_trace()

    print('BEFORECROP', np.array(final_img).shape)
    return crop_image(np.array(final_img), rows=rows, columns=cols)


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt

    FORMAT = "%(asctime)s %(levelno)s %(module)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    img = io.imread(sys.argv[1])
    n_tiles = int(sys.argv[2])


    print("DEfault display tiles size. Heigth: ", DEFAULT_HEIGHT, ", Width: ", DEFAULT_WIDTH)
    tiles = get_tiles(img, n_tiles)
    for t in tiles:
        plt.figure()
        plt.imshow(t)
        plt.tight_layout()
    plt.show()
    plt.imshow(img)
