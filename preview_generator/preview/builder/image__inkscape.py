# -*- coding: utf-8 -*-


import os
from shutil import which
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call
from subprocess import check_output
import tempfile
import typing
import uuid

from preview_generator.exception import IntermediateFileBuildingFailed
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import check_executable_is_available


class ImagePreviewBuilderInkscape(ImagePreviewBuilder):
    @classmethod
    def get_label(cls) -> str:
        return "Vector images - based on Inkscape"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["image/svg+xml"]

    @classmethod
    def check_dependencies(cls) -> bool:
        return check_executable_is_available("inkscape")

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
        tmp_filename = "{}.png".format(str(uuid.uuid4()))
        if tempfile.tempdir:
            tmp_filepath = os.path.join(tempfile.tempdir, tmp_filename)
        else:
            tmp_filepath = tmp_filename
        build_png_result_code = check_call(
            ["inkscape", file_path, "--export-area-drawing", "-e", tmp_filepath],
            stdout=DEVNULL,
            stderr=STDOUT,
        )

        if build_png_result_code != 0:
            raise IntermediateFileBuildingFailed(
                "Building PNG intermediate file using inkscape "
                "failed with status {}".format(build_png_result_code)
            )

        return ImagePreviewBuilderPillow().build_jpeg_preview(
            tmp_filepath, preview_name, cache_path, page_id, extension, size, mimetype
        )
