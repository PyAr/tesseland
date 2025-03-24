from functools import cache

from math import ceil
from PIL import Image


# Most smartphones featured a 16:9 aspect ratio.
multiplier = 40
DEFAULT_HEIGHT = 19 * multiplier  # rows
DEFAULT_WIDTH = 9 * multiplier  # columns


@cache
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


def crop_image(media=None, rows=None, columns=None):
    if media is None or rows is None or columns is None:
        return []

    for ul, lr in compute_boxes(rows=rows, columns=columns):
        ul_x, ul_y = ul
        lr_x, lr_y = lr

        tile = media.transform(
            (DEFAULT_WIDTH, DEFAULT_HEIGHT),  
            method=Image.Transform.EXTENT, 
            data=(ul_x, ul_y, lr_x, lr_y)
        )
        yield tile


def crop_video(media=None, rows=None, columns=None):
    if media is None or rows is None or columns is None:
        return []

    def init_video_writer(idx):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # (WIDTH, HEIGHT)
        return cv2.VideoWriter("video-tile-" + str(idx) + '.mp4', fourcc, 30, (640, 720))
    
    #boxes = enumerate(compute_boxes(rows=rows, columns=columns))
    boxes = [
        ((0, 0), (640, 720)),
        ((640, 0), (1280, 720))
    ]
    output_videos = [init_video_writer(i) for i, _ in enumerate(boxes)]

    while True:
        ret, frame = media.read()
        print(ret)

        if not ret:
            for output_video in output_videos:
                print("Release ", output_video)
                output_video.release()
            break

        for (ul, lr), output_video in zip(boxes, output_videos):
            print("crop tile ", ul, lr)
            ul_x, ul_y = ul
            lr_x, lr_y = lr

            # Following crop assumes the video is colored, 
            # in case it's Grayscale, you may use: crop_img = frame[top:bottom, left:right]  
            crop_img = frame[ul_y: lr_y, ul_x: lr_x, :]
            output_video.write(crop_img)

    return output_videos

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


def scale_video(vid, width, height):
    """
    Resizes each frame of the given video to the specified dimensions while maintaining the aspect ratio.
    Returns a cv2.VideoCapture object for the resized video.
    
    """
    # Get the original video properties
    original_width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(vid.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Calculate the scaling factor to maintain aspect ratio
    scale_factor = min(width / original_width, height / original_height)
    new_width = ceil(original_width * scale_factor)
    new_height = ceil(original_height * scale_factor)

    # Temporary file to save the resized video
    output_file = 'scaled_video.mp4'

    # Create a VideoWriter object for the output video
    output_video = cv2.VideoWriter(output_file, fourcc, fps, (new_width, new_height))
    print("Resize frames to new_width, new_height: ", new_width, new_height)
    while True:
        ret, frame = vid.read()
        if not ret:
            break

        # Resize the frame while maintaining the aspect ratio
        resized_frame = cv2.resize(frame, (new_width, new_height+1), interpolation=cv2.INTER_AREA)
        output_video.write(resized_frame)

    # Release resources
    vid.release()  # TODO: revisar si esto va a acá o en otro lado
    output_video.release()

    # Return a new VideoCapture object for the resized video
    
    v = cv2.VideoCapture(output_file)
    while not v.isOpened():
        print("Trying to open output_file. ")
        import time
        time.sleep(0.5)
        #v = cv2.VideoCapture(output_file)
    return v


def place_video_in_display_size(
        video, 
        vid_height, 
        vid_width, 
        display_width, 
        display_height
    ):
    """
    Centers the video in the given display size without resizing it.
    Adds black padding around the video frames to fit the specified dimensions.
    Returns a cv2.VideoCapture object for the resulting video.
    
    """
    import numpy as np

    # Temporary file to save the padded video
    output_file = 'centered_video.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = int(video.get(cv2.CAP_PROP_FPS))

    # Create a VideoWriter object for the output video
    output_video = cv2.VideoWriter(output_file, fourcc, fps, (display_width, display_height))

    # Calculate offsets to center the video
    offset_x = max(0, (display_width - vid_width) // 2)
    offset_y = max(0, (display_height - vid_height) // 2)

    print("place_video_in_display_size: ",vid_width,vid_height,display_width,display_height)
    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Ensure the frame dimensions match the expected video dimensions
        frame_height, frame_width = frame.shape[:2]
        if frame_height != vid_height or frame_width != vid_width:
            raise ValueError(f"Frame dimensions ({frame_width}, {frame_height}) do not match expected dimensions ({vid_width}, {vid_height}).")

        # Create a black frame with the display size
        padded_frame = np.zeros((display_height, display_width, 3), dtype=np.uint8)

        # Calculate the region where the frame will be placed
        start_y = offset_y
        end_y = offset_y + frame_height
        start_x = offset_x
        end_x = offset_x + frame_width

        # Ensure the slice dimensions match the frame dimensions
        padded_frame[start_y:end_y, start_x:end_x] = frame

        # Write the padded frame to the output video
        output_video.write(padded_frame)

    # Release resources
    video.release()
    output_video.release()

    # Return a new VideoCapture object for the padded video
    return cv2.VideoCapture(output_file)


def fit_video_in_display(video, total_tiles):
    print("fit_video_in_display ", video.isOpened())
    video_width  = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return fit_media_in_display(
        media=video,
        media_width=video_width,
        media_height=video_height,
        total_tiles=total_tiles,
        scale_function=scale_video,
        fit_function=place_video_in_display_size
    )


def place_image_in_background(
        image, 
        img_height, 
        img_width, 
        display_width, 
        display_height
    ):
    final_image = create_background((display_width, display_height))
    offset_H = ceil((display_height - img_height) / 2)
    offset_W = ceil((display_width - img_width) / 2)
    final_image.paste(image, (offset_W, offset_H))
    return final_image


def fit_image_in_display(img, total_tiles):
    img_width, img_height = img.size
    scale_image = lambda image, width, height: image.resize((width, height))

    return fit_media_in_display(
        media=img,
        media_width=img_width,
        media_height=img_height,
        total_tiles=total_tiles,
        scale_function=scale_image,
        fit_function=place_image_in_background
    )


# make all the args kwargs instead
def fit_media_in_display(
        media=None,
        media_width=None,
        media_height=None,
        total_tiles=None,
        scale_function=None,
        fit_function=None
    ):
    """
    Given the display's dimensions, create a new image that fits exactly in the display.
    REturn a display configuration that's a dict with the image and the number of rows and columns.
    """
    
    print("img_height:", media_height, " img_width: ", media_width)

    scaling_factor, rows, cols = find_best_tiling(media_height, media_width, total_tiles)
    display_height = rows * DEFAULT_HEIGHT
    display_width = cols * DEFAULT_WIDTH
    print("Display height:", display_height, ", display width: ", display_width)

    scaled_img_width = ceil(media_width * scaling_factor)
    scaled_img_height = ceil(media_height * scaling_factor)
    print("Scaling factor:", scaling_factor, "Rows:", rows, ", Columns: ", cols)
    print("scaled img_height:", scaled_img_height, ", scaled img_width: ", scaled_img_width)

    scaled_media = scale_function(media, scaled_img_width, scaled_img_height)
    scaled_img_height, scaled_img_width = media_height * scaling_factor, media_width * scaling_factor
    display_height, display_width = rows * DEFAULT_HEIGHT, cols * DEFAULT_WIDTH

    # Fit the scaled image into the display, filling the gaps with a background image.
    final_media = fit_function(
        scaled_media, 
        ceil(scaled_img_height), 
        ceil(scaled_img_width), 
        display_width, 
        display_height
    )

    return {"media": final_media, "rows": rows, "columns": cols}

def get_tiles(image_path: str, n_tiles):
    if n_tiles < 2:
        raise Exception("Tiles must be at least 2.")
    img = Image.open(image_path)

    total_tiles = n_tiles
    while is_prime(total_tiles):
        total_tiles += 1

    display_config = fit_image_in_display(img, total_tiles)

    return crop_image(**display_config)


def get_video_tiles(video_path: str, n_tiles):
    if n_tiles < 2:
        raise Exception("Tiles must be at least 2.")

    total_tiles = n_tiles
    while is_prime(total_tiles):
        total_tiles += 1


    video = cv2.VideoCapture(video_path)
    display_config = fit_video_in_display(video, total_tiles)

    return crop_video(**display_config)


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
    import mimetypes


    media_path = sys.argv[1]
    n_tiles = int(sys.argv[2])

    if mimetypes.guess_type(media_path)[0].startswith('video'):
        print('Processing a video')
        import cv2
        
        # cap = cv2.VideoCapture(media_path)
        # while(cap.isOpened()):
        #     # Capture frame-by-frame
        #     ret, frame = cap.read()
        #     if ret == True:
        #     # Display the resulting frame
        #         cv2.imshow('Frame',frame)
        #     # Press Q on keyboard to  exit
        #     if cv2.waitKey(25) & 0xFF == ord('q'):
        #         break
        # cap.release()
        # cv2.destroyAllWindows()

        x = get_video_tiles(media_path, n_tiles)
        print(x)

    else:
        import matplotlib.pyplot as plt
        print('Processing an image')
        plt.figure()
        plt.imshow(Image.open(media_path))
        

        print("Ddfault display tiles size. Heigth: ", DEFAULT_HEIGHT, ", Width: ", DEFAULT_WIDTH)
        tiles = get_tiles(media_path, n_tiles)
        for t in tiles:
            plt.figure()
            plt.imshow(t)
            plt.tight_layout()
        plt.show()

