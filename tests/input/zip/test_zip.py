# -*- coding: utf-8 -*-

import json
import os
import shutil
import typing

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, "the_zip.zip")


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_zip_to_text() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_text_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_text_preview(file_path=IMAGE_FILE_PATH)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0


def test_zip_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_json_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_json_preview(file_path=IMAGE_FILE_PATH)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0

    data = json.load(open(path_to_file))
    assert "fileNb" in data.keys()
    assert "files" in data.keys()
    assert "size" in data.keys()
    assert "sizeCompressed" in data.keys()
    assert "lastModification" in data.keys()
    assert "compressionRate" in data.keys()
    assert data["size"] > 0
    assert data["sizeCompressed"] > 0
    assert data["compressionRate"] > 1

    assert len(data["files"]) == 4
    for _file in data["files"]:
        assert "lastModification" in _file.keys()
        assert "name" in _file.keys()
        assert "size" in _file.keys()
        assert "sizeCompressed" in _file.keys()
        assert _file["size"] > 0
        assert _file["sizeCompressed"] > 0


def test_zip_to_html() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_html_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_html_preview(file_path=IMAGE_FILE_PATH)
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0


def test_zip_to_html__no_original_name() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_html_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_html_preview(file_path=IMAGE_FILE_PATH)
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert IMAGE_FILE_PATH.replace(".zip", "") not in path_to_file

    # test default not to put original file name in cache file
    assert manager.has_html_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file2 = manager.get_html_preview(file_path=IMAGE_FILE_PATH)
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert IMAGE_FILE_PATH.replace(".zip", "") not in path_to_file2
