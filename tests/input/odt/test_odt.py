# -*- coding: utf-8 -*-

import os
from PIL import Image
from wand.image import Image as WandImage
import shutil

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, 'the_jpeg.jpeg')


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path0 = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        height=512,
        width=256,
        page=0,
        force=True
    )
    assert os.path.exists(path0) == True
    assert os.path.getsize(path0) > 0
    assert path0 == '/tmp/preview-generator-tests/cache/22dd222de01caa012b7b214747169d41-256x512-page0.jpeg'  # nopep8

    with Image.open(path0) as jpeg:
        assert jpeg.height in range(361, 363)
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
    assert path1 == '/tmp/preview-generator-tests/cache/22dd222de01caa012b7b214747169d41-256x512-page1.jpeg'  # nopep8
    with Image.open(path1) as jpeg:
        assert jpeg.height in range(361, 363)
        assert jpeg.width == 256


def test_to_jpeg_no_size():
    manager = PreviewManager(
        cache_folder_path=CACHE_DIR,
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=0,
        force=True
    )
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/22dd222de01caa012b7b214747169d41-256x256-page0.jpeg'  # nopep8
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(180, 182)


def test_to_jpeg_no_page():
    manager = PreviewManager(
        cache_folder_path=CACHE_DIR,
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
    assert path_to_file == '/tmp/preview-generator-tests/cache/22dd222de01caa012b7b214747169d41-512x512.jpeg'  # nopep8

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width in range(361, 363)


def test_to_jpeg_no_size_no_page():
    manager = PreviewManager(
        cache_folder_path=CACHE_DIR,
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/22dd222de01caa012b7b214747169d41-256x256.jpeg'  # nopep8
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(180, 182)


def test_to_pdf_full_export():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=-1,
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/565e100b2c2337222cf1a551f36c17e7.pdf'  # nopep8


def test_to_pdf_one_page():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_0 = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=0,
        force=True
    )
    assert os.path.exists(path_0) == True
    assert os.path.getsize(path_0) > 0
    assert path_0 == '/tmp/preview-generator-tests/cache/565e100b2c2337222cf1a551f36c17e7-page0.pdf'  # nopep8

    path_1 = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=1,
        force=True
    )
    assert os.path.exists(path_1) == True
    assert os.path.getsize(path_1) > 0
    assert path_1 == '/tmp/preview-generator-tests/cache/565e100b2c2337222cf1a551f36c17e7-page1.pdf'  # nopep8


def test_to_pdf_no_page():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        force=True
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == '/tmp/preview-generator-tests/cache/565e100b2c2337222cf1a551f36c17e7.pdf'  # nopep8
    with WandImage(filename=path_to_file) as pdf:
        assert len(pdf.sequence) == 2
