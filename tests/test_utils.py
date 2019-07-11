# -*- coding: utf-8 -*-

from preview_generator.utils import CropDims
from preview_generator.utils import ImgDims
from preview_generator.utils import compute_resize_dims


def test_imgdims() -> None:
    dims = ImgDims(123, 456)
    assert dims.width == 123
    assert dims.height == 456


def test_cropdims() -> None:
    dims = CropDims(12, 34, 56, 78)
    assert dims.left == 12
    assert dims.top == 34
    assert dims.right == 56
    assert dims.bottom == 78


def test_compute_resize_dims_same_ratio() -> None:
    dims_in = ImgDims(100, 50)
    dims_out = ImgDims(200, 100)

    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 200
    assert dims_resize.height == 100


def test_compute_resize_dims_same_format() -> None:
    dims_in = ImgDims(100, 50)
    dims_out = ImgDims(90, 30)

    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 60
    assert dims_resize.height == 30


def test_compute_resize_dims_different_ratio() -> None:
    dims_in = ImgDims(100, 50)  # horizontal
    dims_out = ImgDims(200, 400)  # vertical

    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 200
    assert dims_resize.height == 100


def test_compute_resize_dims_different_ratio_inverted() -> None:
    dims_in = ImgDims(198, 600)  # vertical
    dims_out = ImgDims(400, 100)  # horizontal

    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 33
    assert dims_resize.height == 100


def test_compute_resize_dims_right_limits() -> None:
    dims_in = ImgDims(520, 206)  # vertical
    dims_out = ImgDims(512, 256)  # horizontal

    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 512
    assert dims_resize.height == 203


def test_check_dependencies() -> None:
    from preview_generator.preview.builder.office__libreoffice import (
        OfficePreviewBuilderLibreoffice,
    )

    OfficePreviewBuilderLibreoffice.check_dependencies()


CACHE_FILE_PATH_PATTERN__JPEG = (
    "/tmp/preview-generator-tests/cache/[abcdef0123456789]{32}-[0-9]*x[0-9]*.jpeg"
)
CACHE_FILE_PATH_PATTERN_WITH_PAGE__JPEG = (
    "/tmp/preview-generator-tests/cache/[abcdef0123456789]{32}-[0-9]*x[0-9]*-page[[0-9]*.jpeg"
)

CACHE_FILE_PATH_PATTERN__PDF = "/tmp/preview-generator-tests/cache/[abcdef0123456789]{32}.pdf"
CACHE_FILE_PATH_PATTERN_WITH_PAGE__PDF = (
    "/tmp/preview-generator-tests/cache/[abcdef0123456789]{32}-page[[0-9]*.pdf"
)

CACHE_FILE_PATH_PATTERN__JSON = "/tmp/preview-generator-tests/cache/[abcdef0123456789]{32}.json"
CACHE_FILE_PATH_PATTERN_WITH_PAGE__JSON = (
    "/tmp/preview-generator-tests/cache/[abcdef0123456789]{32}-page[[0-9]*.json"
)
