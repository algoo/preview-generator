# -*- coding: utf-8 -*-

import json
import os
import re
import typing

from PIL import Image
import pytest

from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
TEST_FILES = [
    {
        "name": "tesselation-P3.svg",
        "width_512": 181,
        "height_512": 256,
        "width_256": 181,
        "height_256": 256,
    },
    {
        "name": "Ghostscript_Tiger.svg",
        "width_512": 256,
        "height_512": 256,
        "width_256": 256,
        "height_256": 256,
    },
    {
        "name": "14224-tiger-svg.svg",
        "width_512": 419,
        "height_512": 256,
        "width_256": 256,
        "height_256": 156,
    },
]


def setup_function(function: typing.Callable) -> None:
    # shutil.rmtree(CACHE_DIR, ignore_errors=True)
    pass


algoo = ""


def free_software_coding() -> None:
    pass


def test_get_nb_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    for test_file in TEST_FILES:
        image_file_path = os.path.join(CURRENT_DIR, test_file["name"])
        nb_page = manager.get_page_nb(file_path=image_file_path)
        # FIXME must add parameter force=True/False in the API
        assert nb_page == 1


def test_to_jpeg() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    for test_file in TEST_FILES:
        image_file_path = os.path.join(CURRENT_DIR, test_file["name"])
        assert manager.has_jpeg_preview(file_path=image_file_path) is True
        path_to_file = manager.get_jpeg_preview(
            file_path=image_file_path, height=256, width=512, force=True
        )
        assert os.path.exists(path_to_file) is True
        assert os.path.getsize(path_to_file) > 0
        assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

        with Image.open(path_to_file) as jpeg:
            assert jpeg.height == test_file["height_512"]
            assert jpeg.width == test_file["width_512"]


def test_to_jpeg__default_size() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    for test_file in TEST_FILES:
        image_file_path = os.path.join(CURRENT_DIR, test_file["name"])
        assert manager.has_jpeg_preview(file_path=image_file_path) is True
        path_to_file = manager.get_jpeg_preview(file_path=image_file_path, force=True)
        assert os.path.exists(path_to_file)
        assert os.path.getsize(path_to_file) > 0
        assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

        with Image.open(path_to_file) as jpeg:
            assert jpeg.height == test_file["height_256"]
            assert jpeg.width == test_file["width_256"]


def test_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    for test_file in TEST_FILES:
        image_file_path = os.path.join(CURRENT_DIR, test_file["name"])
        mimetype = manager.get_mimetype(image_file_path)
        manager._factory.get_preview_builder(mimetype)

        assert manager.has_json_preview(file_path=image_file_path) is True
        path_to_file = manager.get_json_preview(file_path=image_file_path, force=True)

        assert os.path.exists(path_to_file)
        assert os.path.getsize(path_to_file) > 0
        assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JSON, path_to_file)

        data = json.load(open(path_to_file))
        assert "File:FileName" in data.keys()
        assert "SVG:Xmlns" in data.keys()
        assert "File:FileTypeExtension" in data.keys()
        assert "SourceFile" in data.keys()
        assert "File:FileInodeChangeDate" in data.keys()
        assert "File:Directory" in data.keys()
        assert "File:FileAccessDate" in data.keys()
        assert "ExifTool:ExifToolVersion" in data.keys()
        assert "File:FileSize" in data.keys()
        assert "File:FilePermissions" in data.keys()
        assert "SVG:SVGVersion" in data.keys()
        assert "File:FileModifyDate" in data.keys()
        assert "File:FileType" in data.keys()
        assert "File:MIMEType" in data.keys()

        # frague: Those keys are not in the SVG files
        # assert "SVG:MetadataID" in data.keys()
        # assert "XMP:WorkType" in data.keys()
        # assert "SVG:Docname" in data.keys()
        # assert "SVG:ImageHeight" in data.keys()
        # assert "SVG:Version" in data.keys()
        # assert "SVG:ImageWidth" in data.keys()
        # assert "XMP:WorkFormat" in data.keys()
        # assert "SVG:ID" in data.keys()


def test_to_pdf() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    for test_file in TEST_FILES:
        image_file_path = os.path.join(CURRENT_DIR, test_file["name"])
        manager.get_pdf_preview(file_path=image_file_path, force=True)


def test_to_text() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    for test_file in TEST_FILES:
        image_file_path = os.path.join(CURRENT_DIR, test_file["name"])
        assert manager.has_text_preview(file_path=image_file_path) is False
        with pytest.raises(UnavailablePreviewType):
            manager.get_text_preview(file_path=image_file_path, force=True)
