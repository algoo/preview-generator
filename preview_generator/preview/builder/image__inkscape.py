# -*- coding: utf-8 -*-


import os
from subprocess import check_call
from subprocess import DEVNULL
from subprocess import STDOUT
import tempfile
import typing
import uuid

from preview_generator.exception import PreviewGeneratorException
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import OnePagePreviewBuilder
from preview_generator.utils import check_executable_is_available
from preview_generator.utils import ImgDims


class ImagePreviewBuilderInkscape(OnePagePreviewBuilder):
    @classmethod
    def get_label(cls) -> str:
        return 'Vector images - based on Inkscape'

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ['image/svg+xml']

    @classmethod
    def check_dependencies(cls) -> bool:
        return check_executable_is_available('inkscape')

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = '.jpg',
        size: ImgDims=None,
        mimetype: str = ''
    ) -> None:
        # inkscape tesselation-P3.svg  -e
        tempfolder = tempfile.tempdir
        tmp_filename = '{}.png'.format(str(uuid.uuid4()))
        tmp_filepath = os.path.join(tempfolder, tmp_filename)
        build_png_result_code = check_call(
            [
                'inkscape',
                file_path,
                '--export-area-drawing',
                '-e',
                tmp_filepath
            ],
            stdout=DEVNULL, stderr=STDOUT
        )

        if build_png_result_code != 0:
            raise PreviewGeneratorException(
                'Building PNG intermediate file using inkscape '
                'failed with status {}'.format(build_png_result_code)
            )

        return ImagePreviewBuilderPillow().build_jpeg_preview(
            tmp_filepath,
            preview_name,
            cache_path,
            page_id,
            extension,
            size,
            mimetype
        )

