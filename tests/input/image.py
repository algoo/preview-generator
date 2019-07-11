# -*- coding: utf-8 -*-

import os
import shutil
import typing

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_json() -> None:
    manager = PreviewManager(cache_folder_path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_json_preview(file_path=os.path.join(CURRENT_DIR, "the_jpeg.jpeg"))
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0
