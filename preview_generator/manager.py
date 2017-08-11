# -*- coding: utf-8 -*-

import hashlib
import logging
import os
import typing

from preview_generator.preview.builder.office__libreoffice import OfficePreviewBuilderLibreoffice  # nopep8
from preview_generator.preview.builder_factory import PreviewBuilderFactory
from preview_generator.utils import ImgDims


class PreviewManager(object):

    def __init__(
            self,
            cache_folder_path: str,
            create_folder: bool=False
    ) -> None:
        """
        :param cache_folder_path: path to the cache folder.
        This is where previews will be stored
        :param create_folder: if True, then create the cache folder
        if it does not exist
        """

        cache_folder_path = os.path.join(cache_folder_path, '')  # add trailing slash
        # nopep8 see https://stackoverflow.com/questions/2736144/python-add-trailing-slash-to-directory-string-os-independently

        self.cache_path = cache_folder_path  # type: str
        self._factory = PreviewBuilderFactory.get_instance()  # nopep8 keep link to singleton instance as it will be often used

        if create_folder and not os.path.isdir(self.cache_path):
            try:
                os.makedirs(self.cache_path)
            except OSError as e:
                logging.error(
                    'cant create cache folder [{}]'.format(self.cache_path)
                )

    def get_mimetype(self, file_path: str) -> str:
        """
        Return detected mimetype of the file
        :param file_path: path of the file
        :return: mimetype of the file
        """
        return PreviewBuilderFactory().get_file_mimetype(file_path)

    def has_pdf_preview(self, file_path: str) -> bool:
        """
        return True if the given file offers PDF preview
        Actually, this is the case for office
        :param file_path:
        :return:
        """
        mimetype = self._factory.get_file_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        return builder.has_pdf_preview()

    def get_page_nb(self, file_path: str) -> int:
        """
        Return the page number of the given file.
        :param file_path: path of the file
        :return: number of pages. Default is 1 (eg for a JPEG)
        """
        mimetype = self._factory.get_file_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)

        preview_name = self._get_file_hash(file_path)
        page_nb = builder.get_page_number(
            file_path,
            preview_name,
            self.cache_path
        )
        return page_nb

    def get_jpeg_preview(
            self,
            file_path: str,
            page: int = -1,
            width: int = None,
            height: int = 256,
            force: bool = False,
    ) -> str:
        """
        Return a JPEG preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param page: page of the original document, if it makes sense
        :param width: width of the requested preview image
        :param height: height of the requested preview image
        :param force: if True, do not use cached preview.
        :return: path to the generated preview file
        """
        if width is None:
            width = height

        size = ImgDims(width=width, height=height)
        mimetype = self._factory.get_file_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.jpeg'

        if isinstance(builder, OfficePreviewBuilderLibreoffice):
            file_path = self.get_pdf_preview(
                file_path=file_path,
                force=force,
            )

        preview_name = self._get_file_hash(file_path, size, page)
        mimetype = self._factory.get_file_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)

        preview_file_path = os.path.join(self.cache_path, preview_name + extension)  # nopep8
        page = max(page, 0)  # if page is -1 then return preview of first page
        if force or not os.path.exists(preview_file_path):
            builder.build_jpeg_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=self.cache_path,
                page_id=page,
                extension=extension,
                size=size
            )

        return preview_file_path

    def get_pdf_preview(
            self,
            file_path: str,
            page: int = -1,
            force: bool = False,
    ) -> str:
        """
        Return a PDF preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param page: page of the original document. -1 means "all pages"
        :param force: if True, do not use cached preview.
        :return: path to the generated preview file
        """
        mimetype = self._factory.get_file_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.pdf'
        preview_name = self._get_file_hash(
            file_path=file_path,
            page=page,
        )

        try:
            cache_file_path = self.cache_path + preview_name + extension
            if force or not os.path.exists(cache_file_path):
                builder.build_pdf_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension,
                    page_id=page
                )

            return cache_file_path

        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_text_preview(
            self,
            file_path: str,
            force: bool = False,
    ) -> str:
        """
        Return a TXT preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param force: if True, do not use cached preview.
        :return: path to the generated preview file
        """
        mimetype = self._factory.get_file_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.txt'
        preview_name = self._get_file_hash(
            file_path=file_path
        )
        try:
            cache_file_path = self.cache_path + preview_name + extension
            if force or not os.path.exists(cache_file_path):
                builder.build_text_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return cache_file_path

        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_html_preview(
            self,
            file_path: str,
            force: bool = False,
    ) -> str:
        """
        Return a HTML preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param force: if True, do not use cached preview.
        :return: path to the generated preview file
        """
        mimetype = self._factory.get_file_mimetype(file_path)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.html'
        preview_name = self._get_file_hash(
            file_path,
        )
        try:
            cache_file_path = self.cache_path + preview_name + extension
            if force or not os.path.exists(cache_file_path):
                builder.build_html_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return cache_file_path

        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_json_preview(
            self,
            file_path: str,
            force: bool = False,
    ) -> str:
        """
        Return a HTML preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param force: if True, do not use cached preview.
        :return: path to the generated preview file
        """
        mimetype = self._factory.get_file_mimetype(file_path)
        logging.info('Mimetype of the document is :' + mimetype)
        builder = self._factory.get_preview_builder(mimetype)
        extension = '.json'

        preview_name = self._get_file_hash(file_path=file_path)
        try:
            cache_file_path = self.cache_path + preview_name + extension
            if force or not os.path.exists(cache_file_path):  # nopep8
                builder.build_json_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return cache_file_path
        except AttributeError:
            raise Exception('Error while getting the file preview')

    def _get_file_hash(
            self,
            file_path: str,
            size: ImgDims=None,
            page: int = None
    ) -> str:
        """
        Build a hash based on the given parameters.
        This hash will be used as key for caching generated previews.

        The hash is something like this:
            720f89890597ec1eb45e7b775898e806-320x139-page32

        :param file_path: the path of the original file
        :param size: requested size (width and height)
        :param page: requested page
        :return:
        """
        hash_str = hashlib.md5(file_path.encode('utf-8')).hexdigest()

        page_str = ''
        if page is not None and page > -1:
            page_str = '-page{page}'.format(page=page)

        size_str = ''
        if size:
            size_str = '-{width}x{height}'.format(
                width=size.width,
                height=size.height
            )

        return '{hash}{size}{page}'.format(
            hash=hash_str,
            size=size_str,
            page=page_str
        )
