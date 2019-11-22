import os
import shutil
import typing

from PIL import Image
import pytest

from preview_generator.preview.builder.video__ffmpeg import VideoPreviewBuilderFFMPEG
from preview_generator.utils import ImgDims
from preview_generator.utils import executable_is_available

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache/"
# INFO - G.M - 2019-11-05 - video from https://peach.blender.org/trailer-page/
# Big buck bunny trailer under licence cc-by
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, "trailer_400p.ogg")

if not executable_is_available("ffprobe"):
    pytest.skip("ffprobe is not available.", allow_module_level=True)


def setup_function(function: typing.Callable) -> None:
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_to_jpeg() -> None:
    os.makedirs(CACHE_DIR)
    builder = VideoPreviewBuilderFFMPEG()
    assert builder.has_jpeg_preview() is True
    size = ImgDims(height=256, width=512)
    preview_name = "ogg_theora_big_buck_bunny_trailer_test_ffmpeg"
    builder.build_jpeg_preview(
        file_path=IMAGE_FILE_PATH,
        size=size,
        page_id=7,
        cache_path=CACHE_DIR,
        preview_name=preview_name,
    )
    path_to_file = os.path.join(CACHE_DIR, "{}.jpg".format(preview_name))
    assert os.path.exists(path_to_file) is True
    assert os.path.getsize(path_to_file) > 0

    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 461


def test_get_nb_page() -> None:
    os.makedirs(CACHE_DIR)
    builder = VideoPreviewBuilderFFMPEG()
    preview_name = "ogg_theora_big_buck_bunny_trailer_test_ffmpeg"
    nb_page = builder.get_page_number(
        file_path=IMAGE_FILE_PATH, cache_path=CACHE_DIR, preview_name=preview_name
    )
    assert nb_page == 10
