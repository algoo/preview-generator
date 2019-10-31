# -*- coding: utf-8 -*-

import os
import shutil
import typing

import pytest

from preview_generator.manager import PreviewManager
from preview_generator.utils import executable_is_available

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, "the_text.txt")
IMAGE_FILE_PATH_NO_EXTENSION = os.path.join(CURRENT_DIR, "the_text_no_extension")  # nopep8


if not executable_is_available("libreoffice"):
    pytest.skip("libreoffice is not available.", allow_module_level=True)


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_text_to_jpeg() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    image_file_path = IMAGE_FILE_PATH
    assert manager.has_jpeg_preview(file_path=image_file_path) is True
    path_to_file = manager.get_jpeg_preview(file_path=image_file_path, force=True)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0


def test_to_pdf() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    image_file_path = IMAGE_FILE_PATH
    assert manager.has_jpeg_preview(file_path=image_file_path) is True
    path_to_file = manager.get_pdf_preview(file_path=image_file_path, force=True)
    assert os.path.exists(path_to_file) is True


def test_page_number() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    page_number = manager.get_page_nb(file_path=IMAGE_FILE_PATH)
    assert page_number == 1


def test_to_pdf_no_extension() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    image_file_path = IMAGE_FILE_PATH_NO_EXTENSION
    assert manager.has_jpeg_preview(file_path=image_file_path) is True
    path_to_file = manager.get_pdf_preview(file_path=image_file_path, force=True)
    assert os.path.exists(path_to_file) is True


def test_to_pdf_no_extension_extension_forced() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    image_file_path = IMAGE_FILE_PATH_NO_EXTENSION
    assert manager.has_pdf_preview(file_path=image_file_path, file_ext=".txt") is True
    path_to_file = manager.get_pdf_preview(file_path=image_file_path, force=True, file_ext=".txt")
    assert os.path.exists(path_to_file) is True


def test_to_jpeg_no_extension() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    image_file_path = IMAGE_FILE_PATH_NO_EXTENSION
    assert manager.has_jpeg_preview(file_path=image_file_path) is True
    path_to_file = manager.get_jpeg_preview(file_path=image_file_path, force=True)
    assert os.path.exists(path_to_file) is True


def test_to_jpeg_no_extension_extension_forced() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    image_file_path = IMAGE_FILE_PATH_NO_EXTENSION
    assert manager.has_jpeg_preview(file_path=image_file_path, file_ext=".txt") is True
    path_to_file = manager.get_jpeg_preview(file_path=image_file_path, force=True, file_ext=".txt")
    assert os.path.exists(path_to_file) is True


def test_page_number__no_extension() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    page_number = manager.get_page_nb(file_path=IMAGE_FILE_PATH_NO_EXTENSION)
    assert page_number == 1


def test_page_number__extension_forced() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    page_number = manager.get_page_nb(file_path=IMAGE_FILE_PATH_NO_EXTENSION, file_ext=".txt")
    assert page_number == 1


def test_to_text() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_text_preview(file_path=IMAGE_FILE_PATH) is True
    manager.get_text_preview(file_path=IMAGE_FILE_PATH, force=True)
    # TODO - G.M - 2018-11-06 - To be completed


def test_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_json_preview(file_path=IMAGE_FILE_PATH) is True
    manager.get_json_preview(file_path=IMAGE_FILE_PATH, force=True)
    # TODO - G.M - 2018-11-06 - To be completed
