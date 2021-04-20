# -*- coding: utf-8 -*-

import json
import logging
import typing

import pyexifinfo

from preview_generator.exception import UnavailablePreviewType
from preview_generator.extension import mimetypes_storage
from preview_generator.utils import ImgDims
from preview_generator.utils import LOGGER_NAME
from preview_generator.utils import MimetypeMapping


class PreviewBuilder(object):
    default_size = ImgDims(256, 256)

    def __init__(self) -> None:
        self.logger = logging.getLogger(LOGGER_NAME)
        self.logger.info("New Preview builder of class" + str(self.__class__))

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        raise NotImplementedError()

    @classmethod
    def get_label(cls) -> str:
        return cls.__name__  # default label is the class name

    @classmethod
    def check_dependencies(cls) -> None:
        """Raises a BuilderDependencyNotFound with an appropriate message
        if a dependency is missing.
        """

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        """
        Get specific mimetypes mappings (mimetype/file_extension) related to
        builder, this allow to update mimetypes mapping use by preview_generator
        to help preview_generator to determine more correctly type or file_extension
        :return:
        """
        return []

    @classmethod
    def update_mimetypes_mapping(cls) -> None:
        """
        Update mimetypes mapping with file extension in preview_generator
        mimetypes_storage
        """
        for mimetypes_mapping in cls.get_mimetypes_mapping():
            # INFO - G.M - 2019-11-22 - mimetype are added as strict to force override of default
            # system/mimetype lib value, which is needed for type like .obj where system type can be
            # "text/plain" or "application/octet-stream"
            mimetypes_storage.add_type(  # type: ignore
                type=mimetypes_mapping.mimetype, ext=mimetypes_mapping.file_extension, strict=True
            )

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        """Tell about the version of dependencies. Returns None if there is
        this builder has no dependencies.
        """
        return None

    def get_page_number(
        self, file_path: str, preview_name: str, cache_path: str, mimetype: str = ""
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
        extension: str = ".jpg",
        size: ImgDims = None,
        mimetype: str = "",
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

    def has_jpeg_preview(self) -> bool:
        """
        Override and return True if your builder allow jpeg preview
        """
        return False

    def has_json_preview(self) -> bool:
        """
        Override and return True if your builder allow json preview
        """
        return True

    def has_text_preview(self) -> bool:
        """
        Override and return True if your builder allow text preview
        """
        return False

    def has_html_preview(self) -> bool:
        """
        Override and return True if your builder allow html preview
        """
        return False

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
        raise UnavailablePreviewType(
            "No builder registered for PDF preview of {}".format(file_path)
        )

    def build_html_preview(
        self, file_path: str, preview_name: str, cache_path: str, extension: str = ".html"
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
        extension: str = ".json",
    ) -> None:
        """
        generate the json preview. Default implementation is based on ExifTool
        """
        metadata = pyexifinfo.get_json(file_path)[0]

        with open(cache_path + preview_name + extension, "w") as jsonfile:
            json.dump(metadata, jsonfile)

    def build_text_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int = 0,
        extension: str = ".txt",
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


class ImagePreviewBuilder(OnePagePreviewBuilder):
    """
    Generic preview handler for image preview_builder
    """

    def has_jpeg_preview(self) -> bool:
        return True
