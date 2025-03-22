import pytest

from backend.engine.tiles import find_best_tiling, DEFAULT_WIDTH, DEFAULT_HEIGHT


def test_find_best_tiling():
    # better than nothing, PyCamp style.
    img_height = 2 * DEFAULT_HEIGHT
    img_width = DEFAULT_WIDTH
    total_tiles = 2
    scaling_factor, rows, columns = find_best_tiling(img_height, img_width, total_tiles)
    print("Case:", rows, columns, "Factor:", scaling_factor)
    assert (rows == 2 and columns == 1)

    img_height = 1 * DEFAULT_HEIGHT
    img_width = 2 * DEFAULT_WIDTH
    total_tiles = 2
    scaling_factor, rows, columns = find_best_tiling(img_height, img_width, total_tiles)
    print("Case:", rows, columns, "Factor:", scaling_factor)
    assert (rows == 1 and columns == 2)

    img_height = 1
    img_width = 1
    total_tiles = 2
    scaling_factor, rows, columns = find_best_tiling(img_height, img_width, total_tiles)
    print("Case:", rows, columns, "Factor:", scaling_factor)
    assert (rows == 1 and columns == 2)

    img_height = 10 * DEFAULT_HEIGHT
    img_width = 10 * DEFAULT_WIDTH
    total_tiles = 100
    scaling_factor, rows, columns = find_best_tiling(img_height, img_width, total_tiles)
    print("Case:", rows, columns, "Factor:", scaling_factor)
    assert (rows == 10 and columns == 10)


    img_height = 10 * DEFAULT_HEIGHT + 100
    img_width = 10 * DEFAULT_WIDTH + 100
    total_tiles = 100
    scaling_factor, rows, columns = find_best_tiling(img_height, img_width, total_tiles)
    print("Case:", rows, columns, "Factor:", scaling_factor)
    assert (rows == 10 and columns == 10)