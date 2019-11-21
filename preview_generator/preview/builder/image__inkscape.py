# -*- coding: utf-8 -*-


from shutil import which
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call
from subprocess import check_output
import tempfile
import typing

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import IntermediateFileBuildingFailed
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import executable_is_available


class ImagePreviewBuilderInkscape(ImagePreviewBuilder):
    @classmethod
    def get_label(cls) -> str:
        return "Vector images - based on Inkscape"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["image/svg+xml", "image/svg"]

    @classmethod
    def check_dependencies(cls) -> None:
        if not executable_is_available("inkscape"):
            raise BuilderDependencyNotFound("this builder requires inkscape to be available")

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        return "{} from {}".format(
            check_output(["inkscape", "--version"], universal_newlines=True).strip(),
            which("inkscape"),
        )

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
        # inkscape tesselation-P3.svg  -e
        with tempfile.NamedTemporaryFile(
            "w+b", prefix="preview-generator-", suffix=".png"
        ) as tmp_png:
            build_png_result_code = check_call(
                ["inkscape", file_path, "--export-area-drawing", "-e", tmp_png.name],
                stdout=DEVNULL,
                stderr=STDOUT,
            )

            if build_png_result_code != 0:
                raise IntermediateFileBuildingFailed(
                    "Building PNG intermediate file using inkscape "
                    "failed with status {}".format(build_png_result_code)
                )

            return ImagePreviewBuilderPillow().build_jpeg_preview(
                tmp_png.name, preview_name, cache_path, page_id, extension, size, mimetype
            )
