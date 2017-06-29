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
    PreviewManager(path=CACHE_DIR, create_folder=False)
    assert not os.path.exists(CACHE_DIR)


def test_cache_dir_is_created():
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    PreviewManager(path=CACHE_DIR, create_folder=True)
    assert os.path.exists(CACHE_DIR)
