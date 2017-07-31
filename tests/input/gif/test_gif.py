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
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, 'the_gif.gif')


def setup_function(function):
    shutil.rmtree(CACHE_DIR)


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
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/243918a3cda4aa11bfe7603b627a587f-512x256.jpeg'  # nopep8
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
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/243918a3cda4aa11bfe7603b627a587f-256x256.jpeg'  # nopep8
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
    assert path_to_file == '/tmp/preview-generator-tests/cache/243918a3cda4aa11bfe7603b627a587f.json'  # nopep8

    data = json.load(open(path_to_file))
    assert data['width'] == 520
    assert data['height'] == 206
    assert data['size'] == 42625
    assert data['mode'] == 'P'  # P means palette
    assert data['info']['transparency'] == 254
    assert data['info']['comment'] == 'Created with GIMP'
    assert data['info']['background'] == 250
    assert data['info']['version'] == 'GIF89a'
    assert data['info']['duration'] == 40


def test_to_pdf():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    with pytest.raises(UnavailablePreviewType):
        path_to_file = manager.get_pdf_preview(
            file_path=IMAGE_FILE_PATH,
            force=True
        )
