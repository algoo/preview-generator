import hashlib
import os

from PyPreviewGenerator.factory import PreviewBuilderFactory


class PreviewManager(object):

    cache_path = ''
    factory = PreviewBuilderFactory()

    def __init__(self, path: str):
        if path[-1] != '/':
            path = path + '/'
        self.cache_path = path

    def get_nb_page(self, file_path, cache_path):
        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        preview_name = self.get_file_hash(file_path)
        page_nb = builder.get_page_number(file_path, preview_name, cache_path)
        return page_nb

    def get_jpeg_preview(self, file_path: str, page=None, height=256, width=None, force: bool=False):

        if width == None:
            width = height

        size = (height, width)

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.jpeg'
        preview_name=self.get_file_hash(file_path, size)
        return builder.get_jpeg_preview(
            file_path=file_path,
            preview_name=preview_name,
            page_id=page,
            cache_path=self.cache_path,
            extension=extension,
            force=force,
            size=size
        )

    def get_pdf_preview(self, file_path: str, page='full', force: bool=False):

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.pdf'
        preview_name = self.get_file_hash(file_path)
        return builder.get_pdf_preview(
            file_path=file_path,
            preview_name=preview_name,
            cache_path=self.cache_path,
            force=force,
            extension=extension,
            page=page,
        )

    def get_text_preview(self, file_path: str, page=0, force: bool=False):

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.txt'
        preview_name = self.get_file_hash(file_path)
        return builder.get_text_preview(
            file_path=file_path,
            preview_name=preview_name,
            cache_path=self.cache_path,
            force=force,
            extension=extension
        )

    def get_html_preview(self, file_path: str, page=0, force: bool=False):
        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.html'
        preview_name = self.get_file_hash(file_path)
        return builder.get_html_preview(
            file_path=file_path,
            preview_name=preview_name,
            cache_path=self.cache_path,
            force=force,
            extension=extension,
        )

    def get_json_preview(self, file_path: str, page=0, force: bool=False):
        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.json'
        preview_name = self.get_file_hash(file_path)
        return builder.get_json_preview(
            file_path=file_path,
            preview_name=preview_name,
            cache_path=self.cache_path,
            force=force,
            extension=extension
        )

    def get_file_hash(self, file_path, size=None):
        if '.' in file_path:
            tab_str = file_path.split('.')
            file_path=''
            for index in range(0 ,len(tab_str)-1):
                file_path = file_path + tab_str[index]
        if size == None:
            file_name = os.path.basename(file_path)
        else:
            file_name = '{fn}-{fh}x{fw}'.format(
                fn=os.path.basename(file_path),
                fh=str(size[0]),
                fw=str(size[1]),
            )

        file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        return '{fn}-{fh}'.format(fn=file_name, fh=file_hash)