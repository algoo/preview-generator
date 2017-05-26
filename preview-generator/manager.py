import hashlib
import os

import logging
import typing

from preview_generator.factory import PreviewBuilderFactory


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

    def get_nb_page(self, file_path: str, cache_path: str) -> int:
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
        preview_name = self.get_file_hash(
            file_path=file_path,
            size=size,
            page=page,
            use_original_filename=use_original_filename
        )
        try:
            return builder.get_jpeg_preview(
                file_path=file_path,
                preview_name=preview_name,
                page_id=page,
                cache_path=self.cache_path,
                extension=extension,
                force=force,
                size=size
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
            return builder.get_pdf_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=self.cache_path,
                force=force,
                extension=extension,
                page=page,
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
            return builder.get_text_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=self.cache_path,
                force=force,
                extension=extension
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
            return builder.get_html_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=self.cache_path,
                force=force,
                extension=extension,
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
            return builder.get_json_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=self.cache_path,
                force=force,
                extension=extension
            )
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

        file_name  = []
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





        # if size == None:
        #     file_name = os.path.basename(file_path)
        # else:
        #     file_name = '{fn}-{fh}x{fw}'.format(
        #         fn=os.path.basename(file_path),
        #         fh=str(size[0]),
        #         fw=str(size[1]),
        #     )
        #
        # file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        # if page == -1 or page == None:
        #     return '{fn}-{fh}'.format(fn=file_name, fh=file_hash)
        # else:
        #     return '{fn}-{fh}-page{page}'.format(fn=file_name, fh=file_hash, page=page)

