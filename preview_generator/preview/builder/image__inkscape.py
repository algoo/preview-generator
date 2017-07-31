# -*- coding: utf-8 -*-

from io import BytesIO
import json
import logging
import os
from subprocess import check_call
from subprocess import DEVNULL
from subprocess import STDOUT
import time
import typing

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from preview_generator.exception import PreviewGeneratorException
from preview_generator.utils import PreviewGeneratorJsonEncoder

from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.preview.builder.image__wand import convert_pdf_to_jpeg
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import check_executable_is_available
from preview_generator.utils import ImgDims

class ImagePreviewBuilderInkscape(ImagePreviewBuilder):
    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [ 'image/svg+xml' ]

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
            size: ImgDims=None
    ) -> None:
        # inkscape tesselation-P3.svg  -e

        import tempfile
        import uuid

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
            size
        )

    def _get_json_stream_from_image_stream(
        self,
            img: typing.IO[bytes],
            filesize: int=0
    ) -> BytesIO:
        output = BytesIO()
        if not filesize:
            filesize = len(img.read())

        info = {
            'width': None,
            'height': None,
            'size': filesize,
        }

        content = json.dumps(info, cls=PreviewGeneratorJsonEncoder)
        output.write(content.encode())
        output.seek(0, 0)
        return output
