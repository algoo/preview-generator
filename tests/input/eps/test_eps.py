# -*- coding: utf-8 -*-

import os
from PIL import Image
import pytest
import shutil
from wand.exceptions import PolicyError

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg():
    try:
        manager = PreviewManager(
            cache_folder_path=CACHE_DIR,
            create_folder=True
        )
        path_to_file = manager.get_jpeg_preview(
            file_path=os.path.join(CURRENT_DIR, 'algoo.eps'),
            height=512,
            width=321,
            force=True
        )
        assert os.path.exists(path_to_file) is True
        assert os.path.getsize(path_to_file) > 0
        with Image.open(path_to_file) as jpeg:
            assert jpeg.height == 321
            assert jpeg.width == 321
    except PolicyError:
        pytest.skip(
            'You must update ImageMagic policy file to allow EPS convert'
        )


def test_to_jpeg_no_size():
    try:
        manager = PreviewManager(
            cache_folder_path=CACHE_DIR,
            create_folder=True
        )
        path_to_file = manager.get_jpeg_preview(
            file_path=os.path.join(CURRENT_DIR, 'algoo.eps'),
            force=True
        )
        assert os.path.exists(path_to_file) is True
        assert os.path.getsize(path_to_file) > 0
        with Image.open(path_to_file) as jpeg:
            assert jpeg.height == 256
            assert jpeg.width == 256
    except PolicyError:
        pytest.skip(
            'You must update ImageMagic policy file to allow EPS convert'
        )
