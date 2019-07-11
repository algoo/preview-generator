# -*- coding: utf-8 -*-

import hashlib
import json
import os
import re
import shutil
import typing

from PIL import Image
import pytest

from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, "the_jpeg.jpeg")
FILE_HASH = hashlib.md5(IMAGE_FILE_PATH.encode("utf-8")).hexdigest()


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(file_path=IMAGE_FILE_PATH, height=256, width=512)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(284, 286)


def test_get_nb_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    nb_page = manager.get_page_nb(file_path=IMAGE_FILE_PATH)
    # FIXME must add parameter force=True/False in the API
    assert nb_page == 1


def test_to_jpeg__default_size() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(file_path=IMAGE_FILE_PATH)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(229, 231)
        assert jpeg.width == 256


def test_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_json_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_json_preview(file_path=IMAGE_FILE_PATH, force=True)

    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JSON, path_to_file)

    data = json.load(open(path_to_file))
    assert "Composite:ImageSize" in data.keys()
    assert "Composite:Megapixels" in data.keys()
    assert "ExifTool:ExifToolVersion" in data.keys()
    assert "File:BitsPerSample" in data.keys()
    assert "File:ColorComponents" in data.keys()
    assert "File:Directory" in data.keys()
    assert "File:EncodingProcess" in data.keys()
    assert "File:FileAccessDate" in data.keys()
    assert "File:FileInodeChangeDate" in data.keys()
    assert "File:FileModifyDate" in data.keys()
    assert "File:FileName" in data.keys()
    assert "File:FilePermissions" in data.keys()
    assert "File:FileSize" in data.keys()
    assert "File:FileType" in data.keys()
    assert "File:FileTypeExtension" in data.keys()
    assert "File:ImageHeight" in data.keys()
    assert "File:ImageWidth" in data.keys()
    assert "File:MIMEType" in data.keys()
    assert "File:YCbCrSubSampling" in data.keys()
    assert "JFIF:JFIFVersion" in data.keys()
    assert "JFIF:ResolutionUnit" in data.keys()
    assert "JFIF:XResolution" in data.keys()
    assert "JFIF:YResolution" in data.keys()
    assert "SourceFile" in data.keys()


def test_to_pdf() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=IMAGE_FILE_PATH) is False
    with pytest.raises(UnavailablePreviewType):
        manager.get_pdf_preview(file_path=IMAGE_FILE_PATH, force=True)


def test_to_text() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_text_preview(file_path=IMAGE_FILE_PATH) is False
    with pytest.raises(UnavailablePreviewType):
        manager.get_text_preview(file_path=IMAGE_FILE_PATH, force=True)
