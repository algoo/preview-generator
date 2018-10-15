# -*- coding: utf-8 -*-

import os
import shutil

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_text_to_jpeg():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_text.txt'),
        force=True
    )
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0


def test_to_pdf():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_text.txt'),
        force=True
    )
    assert os.path.exists(path_to_file) is True


def test_page_number():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    page_number = manager.get_page_nb(
        file_path=os.path.join(CURRENT_DIR, 'the_text.txt'),
    )
    assert page_number == 1


def test_to_pdf_no_extension():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_text_no_extension'),
        force=True
    )
    assert os.path.exists(path_to_file) is True


def test_to_pdf_no_extension_extension_forced():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_pdf_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_text_no_extension'),
        force=True,
        file_ext=".txt"
    )
    assert os.path.exists(path_to_file) is True


def test_to_jpeg_no_extension():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_text_no_extension'),
        force=True
    )
    assert os.path.exists(path_to_file) is True


def test_to_jpeg_no_extension_extension_forced():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_text_no_extension'),
        force=True,
        file_ext=".txt"
    )
    assert os.path.exists(path_to_file) is True


def test_page_number__no_extension():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    page_number = manager.get_page_nb(
        file_path=os.path.join(CURRENT_DIR, 'the_text_no_extension'),
    )
    assert page_number == 1


def test_page_number__extension_forced():
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    page_number = manager.get_page_nb(
        file_path=os.path.join(CURRENT_DIR, 'the_text_no_extension'),
        file_ext=".txt"
    )
    assert page_number == 1
