# -*- coding: utf-8 -*-

import os
import shutil
import typing

from PIL import Image
import pytest
from wand.exceptions import PolicyError

from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, "algoo.eps")


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg() -> None:
    try:
        manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
        assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
        path_to_file = manager.get_jpeg_preview(
            file_path=IMAGE_FILE_PATH, height=512, width=321, force=True
        )
        assert os.path.exists(path_to_file) is True
        assert os.path.getsize(path_to_file) > 0
        with Image.open(path_to_file) as jpeg:
            assert jpeg.height == 321
            assert jpeg.width == 321
    except PolicyError:
        pytest.skip("You must update ImageMagic policy file to allow EPS convert")


def test_to_jpeg_no_size() -> None:
    try:
        manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
        assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
        path_to_file = manager.get_jpeg_preview(file_path=IMAGE_FILE_PATH, force=True)
        assert os.path.exists(path_to_file) is True
        assert os.path.getsize(path_to_file) > 0
        with Image.open(path_to_file) as jpeg:
            assert jpeg.height == 256
            assert jpeg.width == 256
    except PolicyError:
        pytest.skip("You must update ImageMagic policy file to allow EPS convert")


def test_to_text() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_text_preview(file_path=IMAGE_FILE_PATH) is False
    with pytest.raises(UnavailablePreviewType):
        manager.get_text_preview(file_path=IMAGE_FILE_PATH, force=True)


def test_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_json_preview(file_path=IMAGE_FILE_PATH) is True
    manager.get_json_preview(file_path=IMAGE_FILE_PATH, force=True)
    # TODO - G.M - 2018-11-06 - To be completed


def test_to_pdf() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=IMAGE_FILE_PATH) is False
    with pytest.raises(UnavailablePreviewType):
        manager.get_pdf_preview(file_path=IMAGE_FILE_PATH, force=True)
