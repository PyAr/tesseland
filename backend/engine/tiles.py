from itertools import product
from math import ceil
from skimage import io
from skimage.util import slice_along_axes
import logging


logger = logging.getLogger(__name__)

# Most smartphones featured a 16:9 aspect ratio.
multiplier = 40
FIGURE_DEFAULT_HEIGHT = 16 * multiplier  # rows
FIGURE_DEFAULT_WIDTH= 9 * multiplier  # columns


def compute_boxes(img, rows=None, columns=None):
    """
    Given an input image, compute the coordinates of tiles that would split the image in rows and columns.

    """
    if not rows or not columns:
        return []

    img_width, img_height, _ = img.shape
    logger.info("Image size: %i columns, %i rows", img_width, img_height)
    logger.info("Tiling: %i columns (of width %i), %i rows (of height %i)", columns, FIGURE_DEFAULT_WIDTH, rows, FIGURE_DEFAULT_HEIGHT)

    for i in range(columns):
        for j in range(rows):
            box_ll = i * FIGURE_DEFAULT_WIDTH, j * FIGURE_DEFAULT_HEIGHT
            box_ur = (i+1) * FIGURE_DEFAULT_WIDTH, (j+1) * FIGURE_DEFAULT_HEIGHT
            yield (box_ll, box_ur)
            # Each box is represented with a tuple of its lower-left and upper-right corners: (ll_x, ll_y), (ur_x, ur_y)


def scale_img_to_best_fit(img):
    return img


def crop_image(img, rows=None, columns=None):
    if not rows or not columns:
        return []

    rescaled_img = scale_img_to_best_fit(img)
    for ll, ur in compute_boxes(rescaled_img, rows=rows, columns=columns):
        ll_x, ll_y = ll
        ur_x, ur_y = ur
        logger.info("tile slice_along_axes: %s, %s", str((ll_x, ur_x)), str((ll_y, ur_y)))
        cropped_img = slice_along_axes(img, [(ll_x, ur_x), (ll_y, ur_y)])
        yield cropped_img


def is_prime(n):
    """Return True if the given number is a prime. Hack. Only checks lower than 100. Fix it."""
    return n in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def factorize(n):
    for i in range(1, n):
        for j in range(1, n):
            if i * j == n:
                logger.info("factors: %i, %i", i, j)
                yield (i, j)


def get_tiles(img, n_tiles):
    img_height, img_width, _ = img.shape
    img_aspect_ratio = img_height / img_width
    logger.info("img_aspect_ratio: %f (%s)", img_aspect_ratio, str(img.shape))

    
    total_tiles = n_tiles
    while is_prime(total_tiles):
        total_tiles += 1

    logger.info("Total tiles: %i", total_tiles)
    # search for the N and M whose ratio is closer to the image's aspect ratio
    min = 1_000_000.0  # Arbitrary big number.
    n = 1
    m = 1
    rows = n
    cols = m
    for n, m in factorize(total_tiles):
        logger.info("N, M: %i, %i", n, m)
        logger.info("aspect ratio: %f", n/m)
        if abs(n/m - img_aspect_ratio) < min:
            rows = n
            cols = m
    logger.info("rows, cols: %i, %i", rows, cols)
    logger.info("aspect ratio: %f", rows/cols)
    return crop_image(img, rows=rows, columns=cols)


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt

    FORMAT = "%(asctime)s %(levelno)s %(module)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    img = io.imread(sys.argv[1])
    n_tiles = int(sys.argv[2])

    

    tiles = get_tiles(img, n_tiles)
    for t in tiles:
        plt.figure()
        plt.imshow(t)
        plt.tight_layout()
    plt.show()
    plt.imshow(img)
