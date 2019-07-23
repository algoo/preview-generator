# -*- coding: utf-8 -*-

import hashlib
import os
import shutil
import typing

import pytest

from preview_generator.exception import UnsupportedMimeType
from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
BINARY_FILE_PATH = os.path.join(CURRENT_DIR, "binary_file.bin")
BINARY_FILE_PATH_WITHOUT_EXT = os.path.join(CURRENT_DIR, "binary_file")
FILE_HASH = hashlib.md5(BINARY_FILE_PATH.encode("utf-8")).hexdigest()


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_to_jpeg(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.get_jpeg_preview(file_path=file_path, height=256, width=512)


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_get_nb_page(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.get_page_nb(file_path=file_path, file_ext=".bin")


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_to_jpeg__default_size(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.get_jpeg_preview(file_path=file_path, file_ext=".bin")


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_to_json(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.get_json_preview(file_path=file_path, force=True)


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_to_pdf(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.get_pdf_preview(file_path=file_path, force=True)


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_has_pdf_preview(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.has_pdf_preview(file_path=file_path, file_ext=".bin")


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_has_jpeg_preview(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.has_jpeg_preview(file_path=file_path, file_ext=".bin")


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_has_json_preview(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.has_json_preview(file_path=file_path, file_ext=".bin")


@pytest.mark.parametrize("file_path", [BINARY_FILE_PATH, BINARY_FILE_PATH_WITHOUT_EXT])
def test_has_html_preview(file_path) -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnsupportedMimeType):
        manager.has_html_preview(file_path=file_path, file_ext=".bin")
