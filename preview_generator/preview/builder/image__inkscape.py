# -*- coding: utf-8 -*-
from shutil import which
from subprocess import CalledProcessError
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call
from subprocess import check_output
import tempfile
import typing

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import IntermediateFileBuildingFailed
from preview_generator.preview.builder.image__wand import ImagePreviewBuilderWand  # nopep8
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import executable_is_available

INKSCAPE_EXECUTABLE = "inkscape"

INKSCAPE_0x_SVG_TO_PNG_OPTIONS = ("--export-area-drawing", "-e")
INKSCAPE_100_SVG_TO_PNG_OPTIONS = ("--export-area-drawing", "--export-type=png", "-o")

try:
    inkscape_version = check_output((INKSCAPE_EXECUTABLE, "--version"))
except (FileNotFoundError, CalledProcessError):
    inkscape_version = b"not_installed"
INKSCAPE_SVG_TO_PNG_OPTIONS = (
    INKSCAPE_0x_SVG_TO_PNG_OPTIONS
    if inkscape_version.startswith(b"Inkscape 0.")
    else INKSCAPE_100_SVG_TO_PNG_OPTIONS
)


def get_inkscape_parameters(input_path: str, output_path: str) -> typing.Tuple[str, ...]:
    return (INKSCAPE_EXECUTABLE, input_path, *INKSCAPE_SVG_TO_PNG_OPTIONS, output_path)


class ImagePreviewBuilderInkscape(ImagePreviewBuilder):
    weight = 70

    @classmethod
    def get_label(cls) -> str:
        return "Vector images - based on Inkscape"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["image/svg+xml", "image/svg"]

    @classmethod
    def check_dependencies(cls) -> None:
        if not executable_is_available(INKSCAPE_EXECUTABLE):
            raise BuilderDependencyNotFound("this builder requires inkscape to be available")

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        return "{} from {}".format(inkscape_version.decode(), which(INKSCAPE_EXECUTABLE))

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
                get_inkscape_parameters(file_path, tmp_png.name),
                stdout=DEVNULL,
                stderr=STDOUT,
            )

            if build_png_result_code != 0:
                raise IntermediateFileBuildingFailed(
                    "Building PNG intermediate file using inkscape "
                    "failed with status {}".format(build_png_result_code)
                )

            return ImagePreviewBuilderWand().build_jpeg_preview(
                tmp_png.name, preview_name, cache_path, page_id, extension, size, mimetype
            )
