# -*- coding: utf-8 -*-

import os
from PIL import Image
import shutil

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, 'the_jpeg.jpeg')


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg():
    manager = PreviewManager(path=CACHE_DIR, create_folder=True)
    path0 = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        height=512,
        width=256,
        page=0,
        force=True
    )
    assert os.path.exists(path0) == True
    assert os.path.getsize(path0) > 0
    with Image.open(path0) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 256

    path1 = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        height=512,
        width=256,
        page=1,
        force=True
    )
    assert os.path.exists(path1) == True
    assert os.path.getsize(path1) > 0
    with Image.open(path1) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 256


def test_to_jpeg_no_size():
    manager = PreviewManager(
        path=CACHE_DIR,
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=0,
        force=True
    )
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 256


def test_to_jpeg_no_page():
    manager = PreviewManager(
        path=CACHE_DIR,
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        height=512,
        width=512,
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 512


def test_to_jpeg_no_size_no_page():
    manager = PreviewManager(
        path=CACHE_DIR,
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 256


def test_to_pdf_full_export():
    manager = PreviewManager(path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=-1,
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0


def test_to_pdf_one_page():
    manager = PreviewManager(path=CACHE_DIR, create_folder=True)
    path_0 = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=0,
        force=True
    )
    assert os.path.exists(path_0) == True
    assert os.path.getsize(path_0) > 0

    path_1 = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=1,
        force=True
    )
    assert os.path.exists(path_1) == True
    assert os.path.getsize(path_1) > 0


def test_to_pdf_no_page():
    manager = PreviewManager(path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
