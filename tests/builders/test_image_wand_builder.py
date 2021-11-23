import os

from PIL import Image

from preview_generator.preview.builder.image__wand import ImagePreviewBuilderWand
from preview_generator.utils import ImgDims

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = "/tmp/preview-generator-tests/cache"


def test_build_jpeg_preview() -> None:
    wand_builder = ImagePreviewBuilderWand()
    test_orient_path = os.path.join(CURRENT_DIR, "the_img.png")
    extension = ".jpg"
    preview_name = "preview_the_img"
    width = 512
    height = 256
    size = ImgDims(width=width, height=height)
    wand_builder.build_jpeg_preview(
        file_path=test_orient_path,
        preview_name=preview_name,
        cache_path=CACHE_DIR,
        page_id=-1,
        size=size,
        extension=extension,
    )
    preview_name = preview_name + extension
    dest_path = os.path.join(CACHE_DIR, preview_name)
    assert os.path.exists(dest_path)
    assert os.path.getsize(dest_path) > 0
    with Image.open(dest_path) as jpg:
        assert jpg.height == height
        assert jpg.width in range(288, 290)
