# -*- coding: utf-8 -*-

import os
from PIL import Image
from wand.image import Image as WandImage
import shutil
import hashlib
import re
import pytest
from wand.exceptions import PolicyError

from preview_generator.manager import PreviewManager
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, 'the_jpeg.jpeg')
FILE_HASH = hashlib.md5(IMAGE_FILE_PATH.encode('utf-8')).hexdigest()


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
    assert os.path.exists(path0)
    assert os.path.getsize(path0) > 0
    re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path0)

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
    assert os.path.exists(path1)
    assert os.path.getsize(path1) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path1)

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
    assert re.match(
        test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path_to_file
    )

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
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

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
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

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
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__PDF, path_to_file)


def test_to_pdf_one_page():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_0 = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=0,
        force=True
    )
    assert os.path.exists(path_0) is True
    assert os.path.getsize(path_0) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__PDF, path_0)

    path_1 = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        page=1,
        force=True
    )
    assert os.path.exists(path_1) is True
    assert os.path.getsize(path_1) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__PDF, path_1)


def test_to_pdf_no_page():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_odt.odt'),
        force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__PDF, path_to_file)

    try:
        with WandImage(filename=path_to_file) as pdf:
            assert len(pdf.sequence) == 2
    except PolicyError:
        pytest.skip(
            'You must update ImageMagic policy file to allow PDF files'
        )
