# -*- coding: utf-8 -*-

import hashlib
import os
import re
import shutil
import subprocess
import typing

from PIL import Image
from PyPDF2 import PdfFileReader
import pytest

from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager
from preview_generator.utils import executable_is_available
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
ODT_FILE_PATH = os.path.join(CURRENT_DIR, "the_odt.odt")
FILE_HASH = hashlib.md5(ODT_FILE_PATH.encode("utf-8")).hexdigest()

if not executable_is_available("libreoffice"):
    pytest.skip("libreoffice is not available.", allow_module_level=True)


@pytest.fixture
def set_small_process_timeout() -> typing.Generator[None, None, None]:
    from preview_generator.preview.builder import office__libreoffice as lo

    value = lo.LIBREOFFICE_PROCESS_TIMEOUT
    lo.LIBREOFFICE_PROCESS_TIMEOUT = 0.1
    yield
    lo.LIBREOFFICE_PROCESS_TIMEOUT = value


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=ODT_FILE_PATH) is True
    path0 = manager.get_jpeg_preview(
        file_path=ODT_FILE_PATH, height=512, width=256, page=0, force=True
    )
    assert os.path.exists(path0)
    assert os.path.getsize(path0) > 0
    re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path0)

    with Image.open(path0) as jpeg:
        assert jpeg.height in range(361, 363)
        assert jpeg.width == 256

    path1 = manager.get_jpeg_preview(
        file_path=ODT_FILE_PATH, height=512, width=256, page=1, force=True
    )
    assert os.path.exists(path1)
    assert os.path.getsize(path1) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path1)

    with Image.open(path1) as jpeg:
        assert jpeg.height in range(361, 363)
        assert jpeg.width == 256


def test_to_jpeg_no_size() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=ODT_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(file_path=ODT_FILE_PATH, page=0, force=True)
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(180, 182)


def test_to_jpeg_no_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=ODT_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(
        file_path=ODT_FILE_PATH, height=512, width=512, force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width in range(361, 363)


def test_to_jpeg_no_size_no_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=ODT_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(file_path=ODT_FILE_PATH, force=True)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(180, 182)


def test_to_pdf_full_export() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=ODT_FILE_PATH) is True
    path_to_file = manager.get_pdf_preview(file_path=ODT_FILE_PATH, page=-1, force=True)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__PDF, path_to_file)


def test_to_pdf_one_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=ODT_FILE_PATH) is True
    path_0 = manager.get_pdf_preview(file_path=ODT_FILE_PATH, page=0, force=True)
    assert os.path.exists(path_0) is True
    assert os.path.getsize(path_0) > 1000  # verify if the size of the pdf refer to a normal content
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__PDF, path_0)
    pdf = PdfFileReader(open(path_0, "rb"))
    assert pdf.getNumPages() == 1

    path_1 = manager.get_pdf_preview(file_path=ODT_FILE_PATH, page=1, force=True)
    assert os.path.exists(path_1) is True
    assert os.path.getsize(path_1) > 1000  # verify if the size of the pdf refer to a normal content
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__PDF, path_1)
    pdf = PdfFileReader(open(path_1, "rb"))
    assert pdf.getNumPages() == 1


def test_to_pdf_no_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=ODT_FILE_PATH) is True
    path_to_file = manager.get_pdf_preview(file_path=ODT_FILE_PATH, force=True)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__PDF, path_to_file)

    pdf = PdfFileReader(open(path_to_file, "rb"))
    assert pdf.getNumPages() == 2


def test_to_text() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_text_preview(file_path=ODT_FILE_PATH) is False
    with pytest.raises(UnavailablePreviewType):
        manager.get_text_preview(file_path=ODT_FILE_PATH, force=True)


def test_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_json_preview(file_path=ODT_FILE_PATH) is True
    manager.get_json_preview(file_path=ODT_FILE_PATH, force=True)
    # TODO - G.M - 2018-11-06 - To be completed


def test_to_pdf() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=ODT_FILE_PATH) is True
    manager.get_pdf_preview(file_path=ODT_FILE_PATH, force=True)
    # TODO - G.M - 2018-11-06 - To be completed


@pytest.mark.usefixtures("set_small_process_timeout")
def test_to_pdf__err_timeout() -> None:
    with pytest.raises(subprocess.TimeoutExpired):
        manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
        manager.get_pdf_preview(file_path=ODT_FILE_PATH, force=True)


def test_get_nb_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    nb_page = manager.get_page_nb(file_path=ODT_FILE_PATH)
    assert nb_page == 2
