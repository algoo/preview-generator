# -*- coding: utf-8 -*-

import os

import pytest
from PIL import Image
import shutil

from preview_generator.exception import UnavailablePreviewType
from tests import test_utils
import re

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, 'the_pdf.pdf')


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg():
    manager = PreviewManager(
        cache_folder_path=CACHE_DIR,
        create_folder=True
    )
    assert manager.has_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
    ) is True
    path_to_file = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
        height=512,
        width=321,
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(453, 455)
        assert jpeg.width == 321


def test_to_jpeg_no_size():
    manager = PreviewManager(
        cache_folder_path=CACHE_DIR,
        create_folder=True
    )
    assert manager.has_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
    ) is True
    path_to_file = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(180, 182)


def test_to_text():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_text_preview(
        file_path=IMAGE_FILE_PATH
    ) is False
    with pytest.raises(UnavailablePreviewType):
        path_to_file = manager.get_text_preview(
            file_path=IMAGE_FILE_PATH,
            force=True
        )


def test_to_json():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_json_preview(
        file_path=IMAGE_FILE_PATH
    ) is True
    path_to_file = manager.get_json_preview(
        file_path=IMAGE_FILE_PATH,
        force=True
    )
    # TODO - G.M - 2018-11-06 - To be completed


def test_to_pdf():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(
        file_path=IMAGE_FILE_PATH
    ) is True
    path_to_file = manager.get_pdf_preview(
        file_path=IMAGE_FILE_PATH,
        force=True
    )
    # TODO - G.M - 2018-11-06 - To be completed
