# -*- coding: utf-8 -*-

import hashlib
import logging
import os
import typing

from filelock import FileLock

from preview_generator.extension import mimetypes_storage
from preview_generator.preview.builder.document_generic import DocumentPreviewBuilder
from preview_generator.preview.builder_factory import PreviewBuilderFactory
from preview_generator.utils import ImgDims
from preview_generator.utils import LOCKFILE_EXTENSION
from preview_generator.utils import LOCK_DEFAULT_TIMEOUT
from preview_generator.utils import LOGGER_NAME


class PreviewContext(object):
    def __init__(
        self,
        preview_builder_factory: PreviewBuilderFactory,
        cache_path: str,
        file_path: str,
        file_ext: str,
    ):
        self.mimetype = preview_builder_factory.get_file_mimetype(file_path, file_ext)
        self.builder = preview_builder_factory.get_preview_builder(self.mimetype)
        self.hash = hashlib.md5(file_path.encode("utf-8")).hexdigest()
        file_lock_path = os.path.join(cache_path, self.hash + LOCKFILE_EXTENSION)
        self.filelock = FileLock(file_lock_path, timeout=LOCK_DEFAULT_TIMEOUT)


class PreviewManager(object):
    def __init__(self, cache_folder_path: str, create_folder: bool = False) -> None:
        """
        :param cache_folder_path: path to the cache folder.
        This is where previews will be stored
        :param create_folder: if True, then create the cache folder
        if it does not exist
        """
        self.logger = logging.getLogger(LOGGER_NAME)
        cache_folder_path = os.path.join(cache_folder_path, "")  # add trailing slash
        # nopep8 see https://stackoverflow.com/questions/2736144/python-add-trailing-slash-to-directory-string-os-independently

        self.cache_path = cache_folder_path  # type: str
        self._factory = (
            PreviewBuilderFactory.get_instance()
        )  # nopep8 keep link to singleton instance as it will be often used

        if create_folder and not os.path.isdir(self.cache_path):
            try:
                os.makedirs(self.cache_path)
            except OSError:
                self.logger.error("cant create cache folder [{}]".format(self.cache_path))

    def get_preview_context(self, file_path: str, file_ext: str) -> PreviewContext:
        return PreviewContext(self._factory, self.cache_path, file_path, file_ext)

    def get_mimetype(self, file_path: str, file_ext: str = "") -> str:
        """
        Return detected mimetype of the file
        :param file_path: path of the file
        :param file_ext: extension associated to the file. Eg 'jpg'. May be empty -
                it's usefull if the extension can't be found in file_path
        :return: mimetype of the file
        """
        return (
            PreviewBuilderFactory().get_instance().get_file_mimetype(file_path, file_ext)
        )  # nopep8

    def has_pdf_preview(self, file_path: str, file_ext: str = "") -> bool:
        """
        return True if the given file offers PDF preview
        Actually, this is the case for office
        :param file_path:
        :param file_ext: extension associated to the file. Eg 'jpg'. May be empty -
                it's usefull if the extension can't be found in file_path
        :return:
        """
        return self.get_preview_context(file_path, file_ext).builder.has_pdf_preview()

    def has_jpeg_preview(self, file_path: str, file_ext: str = "") -> bool:
        """
        return True if the given file offers jpeg preview
        Actually, this is the case for office, documents and file type
        :param file_path:
        :param file_ext: extension associated to the file. Eg 'jpg'.
        May be empty - it's usefull if the extension can't be found in file_path
        :return:
        """
        return self.get_preview_context(file_path, file_ext).builder.has_jpeg_preview()

    def has_text_preview(self, file_path: str, file_ext: str = "") -> bool:
        """
        return True if the given file offers text preview
        Actually, this is the case for text file and archive file
        :param file_path:
        :param file_ext: extension associated to the file. Eg 'jpg'.
        May be empty - it's usefull if the extension can't be found in file_path
        :return:
        """
        return self.get_preview_context(file_path, file_ext).builder.has_text_preview()

    def has_json_preview(self, file_path: str, file_ext: str = "") -> bool:
        """
        return True if the given file offers json preview
        Actually, this is the case for most type using exiftool
        :param file_path:
        :param file_ext: extension associated to the file. Eg 'jpg'.
        May be empty - it's usefull if the extension can't be found in file_path
        :return:
        """
        return self.get_preview_context(file_path, file_ext).builder.has_json_preview()

    def has_html_preview(self, file_path: str, file_ext: str = "") -> bool:
        """
        return True if the given file offers html preview
        Actually, this is the case for archive files
        :param file_path:
        :param file_ext: extension associated to the file. Eg 'jpg'.
        May be empty - it's usefull if the extension can't be found in file_path
        :return:
        """
        return self.get_preview_context(file_path, file_ext).builder.has_html_preview()

    def get_page_nb(self, file_path: str, file_ext: str = "") -> int:
        """
        Return the page number of the given file.
        :param file_path: path of the file
        :param file_ext: extension associated to the file. Eg 'jpg'. May be empty -
                it's usefull if the extension can't be found in file_path
        :return: number of pages. Default is 1 (eg for a JPEG)
        """

        preview_context = self.get_preview_context(file_path, file_ext)
        # INFO - G.M - 2021-04-29 deal with pivot format
        # jpeg preview from pdf for libreoffice/scribus
        # - change original file to use to pivot file (pdf preview) of the content instead of the
        # original file
        # - use preview context of this pivot pdf file.
        if isinstance(preview_context.builder, DocumentPreviewBuilder):
            file_path = self.get_pdf_preview(file_path=file_path, force=False)
            preview_context = self.get_preview_context(file_path, file_ext=".pdf")
        with preview_context.filelock:
            return preview_context.builder.get_page_number(
                file_path, preview_context.hash, self.cache_path, preview_context.mimetype
            )

    def get_jpeg_preview(
        self,
        file_path: str,
        page: int = -1,
        width: int = None,
        height: int = 256,
        force: bool = False,
        file_ext: str = "",
        dry_run: bool = False,
    ) -> str:
        """
        Return a JPEG preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param page: page of the original document, if it makes sense
        :param width: width of the requested preview image
        :param height: height of the requested preview image
        :param force: if True, do not use cached preview.
        :param file_ext: extension associated to the file. Eg 'jpg'. May be empty -
                it's useful if the extension can't be found in file_path
        :param dry_run: Don't actually generate the file, but return its path as
                if we had
        :return: path to the generated preview file
        """
        preview_context = self.get_preview_context(file_path, file_ext)

        if width is None:
            width = height
        size = ImgDims(width=width, height=height)
        extension = ".jpeg"

        preview_name = self._get_preview_name(preview_context.hash, size, page)
        preview_file_path = os.path.join(self.cache_path, preview_name + extension)  # nopep8

        if dry_run:
            return preview_file_path

        # INFO - G.M - 2021-04-29 deal with pivot format
        # jpeg preview from pdf for libreoffice/scribus
        # - change original file to use to pivot file (pdf preview) of the content instead of the
        # original file
        # - use preview context of this pivot pdf file.
        if isinstance(preview_context.builder, DocumentPreviewBuilder):
            file_path = self.get_pdf_preview(file_path=file_path, force=force)
            preview_context = self.get_preview_context(file_path, file_ext=".pdf")
        with preview_context.filelock:
            if force or not os.path.exists(preview_file_path):
                preview_context.builder.build_jpeg_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    page_id=max(page, 0),  # if page is -1 then return preview of first page,
                    extension=extension,
                    size=size,
                    mimetype=preview_context.mimetype,
                )

        return preview_file_path

    def get_pdf_preview(
        self,
        file_path: str,
        page: int = -1,
        force: bool = False,
        file_ext: str = "",
        dry_run: bool = False,
    ) -> str:
        """
        Return a PDF preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param page: page of the original document. -1 means "all pages"
        :param force: if True, do not use cached preview.
        :param file_ext: extension associated to the file. Eg 'jpg'. May be empty -
                it's usefull if the extension can't be found in file_path
        :param dry_run: Don't actually generate the file, but return its path as
                if we had
        :return: path to the generated preview file
        """
        preview_context = self.get_preview_context(file_path, file_ext)
        extension = ".pdf"
        preview_name = self._get_preview_name(filehash=preview_context.hash, page=page)

        try:
            cache_file_path = self.cache_path + preview_name + extension
            if dry_run:
                return cache_file_path
            with preview_context.filelock:
                if force or not os.path.exists(cache_file_path):
                    preview_context.builder.build_pdf_preview(
                        file_path=file_path,
                        preview_name=preview_name,
                        cache_path=self.cache_path,
                        extension=extension,
                        page_id=page,
                        mimetype=preview_context.mimetype,
                    )

            return cache_file_path

        except AttributeError:
            raise Exception("Error while getting the file the file preview")

    def get_text_preview(
        self, file_path: str, force: bool = False, file_ext: str = "", dry_run: bool = False
    ) -> str:
        """
        Return a TXT preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param force: if True, do not use cached preview.
        :param file_ext: extension associated to the file. Eg 'jpg'. May be empty -
                it's usefull if the extension can't be found in file_path
        :param dry_run: Don't actually generate the file, but return its path as
                if we had
        :return: path to the generated preview file
        """
        preview_context = self.get_preview_context(file_path, file_ext)
        extension = ".txt"
        preview_name = self._get_preview_name(filehash=preview_context.hash)
        try:
            cache_file_path = self.cache_path + preview_name + extension
            if dry_run:
                return cache_file_path
            with preview_context.filelock:
                if force or not os.path.exists(cache_file_path):
                    preview_context.builder.build_text_preview(
                        file_path=file_path,
                        preview_name=preview_name,
                        cache_path=self.cache_path,
                        extension=extension,
                    )
            return cache_file_path

        except AttributeError:
            raise Exception("Error while getting the file the file preview")

    def get_html_preview(
        self, file_path: str, force: bool = False, file_ext: str = "", dry_run: bool = False
    ) -> str:
        """
        Return a HTML preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param force: if True, do not use cached preview.
        :param file_ext: extension associated to the file. Eg 'jpg'. May be empty -
                it's usefull if the extension can't be found in file_path
        :param dry_run: Don't actually generate the file, but return its path as
                if we had
        :return: path to the generated preview file
        """
        preview_context = self.get_preview_context(file_path, file_ext)
        extension = ".html"
        preview_name = self._get_preview_name(filehash=preview_context.hash)
        try:
            cache_file_path = self.cache_path + preview_name + extension
            if dry_run:
                return cache_file_path
            with preview_context.filelock:
                if force or not os.path.exists(cache_file_path):
                    preview_context.builder.build_html_preview(
                        file_path=file_path,
                        preview_name=preview_name,
                        cache_path=self.cache_path,
                        extension=extension,
                    )
            return cache_file_path

        except AttributeError:
            raise Exception("Error while getting the file the file preview")

    def get_json_preview(
        self, file_path: str, force: bool = False, file_ext: str = "", dry_run: bool = False
    ) -> str:
        """
        Return a JSON preview of given file, according to parameters
        :param file_path: path of the file to preview
        :param force: if True, do not use cached preview.
        :param file_ext: extension associated to the file. Eg 'jpg'. May be empty -
                it's usefull if the extension can't be found in file_path
        :param dry_run: Don't actually generate the file, but return its path as
                if we had
        :return: path to the generated preview file
        """
        preview_context = self.get_preview_context(file_path, file_ext)
        extension = ".json"
        preview_name = self._get_preview_name(filehash=preview_context.hash)
        try:
            cache_file_path = self.cache_path + preview_name + extension
            if dry_run:
                return cache_file_path
            with preview_context.filelock:
                if force or not os.path.exists(cache_file_path):  # nopep8
                    preview_context.builder.build_json_preview(
                        file_path=file_path,
                        preview_name=preview_name,
                        cache_path=self.cache_path,
                        extension=extension,
                    )
            return cache_file_path
        except AttributeError:
            raise Exception("Error while getting the file preview")

    def _get_preview_name(self, filehash: str, size: ImgDims = None, page: int = None) -> str:
        """
        Build a hash based on the given parameters.
        This hash will be used as key for caching generated previews.

        The hash is something like this:
            720f89890597ec1eb45e7b775898e806-320x139-page32

        :param hash: hash of the original file
        :param size: requested size (width and height)
        :param page: requested page
        :return:
        """

        page_str = ""
        if page is not None and page > -1:
            page_str = "-page{page}".format(page=page)

        size_str = ""
        if size:
            size_str = "-{width}x{height}".format(width=size.width, height=size.height)

        return "{hash}{size}{page}".format(hash=filehash, size=size_str, page=page_str)

    def get_supported_mimetypes(self) -> typing.List[str]:
        return self._factory.get_supported_mimetypes()

    def get_file_extension(self, mime: str) -> typing.Optional[str]:
        """
        Get one valid file extension related to the given mimetype.
        """
        return mimetypes_storage.guess_extension(mime, strict=False)

    def get_file_extensions(self, mime: str) -> typing.List[str]:
        """
        get all valid file extensions for one the given mimetype
        """
        return mimetypes_storage.guess_all_extensions(mime, strict=False)

    def get_supported_file_extensions(self) -> typing.List[str]:
        """
        Get all supported file_extension by preview_generator
        :return:
        """
        supported_file_extensions = []
        for mime in self.get_supported_mimetypes():
            extensions = mimetypes_storage.guess_all_extensions(mime, strict=False)
            supported_file_extensions.extend(extensions)
        return supported_file_extensions
