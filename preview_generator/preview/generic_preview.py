# -*- coding: utf-8 -*-

from io import BytesIO

import json
import logging
import typing

import pyexifinfo

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
    def get_label(cls) -> str:
        return cls.__name__  # default label is the class name

    @classmethod
    def check_dependencies(cls) -> bool:
        return True

    def get_page_number(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            mimetype: typing.Optional[str] = None,
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
            size: ImgDims=None,
            mimetype: str = ''
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
            page_id: int = -1,
            mimetype: str = ''
    ) -> None:
        """
        generate pdf preview. No default implementation
        """
        raise UnavailablePreviewType(
            'No builder registered for PDF preview of {}'.format(file_path)
        )

    def build_html_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            extension: str = '.html'
    ) -> None:
        """
        generate the html preview. No default implementation
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
        generate the json preview. Default implementation is based on ExifTool
        """
        metadata = pyexifinfo.get_json(file_path)[0]

        with open(cache_path + preview_name + extension, 'w') as jsonfile:
            json.dump(metadata, jsonfile)

    def build_text_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int = 0,
            extension: str = '.txt'
    ) -> None:
        """
        generate the text preview. No default implementation
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
        cache_path: str,
        mimetype: typing.Optional[str] = None,
    ) -> int:
        return 1
