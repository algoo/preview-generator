# -*- coding: utf-8 -*-

from io import BytesIO

import logging
import os
import typing

from preview_generator import file_converter
from preview_generator.exception import UnavailablePreviewType
from preview_generator.utils import ImgDims


class PreviewBuilderMeta(type):
    def __new__(
            mcs,
            *args: str,
            **kwargs: int
    ) -> typing.Type['PreviewBuilder']:
        cls = super().__new__(mcs, *args, **kwargs)
        cls = typing.cast(typing.Type['PreviewBuilder'], cls)
        return cls


class PreviewBuilder(object, metaclass=PreviewBuilderMeta):
    def __init__(
            self,
    ) -> None:
        logging.info('New Preview builder of class' + str(self.__class__))

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        raise NotImplementedError()

    @classmethod
    def check_dependencies(cls) -> bool:
        return True

    def get_page_number(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str
    ) -> int:
        """
        Get the number of page of the document
        """
        raise UnavailablePreviewType()

    def build_jpeg_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int,
            extension: str = '.jpg',
            size: ImgDims=None
    ) -> None:
        """
        generate the jpg preview
        """
        raise UnavailablePreviewType()

    def has_pdf_preview(self) -> bool:
        """
        Override and return True if your builder allow PDF preview
        :return:
        """
        return False

    def build_pdf_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            extension: str = '.pdf',
            page_id: int = -1
    ) -> None:
        """
        generate the jpeg preview
        """
        raise UnavailablePreviewType()

    def build_html_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            extension: str = '.html'
    ) -> None:
        """
        generate the html preview
        """
        raise UnavailablePreviewType()

    def build_json_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int = 0,
            extension: str = '.json'
    ) -> None:
        """
        generate the json preview
        """
        raise UnavailablePreviewType()

    def build_text_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int = 0,
            extension: str = '.txt'
    ) -> None:
        """
        return file content from the cache
        """
        raise UnavailablePreviewType()


class OnePagePreviewBuilder(PreviewBuilder):
    """
    Generic preview handler for single page document
    """

    def get_page_number(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str
    ) -> int:
        return 1


class ImagePreviewBuilder(OnePagePreviewBuilder):
    """
    Generic preview handler for an Image (except multi-pages images)
    """

    def _get_json_stream_from_image_stream(
        self,
            img: typing.IO[bytes],
            filesize: int=0
    ) -> BytesIO:
        return file_converter.image_to_json(img, filesize)

    def build_json_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int = 0,
            extension: str = '.json'
    ) -> None:
        """
        generate the json preview
        """

        with open(file_path, 'rb') as img:
            filesize = os.path.getsize(file_path)
            json_stream = self._get_json_stream_from_image_stream(img, filesize)
            with open(cache_path + preview_name + extension, 'wb') as jsonfile:
                buffer = json_stream.read(256)
                while buffer:
                    jsonfile.write(buffer)
                    buffer = json_stream.read(256)
