# -*- coding: utf-8 -*-

import hashlib
import os
import re
import shutil
import typing

from PIL import Image
import pytest
from wand.exceptions import PolicyError
from wand.image import Image as WandImage

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager
from preview_generator.preview.builder.document__scribus import DocumentPreviewBuilderScribus
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
TEST_FILE_NAME = "DoublePage.sla"
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, TEST_FILE_NAME)
PDF_FILE_HASH = hashlib.md5(IMAGE_FILE_PATH.encode("utf-8")).hexdigest()
JPEG_FILE_HASH = hashlib.md5(
    os.path.join(CACHE_DIR, PDF_FILE_HASH + ".pdf").encode("utf-8")
).hexdigest()


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    if "TRAVIS" in os.environ:
        pytest.skip("Experimental feature -- skipping test in travis environnement")
    try:
        DocumentPreviewBuilderScribus.check_dependencies()
    except BuilderDependencyNotFound as err:
        pytest.skip("skipping scribus: {!s}".format(err))


def test_to_pdf_full_export() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_pdf_preview(file_path=IMAGE_FILE_PATH, page=-1, force=True)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == (os.path.join(CACHE_DIR, PDF_FILE_HASH + ".pdf"))


def test_to_pdf_one_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=IMAGE_FILE_PATH) is True
    path_0 = manager.get_pdf_preview(file_path=IMAGE_FILE_PATH, page=0, force=True)
    assert os.path.exists(path_0) is True
    assert os.path.getsize(path_0) > 0
    assert path_0 == os.path.join(CACHE_DIR, PDF_FILE_HASH + "-page0.pdf")

    path_1 = manager.get_pdf_preview(file_path=IMAGE_FILE_PATH, page=1, force=True)
    assert os.path.exists(path_1) is True
    assert os.path.getsize(path_1) > 0
    assert path_1 == os.path.join(CACHE_DIR, PDF_FILE_HASH + "-page1.pdf")


def test_to_pdf_no_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_pdf_preview(file_path=IMAGE_FILE_PATH, force=True)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert path_to_file == (os.path.join(CACHE_DIR, PDF_FILE_HASH + ".pdf"))

    try:
        with WandImage(filename=path_to_file) as pdf:
            assert len(pdf.sequence) == 2
    except PolicyError:
        pytest.skip("You must update ImageMagic policy file to allow PDF files")


def test_to_jpeg() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
    path0 = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH, height=512, width=256, page=0, force=True
    )
    assert os.path.exists(path0) is True
    assert os.path.getsize(path0) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path0)

    with Image.open(path0) as jpeg:
        assert jpeg.height == 357
        assert jpeg.width == 256

    path1 = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH, height=512, width=256, page=1, force=True
    )
    assert os.path.exists(path1) is True
    assert os.path.getsize(path1) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path1)

    with Image.open(path1) as jpeg:
        assert jpeg.height == 357
        assert jpeg.width == 256


def test_to_jpeg_no_size() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(file_path=IMAGE_FILE_PATH, page=0, force=True)
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(182, 185)


def test_to_jpeg_no_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(
        file_path=IMAGE_FILE_PATH, height=512, width=512, force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 367


def test_to_jpeg_no_size_no_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=IMAGE_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(file_path=IMAGE_FILE_PATH, force=True)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(182, 185)


def test_to_text() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_text_preview(file_path=IMAGE_FILE_PATH) is False
    with pytest.raises(UnavailablePreviewType):
        manager.get_text_preview(file_path=IMAGE_FILE_PATH, force=True)


def test_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_json_preview(file_path=IMAGE_FILE_PATH) is True
    manager.get_json_preview(file_path=IMAGE_FILE_PATH, force=True)
    # TODO - G.M - 2018-11-06 - To be completed
