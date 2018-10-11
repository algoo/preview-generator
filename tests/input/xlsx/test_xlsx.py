# -*- coding: utf-8 -*-

import os
import shutil
import pytest

from preview_generator.manager import PreviewManager
from preview_generator.exception import UnavailablePreviewType

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_text_to_jpeg():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_xlsx.xlsx'),
        force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0


def test_to_pdf():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_xlsx.xlsx'),
        force=True
    )
    assert os.path.exists(path_to_file) is True


def test_to_pdf_no_extension_extension_forced():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_xlsx_no_extension'),
        force=True,
        file_ext=".xlsx"
    )
    assert os.path.exists(path_to_file) is True


def test_to_pdf_no_extension():
    with pytest.raises(UnavailablePreviewType):
        manager = PreviewManager(
            cache_folder_path=CACHE_DIR, create_folder=True
        )
        manager.get_pdf_preview(
            file_path=os.path.join(CURRENT_DIR, 'the_xlsx_no_extension'),
        )
