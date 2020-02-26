# -*- coding: utf-8 -*-

import os
import re
import shutil
import typing

from PIL import Image

from preview_generator.manager import PreviewManager
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, "test_drawio.drawio")


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_drawio_to_jpeg() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH, height=256, width=512, force=True
    )

    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 185
