# -*- coding: utf-8 -*-

import os

from preview_generator.preview.builder.image__wand import ImagePreviewBuilderWand
from preview_generator.utils import ImgDims
from preview_generator.utils import CropDims
from preview_generator.utils import compute_resize_dims


def test_imgdims():
    dims = ImgDims(123,456)
    assert dims.width == 123
    assert dims.height == 456


def test_cropdims():
    dims = CropDims(12,34,56,78)
    assert dims.left == 12
    assert dims.top == 34
    assert dims.right == 56
    assert dims.bottom == 78


def test_compute_resize_dims_same_ratio():
    dims_in = ImgDims(100, 50)
    dims_out = ImgDims(200, 100)

    builder = ImagePreviewBuilderWand()
    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 200
    assert dims_resize.height == 100


def test_compute_resize_dims_same_format():
    dims_in = ImgDims(100, 50)
    dims_out = ImgDims(90, 30)

    builder = ImagePreviewBuilderWand()
    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 60
    assert dims_resize.height == 30


def test_compute_resize_dims_different_ratio():
    dims_in = ImgDims(100, 50)  # horizontal
    dims_out = ImgDims(200, 400)  # vertical

    builder = ImagePreviewBuilderWand()
    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 200
    assert dims_resize.height == 100


def test_compute_resize_dims_different_ratio_inverted():
    dims_in = ImgDims(198, 600)  # vertical
    dims_out = ImgDims(400, 100)  # horizontal

    builder = ImagePreviewBuilderWand()
    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 33
    assert dims_resize.height == 100


def test_compute_resize_dims_right_limits():
    dims_in = ImgDims(520, 206)  # vertical
    dims_out = ImgDims(512, 256)  # horizontal

    builder = ImagePreviewBuilderWand()
    dims_resize = compute_resize_dims(dims_in, dims_out)
    assert dims_resize.width == 512
    assert dims_resize.height == 203

def test_check_dependencies():
    from preview_generator.preview.builder.office__libreoffice import OfficePreviewBuilderLibreoffice
    OfficePreviewBuilderLibreoffice.check_dependencies()
