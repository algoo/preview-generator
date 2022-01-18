import hashlib
import os
import re
import shutil
import typing

from PIL import Image
import pytest
from wand.image import Image as WandImage

from preview_generator.manager import PreviewManager
from preview_generator.utils import ImgDims
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, "special_aspect_img.jpg")
FILE_HASH = hashlib.md5(IMAGE_FILE_PATH.encode("utf-8")).hexdigest()


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_right_aspect_ratio() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(file_path=IMAGE_FILE_PATH, height=256, width=512)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)
    origin_ratio = compute_image_ratio(IMAGE_FILE_PATH)
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
    ratio = compute_image_ratio(path_to_file)
    assert ratio == pytest.approx(origin_ratio, 1e-3)


def compute_image_ratio(filename: str) -> float:
    with WandImage(filename=filename) as img:
        img.auto_orient()
        size = ImgDims(width=img.width, height=img.height)
        return size.ratio()
