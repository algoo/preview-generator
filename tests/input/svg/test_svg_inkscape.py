# -*- coding: utf-8 -*-

import json
import os
import shutil
import typing

from PIL import Image
import pytest

from preview_generator.exception import UnavailablePreviewType
from preview_generator.preview.builder.image__inkscape import ImagePreviewBuilderInkscape
from preview_generator.utils import ImgDims

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache/"
TEST_FILES = [
    {
        "name": "tesselation-P3.svg",
        "width": 359,
        "height": 256,
        "width_default": 181,
        "height_default": 256,
    },
    {
        "name": "Ghostscript_Tiger.svg",
        "width": 248,
        "height": 256,
        "width_default": 256,
        "height_default": 256,
    },
    {
        "name": "14224-tiger-svg.svg",
        "width": 484,
        "height": 256,
        "width_default": 256,
        "height_default": 156,
    },
]


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


@pytest.mark.parametrize("file", TEST_FILES)
def test_to_jpeg(file: typing.Dict[str, typing.Any]) -> None:
    os.makedirs(CACHE_DIR)
    builder = ImagePreviewBuilderInkscape()
    assert builder.has_jpeg_preview() is True
    size = ImgDims(height=256, width=512)
    preview_name = "svg_tesselation_test_inkscape"
    builder.build_jpeg_preview(
        file_path=os.path.join(CURRENT_DIR, file["name"]),
        size=size,
        page_id=0,
        cache_path=CACHE_DIR,
        preview_name=preview_name,
    )
    path_to_file = os.path.join(CACHE_DIR, "{}.jpg".format(preview_name))
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height in range(file["height"] - 2, file["height"] + 2)
        assert jpeg.width in range(file["width"] - 2, file["width"] + 2)


@pytest.mark.parametrize("file", TEST_FILES)
def test_get_nb_page(file: typing.Dict[str, typing.Any]) -> None:
    os.makedirs(CACHE_DIR)
    builder = ImagePreviewBuilderInkscape()
    preview_name = "svg_tesselation_test_inkscape"
    nb_page = builder.get_page_number(
        file_path=os.path.join(CURRENT_DIR, file["name"]),
        cache_path=CACHE_DIR,
        preview_name=preview_name,
    )
    assert nb_page == 1


@pytest.mark.parametrize("file", TEST_FILES)
def test_to_json(file: typing.Dict[str, typing.Any]) -> None:
    os.makedirs(CACHE_DIR)
    builder = ImagePreviewBuilderInkscape()
    preview_name = "svg_tesselation_test_inkscape"
    assert builder.has_json_preview() is True
    builder.build_json_preview(
        file_path=os.path.join(CURRENT_DIR, file["name"]),
        cache_path=CACHE_DIR,
        preview_name=preview_name,
    )
    path_to_file = os.path.join(CACHE_DIR, "{}.json".format(preview_name))

    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0

    data = json.load(open(path_to_file))
    assert "File:FileName" in data.keys()
    assert "SVG:Xmlns" in data.keys()
    assert "File:FileTypeExtension" in data.keys()
    assert "SourceFile" in data.keys()
    assert "File:FileInodeChangeDate" in data.keys()
    assert "File:Directory" in data.keys()
    assert "File:FileAccessDate" in data.keys()
    assert "ExifTool:ExifToolVersion" in data.keys()
    assert "File:FileSize" in data.keys()
    assert "File:FilePermissions" in data.keys()
    assert "File:FileModifyDate" in data.keys()
    assert "File:FileType" in data.keys()
    assert "File:MIMEType" in data.keys()


@pytest.mark.parametrize("file", TEST_FILES)
def test_to_pdf(file: typing.Dict[str, typing.Any]) -> None:
    os.makedirs(CACHE_DIR)
    builder = ImagePreviewBuilderInkscape()
    preview_name = "svg_tesselation_test_inkscape"
    assert builder.has_pdf_preview() is False
    with pytest.raises(UnavailablePreviewType):
        builder.build_pdf_preview(
            file_path=os.path.join(CURRENT_DIR, file["name"]),
            cache_path=CACHE_DIR,
            preview_name=preview_name,
        )


@pytest.mark.parametrize("file", TEST_FILES)
def test_to_text(file: typing.Dict[str, typing.Any]) -> None:
    os.makedirs(CACHE_DIR)
    builder = ImagePreviewBuilderInkscape()
    preview_name = "svg_tesselation_test_inkscape"
    assert builder.has_text_preview() is False
    with pytest.raises(UnavailablePreviewType):
        builder.build_text_preview(
            file_path=os.path.join(CURRENT_DIR, file["name"]),
            cache_path=CACHE_DIR,
            preview_name=preview_name,
        )
