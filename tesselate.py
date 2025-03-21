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


def compute_boxes(img, tile_height=FIGURE_DEFAULT_HEIGHT, tile_width=FIGURE_DEFAULT_WIDTH):
    """
    Given an input image, compute the coordinates of tiles that would split the image
    in rectangles of tile_width x tile_height.

    """
    img_width, img_height, _ = img.shape
    logger.debug("Image size: %i columns, %i rows", img_width, img_height)

    # using ceil to have tiles that overflow the image
    rows = ceil(img_height / FIGURE_DEFAULT_HEIGHT)
    columns = ceil(img_width / FIGURE_DEFAULT_WIDTH)
    logger.info("Tiling: %i columns (of width %i), %i rows (of height %i)", columns, tile_width, rows, tile_height)

    boxes = []
    for i in range(columns):
        for j in range(rows):
            box_ll = i * FIGURE_DEFAULT_WIDTH, j * FIGURE_DEFAULT_HEIGHT
            box_ur = min((i+1) * FIGURE_DEFAULT_WIDTH, img_width), min((j+1) * FIGURE_DEFAULT_HEIGHT, img_height)
            boxes.append((box_ll, box_ur))

    # Each box is represented with a tuple of its lower-left and upper-right corners: (ll_x, ll_y), (ur_x, ur_y)
    return boxes

def crop_image(img, boxes):
    """
    Given an input image and a tiling definition (computed with compute_boxes),
    return the tiles that bundled together complete the image.

    """
    tiles = []
    for ll, ur in boxes:
        ll_x, ll_y = ll
        ur_x, ur_y = ur
        cropped_img = slice_along_axes(img, [(ll_x, ur_x), (ll_y, ur_y)])
        yield cropped_img


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt

    FORMAT = "%(asctime)s %(levelno)s %(module)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    img = io.imread(sys.argv[1])

    plt.imshow(img)

    boxes = compute_boxes(img)
    logger.info("%i tiles", len(boxes))
    logger.debug("Tiles: %s", str(boxes))

    tiles = crop_image(img, boxes)
    for t in tiles:
        plt.figure()
        plt.imshow(t)
        plt.tight_layout()

    plt.show()
