# -*- coding: utf-8 -*-

from io import BytesIO
import os
from pathlib import Path
import time
import typing
import tempfile

from preview_generator.utils import ImgDims
from preview_generator.preview.generic_preview import ImagePreviewBuilder

import cairosvg
import PIL


class ImagePreviewBuilderCairoSVG(ImagePreviewBuilder):
    """
    Build preview for SVG files using cairosvg and PIL libs 
    """

    @classmethod
    def get_label(cls) -> str:  
        return "Vector images - based on Cairo"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["image/svg+xml"]

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = ".jpg",
        size: ImgDims = None,
        mimetype: str = "",
    ) -> None:

        if not size:
            size = self.default_size

        with tempfile.NamedTemporaryFile('w+b', prefix="preview-generator", suffix="png") as tmp_png:
            cairosvg.svg2png(url=file_path, write_to=tmp_png.name, dpi=96)
            png_img = (PIL.Image
                .open(tmp_png.name)
                .resize((size.width, size.height))
                .convert("RGB")
                .save(preview_name + extension, "JPEG")
            )
