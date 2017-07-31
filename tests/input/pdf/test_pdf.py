# -*- coding: utf-8 -*-

import os
from PIL import Image
import shutil

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg():
    manager = PreviewManager(
        cache_folder_path=CACHE_DIR,
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_pdf.pdf'),
        height=512,
        width=321,
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(453, 455)
        assert jpeg.width == 321


def test_to_jpeg_no_size():
    manager = PreviewManager(
        cache_folder_path=CACHE_DIR,
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_pdf.pdf'),
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(180, 182)
