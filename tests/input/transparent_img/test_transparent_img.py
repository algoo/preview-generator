import os
import re
import shutil
import typing

from wand.color import Color
from wand.image import Image

from preview_generator.manager import PreviewManager
from preview_generator.utils import ImgDims
from preview_generator.utils import compute_resize_dims
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_gif_to_jpeg_with_background_white() -> None:
    image_file_path = os.path.join(CURRENT_DIR, "the_gif.gif")
    to_size = ImgDims(width=512, height=256)
    with Image(filename=image_file_path) as input_img:
        input_size = ImgDims(width=input_img.width, height=input_img.height)
    expected_size = compute_resize_dims(input_size, to_size)

    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=image_file_path) is True

    path_to_file = manager.get_jpeg_preview(
        file_path=image_file_path, width=to_size.width, height=to_size.height, force=True
    )

    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image(filename=path_to_file) as output_img:
        assert output_img.width == expected_size.width
        assert output_img.height == expected_size.height
        assert nearest_colour_white(output_img[1][1])


def test_png_to_jpeg_with_background_white() -> None:
    image_file_path = os.path.join(CURRENT_DIR, "the_png.png")
    to_size = ImgDims(width=512, height=256)
    with Image(filename=image_file_path) as input_img:
        input_size = ImgDims(width=input_img.width, height=input_img.height)
    expected_size = compute_resize_dims(input_size, to_size)

    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=image_file_path) is True

    path_to_file = manager.get_jpeg_preview(
        file_path=image_file_path, width=to_size.width, height=to_size.height, force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image(filename=path_to_file) as output_img:
        assert output_img.width == expected_size.width
        assert output_img.height == expected_size.height
        assert nearest_colour_white(output_img[5][5])


def nearest_colour_white(color: Color) -> bool:
    return color.red_int8 >= 250 and color.green_int8 >= 250 and color.blue_int8 >= 250
