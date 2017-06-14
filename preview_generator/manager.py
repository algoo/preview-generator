import hashlib
import os

import logging
from time import sleep

import typing
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO

from preview_generator.factory import PreviewBuilderFactory
from preview_generator.preview.odt_preview import OfficePreviewBuilder


class PreviewManager(object):
    cache_path = ''
    factory = PreviewBuilderFactory()

    def __init__(self, path: str, create_folder: bool=False) -> None:
        if create_folder == True:
            try:
                os.makedirs(path)
            except OSError:
                pass
        if path[-1] != '/':
            path = path + '/'
        self.cache_path = path

    def get_nb_page(self, file_path: str) -> int:
        cache_path = self.cache_path
        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)

        preview_name = self.get_file_hash(file_path)
        page_nb = builder.get_page_number(file_path, preview_name, cache_path)
        return page_nb

    def get_jpeg_preview(
            self,
            file_path: str,
            page: int = -1,
            height: int = 256,
            width: int = None,
            force: bool = False,
            use_original_filename: bool = True
    ) -> str:

        if width == None:
            width = height

        size = (height, width)

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.jpeg'
        if isinstance(builder, OfficePreviewBuilder):
            preview_name = self.get_file_hash(
                file_path=file_path,
                use_original_filename=use_original_filename
            )
            file_path = self.get_pdf_preview(
                file_path=file_path,
                page=page,
                force=force,
                use_original_filename=use_original_filename
            )
            preview_name = self.get_file_hash(
                file_path=file_path,
                size=size,
                page=page,
                use_original_filename=False
            )
        else:
            preview_name = self.get_file_hash(
                file_path=file_path,
                size=size,
                page=page,
                use_original_filename=False
            )

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)

        try:
            if not self.exists_preview(
                    self.cache_path + preview_name,
                    extension
            ) or force:
                builder.build_jpeg_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    page_id=page,
                    extension=extension,
                    size=size
                )

            if page == -1:
                return self.cache_path + preview_name + extension
            else:
                return '{cache}{file}{ext}'.format(
                    cache=self.cache_path,
                    file=preview_name,
                    ext=extension,
                )
        except AttributeError:
            raise Exception('Error while getting the file the file preview')


    def get_pdf_preview(
            self,
            file_path: str,
            page: int = -1,
            force: bool = False,
            use_original_filename: bool = True
    ) -> str:

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.pdf'
        preview_name = self.get_file_hash(
            file_path=file_path,
            page=page,
            use_original_filename=use_original_filename
        )
        try:
            if not self.exists_preview(
                    path=self.cache_path + preview_name,
                    extension=extension) or force:
                builder.build_pdf_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension,
                    page_id=page
                )

            if page == -1 or page == None:
                return '{path}{file_name}{extension}'.format(
                    path=self.cache_path,
                    file_name=preview_name,
                    extension=extension
                )
            else:
                return '{path}{file_name}{extension}'.format(
                    path=self.cache_path,
                    file_name=preview_name,
                    extension=extension
                )
        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_text_preview(
            self,
            file_path: str,
            force: bool = False,
            use_original_filename: bool = True
    ) -> str:

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.txt'
        preview_name = self.get_file_hash(
            file_path=file_path,
            use_original_filename=use_original_filename)
        try:
            if not self.exists_preview(
                    path=self.cache_path + preview_name,
                    extension=extension
            ) or force:
                builder.build_text_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return '{cache}{file}{ext}'.format(
                cache=self.cache_path,
                file=preview_name,
                ext=extension,
            )
        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_html_preview(
            self,
            file_path: str,
            force: bool = False,
            use_original_filename: bool = True
    ) -> str:
        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.html'
        preview_name = self.get_file_hash(
            file_path,
            use_original_filename=use_original_filename
        )
        try:
            if not self.exists_preview(
                self.cache_path + preview_name,
                extension=extension
            ) or force:
                builder.build_html_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return '{cache}{file}{ext}'.format(
                cache=self.cache_path,
                file=preview_name,
                ext=extension,
            )
        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_json_preview(
            self,
            file_path: str,
            force: bool = False,
            use_original_filename: bool = True
    ) -> str:
        mimetype = self.factory.get_document_mimetype(file_path)
        logging.info('Mimetype of the document is :' + mimetype)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.json'
        preview_name = self.get_file_hash(
            file_path=file_path,
            use_original_filename=use_original_filename
        )
        try:
            if not self.exists_preview(
                path=self.cache_path + preview_name,
                extension=extension
            ) or force:
                builder.build_json_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=self.cache_path,
                    extension=extension
                )
            return self.cache_path + preview_name + extension
        except AttributeError:
            raise Exception('Error while getting the file the file preview')

    def get_file_hash(
            self,
            file_path: str,
            size: typing.Tuple[int, int] = None,
            page: int = None,
            use_original_filename: bool = True
    ) -> str:
        if '.' in file_path:
            tab_str = file_path.split('.')
            file_path = ''
            for index in range(0, len(tab_str) - 1):
                file_path = file_path + tab_str[index]

        file_name = []
        if use_original_filename == True :
            file_name.append(os.path.basename(file_path))
        if size != None :
            file_name.append('{fh}x{fw}'.format(
                fh=size[0],
                fw=size[1]
            ))
        file_name.append(hashlib.md5(file_path.encode('utf-8')).hexdigest())

        if page != -1 and page != None:
            file_name.append('page{page}'.format(page=page))

        return '-'.join(file_name)

    def exists_preview(
            self,
            path: str,
            extension: str = ''
    ) -> bool:
        """
        return true if the cache file exists
        """
        full_path = '{path}{extension}'.format(
            path=path,
            extension=extension
        )

        if os.path.exists(full_path):
            return True
        else:
            return False

