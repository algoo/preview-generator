# -*- coding: utf-8 -*-

import os
import shutil
import sys
import typing

from PIL import Image
import pytest

from preview_generator.preview.builder.cad__vtk import ImagePreviewBuilderVtk
from preview_generator.utils import ImgDims

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache/"
# INFO - G.M - 2019-11-05 - 3d object from https://www.thingiverse.com/thing:477
# by bre under public domain
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, "40mmcube.stl")


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


@pytest.mark.xfail(sys.version_info[:2] >= (3, 9), reason="vtk support for python 3.9+ broken")
def test_to_jpeg() -> None:
    os.makedirs(CACHE_DIR)
    builder = ImagePreviewBuilderVtk()
    assert builder.has_jpeg_preview() is True
    size = ImgDims(height=256, width=512)
    preview_name = "stl_cube_test_vtk"
    builder.update_mimetypes_mapping()
    builder.build_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
        size=size,
        page_id=0,
        cache_path=CACHE_DIR,
        preview_name=preview_name,
    )
    path_to_file = os.path.join(CACHE_DIR, "{}.jpg".format(preview_name))
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 512


@pytest.mark.xfail(sys.version_info[:2] >= (3, 9), reason="vtk support for python 3.9+ broken")
def test_get_nb_page() -> None:
    os.makedirs(CACHE_DIR)
    builder = ImagePreviewBuilderVtk()
    preview_name = "stl_cube_test_vtk"
    nb_page = builder.get_page_number(
        file_path=IMAGE_FILE_PATH, cache_path=CACHE_DIR, preview_name=preview_name
    )
    # FIXME must add parameter force=True/False in the API
    assert nb_page == 1
