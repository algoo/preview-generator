# -*- coding: utf-8 -*-


import json
import os
from PIL import Image
import pytest
import shutil
import hashlib
from tests import test_utils
import re

from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, 'the_gif.gif')
FILE_HASH = hashlib.md5(IMAGE_FILE_PATH.encode('utf-8')).hexdigest()


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg():
    manager = PreviewManager(
        cache_folder_path=CACHE_DIR,
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
        height=256,
        width=512,
        force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(202, 204)
        assert jpeg.width == 512


def test_get_nb_page():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    nb_page = manager.get_page_nb(file_path=IMAGE_FILE_PATH)
    # FIXME must add parameter force=True/False in the API
    assert nb_page == 1


def test_to_jpeg__default_size():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
        force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(100, 102)
        assert jpeg.width == 256


def test_to_json():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_json_preview(
        file_path=IMAGE_FILE_PATH,
        force=True
    )

    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JSON, path_to_file)

    data = json.load(open(path_to_file))
    assert 'Composite:ImageSize' in data.keys()
    assert 'Composite:Megapixels' in data.keys()
    assert 'ExifTool:ExifToolVersion' in data.keys()
    assert 'File:Comment' in data.keys()
    assert 'File:Directory' in data.keys()
    assert 'File:FileAccessDate' in data.keys()
    assert 'File:FileInodeChangeDate' in data.keys()
    assert 'File:FileModifyDate' in data.keys()
    assert 'File:FileName' in data.keys()
    assert 'File:FilePermissions' in data.keys()
    assert 'File:FileSize' in data.keys()
    assert 'File:FileTypeExtension' in data.keys()
    assert 'File:FileType' in data.keys()
    assert 'File:MIMEType' in data.keys()
    assert 'GIF:BackgroundColor' in data.keys()
    assert 'GIF:BitsPerPixel' in data.keys()
    assert 'GIF:ColorResolutionDepth' in data.keys()
    assert 'GIF:Duration' in data.keys()
    assert 'GIF:GIFVersion' in data.keys()
    assert 'GIF:HasColorMap' in data.keys()
    assert 'GIF:ImageHeight' in data.keys()
    assert 'GIF:ImageWidth' in data.keys()
    assert 'SourceFile' in data.keys()


def test_to_pdf():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnavailablePreviewType):
        path_to_file = manager.get_pdf_preview(
            file_path=IMAGE_FILE_PATH,
            force=True
        )
