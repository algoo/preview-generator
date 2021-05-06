# -*- coding: utf-8 -*-

import os
import re
import shutil
import typing

from PIL import Image
from PyPDF2 import PdfFileReader
import PyPDF2.utils
import pytest

from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
PDF_FILE_PATH = os.path.join(CURRENT_DIR, "the_pdf.pdf")
PDF_FILE_PATH__ENCRYPTED = os.path.join(CURRENT_DIR, "the_pdf.encrypted.pdf")
PDF_FILE_PATH__A4 = os.path.join(CURRENT_DIR, "qpdfconvert.pdf")


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=PDF_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(
        file_path=PDF_FILE_PATH, height=512, width=321, force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(453, 455)
        assert jpeg.width == 321


def test_to_jpeg__encrypted_pdf() -> None:
    with pytest.raises(PyPDF2.utils.PdfReadError):  #  ensure file is encrpyted
        pdf = PdfFileReader(PDF_FILE_PATH__ENCRYPTED)
        pdf.getPage(0)

    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=PDF_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(
        file_path=PDF_FILE_PATH__ENCRYPTED, height=512, width=321, force=True
    )

    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(453, 455)
        assert jpeg.width == 321


def test_to_jpeg_no_size() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=PDF_FILE_PATH) is True
    path_to_file = manager.get_jpeg_preview(file_path=PDF_FILE_PATH, force=True)
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN__JPEG, path_to_file)

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(180, 182)


def test_to_text() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_text_preview(file_path=PDF_FILE_PATH) is False
    with pytest.raises(UnavailablePreviewType):
        manager.get_text_preview(file_path=PDF_FILE_PATH, force=True)


def test_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_json_preview(file_path=PDF_FILE_PATH) is True
    manager.get_json_preview(file_path=PDF_FILE_PATH, force=True)
    # TODO - G.M - 2018-11-06 - To be completed


def test_to_pdf() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=PDF_FILE_PATH) is True
    manager.get_pdf_preview(file_path=PDF_FILE_PATH, force=True)
    # TODO - G.M - 2018-11-06 - To be completed


def test_to_pdf_one_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_pdf_preview(file_path=PDF_FILE_PATH) is True
    path_0 = manager.get_pdf_preview(file_path=PDF_FILE_PATH, page=0, force=True)
    assert os.path.exists(path_0) is True
    assert os.path.getsize(path_0) > 1000  # verify if the size of the pdf refer to a normal content
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__PDF, path_0)
    pdf = PdfFileReader(open(path_0, "rb"))
    assert pdf.getNumPages() == 1

    path_1 = manager.get_pdf_preview(file_path=PDF_FILE_PATH, page=1, force=True)
    assert os.path.exists(path_1) is True
    assert os.path.getsize(path_1) > 1000  # verify if the size of the pdf refer to a normal content
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__PDF, path_1)
    pdf = PdfFileReader(open(path_1, "rb"))
    assert pdf.getNumPages() == 1


def test_algorithm4() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=PDF_FILE_PATH__A4) is True
    path_to_file = manager.get_jpeg_preview(file_path=PDF_FILE_PATH__A4, force=True)
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width in range(180, 182)


def test_get_nb_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    nb_page = manager.get_page_nb(file_path=PDF_FILE_PATH)
    assert nb_page == 2
    nb_page = manager.get_page_nb(file_path=PDF_FILE_PATH__ENCRYPTED)
    assert nb_page == 2
    nb_page = manager.get_page_nb(file_path=PDF_FILE_PATH__A4)
    assert nb_page == 2
