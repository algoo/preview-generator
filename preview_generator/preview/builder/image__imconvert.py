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
import wand
import mimetypes


class ImagePreviewBuilderIMConvert(OnePagePreviewBuilder):

    MIMETYPES = []  # type: typing.List[str]

    """ IM means Image Magick"""
    @classmethod
    def get_label(cls) -> str:
        return 'Images - based on convert command (Image magick)'

    @classmethod
    def __load_mimetypes(cls) -> typing.List[str]:
        """
        Load supported mimetypes from WAND library
        :return: list of supported mime types
        """

        all_supported = wand.version.formats("*")
        mimes = []  # type: typing.List[str]
        for supported in all_supported:
            url = "./FILE.{0}".format(supported)  # Fake a url
            mime, enc = mimetypes.guess_type(url)
            if mime and mime not in mimes:
                if 'video' not in mime:
                    # TODO - D.A. - 2018-09-24 - Do not skip video if supported
                    mimes.append(mime)
        mimes.remove('image/svg+xml')
        return mimes

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        """
        :return: list of supported mime types
        """
        if len(ImagePreviewBuilderIMConvert.MIMETYPES) == 0:
            ImagePreviewBuilderIMConvert.MIMETYPES = cls.__load_mimetypes()
        return ImagePreviewBuilderIMConvert.MIMETYPES

    @classmethod
    def check_dependencies(cls) -> bool:
        return check_executable_is_available('convert')

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
                'convert',
                file_path,
                '-layers',
                'merge',
                tmp_filepath
            ],
            stdout=DEVNULL, stderr=STDOUT
        )

        if build_png_result_code != 0:
            raise PreviewGeneratorException(
                'Building PNG intermediate file using convert '
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
