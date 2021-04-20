# -*- coding: utf-8 -*-

import os
import shutil
import typing

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_cache_dir_not_created() -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    PreviewManager(cache_folder_path=CACHE_DIR, create_folder=False)
    assert not os.path.exists(CACHE_DIR)


def test_cache_dir_is_created() -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert os.path.exists(CACHE_DIR)


def test_get_preview_name() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)

    filehash = pm.get_preview_context("/tmp/image.jpeg", file_ext=".jpeg").hash
    hash = pm._get_preview_name(filehash)
    assert hash == "7f8df7223d8be60a7ac8a9bf7bd1df2a"


def test_get_preview_name_with_size() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    from preview_generator.utils import ImgDims

    filehash = pm.get_preview_context("/tmp/image.jpeg", file_ext=".jpeg").hash
    hash = pm._get_preview_name(filehash, ImgDims(width=512, height=256))
    assert hash == "7f8df7223d8be60a7ac8a9bf7bd1df2a-512x256"


def test_get_preview_name_with_size_and_page() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    from preview_generator.utils import ImgDims

    filehash = pm.get_preview_context("/tmp/image.jpeg", file_ext=".jpeg").hash
    hash = pm._get_preview_name(filehash, ImgDims(width=512, height=256), page=3)
    assert hash == "7f8df7223d8be60a7ac8a9bf7bd1df2a-512x256-page3"


def test_get_preview_name_with_page() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)

    filehash = pm.get_preview_context("/tmp/image.jpeg", file_ext=".jpeg").hash
    hash = pm._get_preview_name(filehash, page=3)
    assert hash == "7f8df7223d8be60a7ac8a9bf7bd1df2a-page3"


def test_dry_run_jpeg() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)

    preview_path = pm.get_jpeg_preview("/tmp/image.jpeg", dry_run=True)
    assert not os.path.exists(preview_path)


def test_dry_run_pdf() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)

    preview_path = pm.get_pdf_preview("/tmp/image.jpeg", dry_run=True)
    assert not os.path.exists(preview_path)


def test_dry_run_text() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)

    preview_path = pm.get_text_preview("/tmp/image.jpeg", dry_run=True)
    assert not os.path.exists(preview_path)


def test_dry_run_html() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)

    preview_path = pm.get_html_preview("/tmp/image.jpeg", dry_run=True)
    assert not os.path.exists(preview_path)


def test_dry_run_json() -> None:
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)

    preview_path = pm.get_json_preview("/tmp/image.jpeg", dry_run=True)
    assert not os.path.exists(preview_path)
