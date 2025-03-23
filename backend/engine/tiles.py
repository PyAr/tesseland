from math import ceil
from PIL import Image


# Most smartphones featured a 16:9 aspect ratio.
multiplier = 40
DEFAULT_HEIGHT = 19 * multiplier  # rows
DEFAULT_WIDTH = 9 * multiplier  # columns


def compute_boxes(rows=None, columns=None):
    """
    Given an input image, compute the coordinates of tiles that would split the image in rows and columns.

    """
    if not rows or not columns:
        return []

    print("Tiling: %i columns (of width %i), %i rows (of height %i)" %(columns, DEFAULT_WIDTH, rows, DEFAULT_HEIGHT))

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


def crop_image(image=None, rows=None, columns=None):
    if image is None or rows is None or columns is None:
        return []

    for ul, lr in compute_boxes(rows=rows, columns=columns):
        ul_x, ul_y = ul
        lr_x, lr_y = lr

        tile = image.transform(
            (DEFAULT_WIDTH, DEFAULT_HEIGHT),  
            method=Image.Transform.EXTENT, 
            data=(ul_x, ul_y, lr_x, lr_y)
        )
        yield tile


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


def fit_image_in_display(img, total_tiles):
    """
    Given the display's dimensions, create a new image that fits exactly in the display.
    REturn a display configuration that's a dict with the image and the number of rows and columns.
    """
    img_width, img_height = img.size
    print("img_height:", img_height, " img_width: ", img_width)

    scaling_factor, rows, cols = find_best_tiling(img_height, img_width, total_tiles)
    display_height = rows * DEFAULT_HEIGHT
    display_width = cols * DEFAULT_WIDTH
    print("Display height:", display_height, ", display width: ", display_width)

    scaled_img_width = ceil(img_width * scaling_factor)
    scaled_img_height = ceil(img_height * scaling_factor)
    print("Scaling factor:", scaling_factor, "Rows:", rows, ", Columns: ", cols)
    print("scaled img_height:", scaled_img_height, ", scaled img_width: ", scaled_img_width)

    scaled_image = img.resize((scaled_img_width, scaled_img_height))

    scaled_img_height, scaled_img_width = img_height * scaling_factor, img_width * scaling_factor
    display_height, display_width = rows * DEFAULT_HEIGHT, cols * DEFAULT_WIDTH

    # Fit the scaled image into the display, filling the gaps with a background image.
    final_img = create_background((display_width, display_height))
    offset_H = ceil((display_height - scaled_img_height) / 2)
    offset_W = ceil((display_width - scaled_img_width) / 2)
    final_img.paste(scaled_image, (offset_W, offset_H))

    return {"image": final_img, "rows": rows, "columns": cols}

def get_tiles(image_path: str, n_tiles):
    if n_tiles < 2:
        raise Exception("Tiles must be at least 2.")
    img = Image.open(image_path)

    total_tiles = n_tiles
    while is_prime(total_tiles):
        total_tiles += 1

    display_config = fit_image_in_display(img, total_tiles)

    return crop_image(**display_config)


def create_background(shape):
    import random
    from pathlib import Path
    parent_directory = Path(__file__).parent
    bgs = parent_directory / "bgs"

    bgs = [file for file in (parent_directory / "bgs").iterdir()
            if file.is_file() and file.suffix.lower() == '.png']
    random.shuffle(bgs)

    img = Image.open(bgs[0])
    reshaped = img.resize(shape, Image.Resampling.LANCZOS)
    return reshaped


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt


    img = sys.argv[1]
    n_tiles = int(sys.argv[2])
    plt.figure()
    plt.imshow(Image.open(img))
    

    print("Ddfault display tiles size. Heigth: ", DEFAULT_HEIGHT, ", Width: ", DEFAULT_WIDTH)
    tiles = get_tiles(img, n_tiles)
    for t in tiles:
        plt.figure()
        plt.imshow(t)
        plt.tight_layout()
    plt.show()
    
