# -*- coding: utf-8 -*-

import os
import shutil

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_cache_dir_not_created():
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    PreviewManager(cache_folder_path=CACHE_DIR, create_folder=False)
    assert not os.path.exists(CACHE_DIR)


def test_cache_dir_is_created():
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    assert os.path.exists(CACHE_DIR)


def test_get_file_hash():
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    from preview_generator.utils import ImgDims
    hash = pm._get_file_hash('/tmp/image.jpeg')
    assert hash == '7f8df7223d8be60a7ac8a9bf7bd1df2a'


def test_get_file_hash_with_size():
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    from preview_generator.utils import ImgDims
    hash = pm._get_file_hash(
        '/tmp/image.jpeg',
        ImgDims(width=512, height=256)
    )
    assert hash == '7f8df7223d8be60a7ac8a9bf7bd1df2a-512x256'


def test_get_file_hash_with_size_and_page():
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    from preview_generator.utils import ImgDims
    hash = pm._get_file_hash(
        '/tmp/image.jpeg',
        ImgDims(width=512, height=256),
        page=3
    )
    assert hash == '7f8df7223d8be60a7ac8a9bf7bd1df2a-512x256-page3'


def test_get_file_hash_with_page():
    pm = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    from preview_generator.utils import ImgDims
    hash = pm._get_file_hash(
        '/tmp/image.jpeg',
        page=3
    )
    assert hash == '7f8df7223d8be60a7ac8a9bf7bd1df2a-page3'

