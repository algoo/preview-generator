import hashlib
import os
import re

from PIL import Image
import pytest

from preview_generator.manager import PreviewManager
from preview_generator.utils import executable_is_available
from tests import test_utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"
DOCX_FILE_PATH = os.path.join(CURRENT_DIR, "the_docx.docx")
DOCX_FILE_PATH_NO_EXTENSION = os.path.join(CURRENT_DIR, "the_docx")
FILE_HASH = hashlib.md5(DOCX_FILE_PATH.encode("utf-8")).hexdigest()
DOCX_FILE_EXT = ".docx"

if not executable_is_available("libreoffice"):
    pytest.skip("libreoffice is not available.", allow_module_level=True)


def test_docx_to_jpeg() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert manager.has_jpeg_preview(file_path=DOCX_FILE_PATH) is True
    path0 = manager.get_jpeg_preview(
        file_path=DOCX_FILE_PATH, height=512, width=256, page=0, force=True
    )
    assert os.path.exists(path0)
    assert os.path.getsize(path0) > 0
    re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path0)

    with Image.open(path0) as jpeg:
        assert jpeg.height in range(361, 363)
        assert jpeg.width == 256

    path1 = manager.get_jpeg_preview(
        file_path=DOCX_FILE_PATH, height=512, width=256, page=1, force=True
    )
    assert os.path.exists(path1)
    assert os.path.getsize(path1) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path1)

    with Image.open(path1) as jpeg:
        assert jpeg.height in range(361, 363)
        assert jpeg.width == 256


def test_docx_to_jpeg_no_extension() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert (
        manager.has_jpeg_preview(file_path=DOCX_FILE_PATH_NO_EXTENSION, file_ext=DOCX_FILE_EXT)
        is True
    )
    path0 = manager.get_jpeg_preview(
        file_path=DOCX_FILE_PATH_NO_EXTENSION,
        file_ext=DOCX_FILE_EXT,
        height=512,
        width=256,
        page=0,
        force=True,
    )
    assert os.path.exists(path0)
    assert os.path.getsize(path0) > 0
    re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path0)

    with Image.open(path0) as jpeg:
        assert jpeg.height in range(361, 363)
        assert jpeg.width == 256

    path1 = manager.get_jpeg_preview(
        file_path=DOCX_FILE_PATH_NO_EXTENSION,
        file_ext=DOCX_FILE_EXT,
        height=512,
        width=256,
        page=1,
        force=True,
    )
    assert os.path.exists(path1)
    assert os.path.getsize(path1) > 0
    assert re.match(test_utils.CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG, path1)

    with Image.open(path1) as jpeg:
        assert jpeg.height in range(361, 363)
        assert jpeg.width == 256


def test_docx_get_nb_page() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    nb_page = manager.get_page_nb(file_path=DOCX_FILE_PATH)
    assert nb_page in [2, 3]


def test_docx_get_nb_page_no_extension() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    nb_page = manager.get_page_nb(file_path=DOCX_FILE_PATH_NO_EXTENSION, file_ext=DOCX_FILE_EXT)
    assert nb_page in [2, 3]
