# -*- coding: utf-8 -*-

import json
import os
from PIL import Image
import pytest
import shutil

from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, 'the_jpeg.jpeg')


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
        width=512
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/f910f2af6cda4fff79f21456e19e021c-512x256.jpeg'  # nopep8
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(284, 286)


def test_get_nb_page():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    nb_page = manager.get_page_nb(file_path=IMAGE_FILE_PATH)
    # FIXME must add parameter force=True/False in the API
    assert nb_page == 1


def test_to_jpeg__default_size():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/f910f2af6cda4fff79f21456e19e021c-256x256.jpeg'  # nopep8
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(229, 231)
        assert jpeg.width == 256


def test_to_json():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    print("REGISTERED BUILDERS:", manager._factory.builders_classes)
    path_to_file = manager.get_json_preview(
        file_path=IMAGE_FILE_PATH,
        force=True
    )

    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/f910f2af6cda4fff79f21456e19e021c.json'  # nopep8

    data = json.load(open(path_to_file))
    assert data['width'] == 236
    assert data['height'] == 212
    assert data['size'] == 8791
    assert data['mode'] == 'RGB'
    assert data['info']

    assert data['info']['dpi'] == [72, 72]
    assert data['info']['jfif_version'] == [1, 1]
    assert data['info']['jfif'] == 257
    assert data['info']['jfif_unit'] == 1
    assert data['info']['progression'] == 1
    assert data['info']['progressive'] == 1
    assert data['info']['jfif_density'] == [72, 72]


def test_to_pdf():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnavailablePreviewType):
        path_to_file = manager.get_pdf_preview(
            file_path=IMAGE_FILE_PATH,
            force=True
        )
