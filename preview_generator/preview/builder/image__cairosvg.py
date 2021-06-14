# -*- coding: utf-8 -*-

import tempfile
import typing

# HACK - G.M - 2020-12-26 - Hack to allow loading modules without cairosvg installed
from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims

cairosvg_installed = True
try:
    import cairosvg
except ImportError:
    cairosvg_installed = False


class ImagePreviewBuilderCairoSVG(ImagePreviewBuilder):
    """
    Build preview for SVG files using cairosvg and PIL libs
    """

    @classmethod
    def get_label(cls) -> str:
        return "Vector images - based on Cairo"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["image/svg+xml", "image/svg"]

    @classmethod
    def check_dependencies(cls) -> None:
        if not cairosvg_installed:
            raise BuilderDependencyNotFound("this builder requires cairosvg to be available")

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

        with tempfile.NamedTemporaryFile(
            "w+b", prefix="preview-generator", suffix="png"
        ) as tmp_png:
            cairosvg.svg2png(url=file_path, write_to=tmp_png.name, dpi=96)

            return ImagePreviewBuilderPillow().build_jpeg_preview(
                tmp_png.name, preview_name, cache_path, page_id, extension, size, mimetype
            )

    def build_pdf_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        extension: str = ".pdf",
        page_id: int = -1,
        mimetype: str = "",
    ) -> None:
        """
        generate pdf preview. No default implementation
        """
        preview_file_path = "{path}{extension}".format(
            path=cache_path + preview_name, extension=extension
        )
        cairosvg.svg2pdf(url=file_path, write_to=preview_file_path)

    def has_pdf_preview(self) -> bool:
        return True
