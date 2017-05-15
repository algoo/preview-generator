import os
from io import BytesIO
import hashlib

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from PyPreviewGenerator.factory import PreviewBuilderFactory


class PreviewBuilderMeta(type):
    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        cls.register()
        return cls


class PreviewBuilder(object, metaclass=PreviewBuilderMeta):

    mimetype=[]

    def __init__(self):
        print('New Preview Builder')

    @classmethod
    def get_mimetypes_supported(cls):
        return cls.mimetype

    def get_page_number(self, preview_name, file_path, cache_path):
        raise Exception('Number of pages not supported for this kind of Preview'
                        ' Builder. Preview builder must implement a '\
                        'get_page_number method')

    def build_jpeg_preview(self, file_path, preview_name, cache_path, page_id: int, extension='.jpg', size=(256,256)):
        """
        generate the jpg preview
        """
        raise Exception("Not implemented for this kind of document")

    def build_pdf_preview(self, file_path, preview_name, cache_path, extension='.pdf'):
        """
        generate the jpeg preview
        """
        raise Exception("Not implemented for this kind of document")

    def build_html_preview(self, file_path, preview_name, cache_path, extension='.html'):
        """
        generate the html preview
        """
        raise Exception("Not implemented for this kind of document")

    def build_json_preview(self, file_path, preview_name, cache_path, page_id: int=0, extension='.json'):
        """
        generate the json preview
        """
        raise Exception("Not implemented for this kind of document")

    def build_text_preview(self, file_path, preview_name, cache_path, page_id: int=0, extension='.txt'):
        """ 
        return file content from the cache
        """
        raise Exception("Not implemented for this kind of document")

    def get_jpeg_preview(self, file_path: str, preview_name, cache_path, page_id, extension='.jpeg', size=(256,256), force: bool=False):

        if not self.exists_preview(cache_path + preview_name, page_id, extension) or force:
            self.build_jpeg_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=cache_path,
                page_id=page_id,
                extension=extension,
                size=size
            )
        return '{cache}{file}_{page}_{ext}'.format(
            cache=cache_path,
            file=preview_name,
            page=page_id,
            ext=extension,
        )
    def get_pdf_preview(self, file_path: str, preview_name, cache_path, page='full', extension='.pdf', force: bool=False):
        """ 
        return file content from the cache
        """
        if not self.exists_preview(
                path=cache_path + preview_name,
                extension=extension) or force:
            self.build_pdf_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=cache_path,
                extension=extension
            )

        if page =='full':
            return cache_path + preview_name + extension
        else:
            with open(
                    '{path}{file_name}.pdf'.format(
                        path=cache_path,
                        file_name=preview_name
                    ),
                    'rb'
            ) as handler:
                input_pdf = PdfFileReader(handler)
                output_pdf = PdfFileWriter()
                print(page)
                output_pdf.addPage(input_pdf.getPage(int(page)))

                output_stream = BytesIO()
                output_pdf.write(output_stream)
                output_stream.seek(0, 0)

                with open('{path}{file_name}_{page}_{extension}'.format(
                    path=cache_path,
                    file_name=preview_name,
                    page=page,
                    extension=extension
                ), 'wb') \
                as paged_pdf:
                    output_stream.seek(0, 0)
                    buffer = output_stream.read(1024)
                    while buffer:
                        paged_pdf.write(buffer)
                        buffer = output_stream.read(1024)
            return '{path}{file_name}_{page}_'.format(
                path=cache_path,
                file_name=preview_name,
                page=page,
                extension=extension
            )

    def get_html_preview(self, file_path: str, preview_name, cache_path, extension='.html', force: bool=False):
        """ 
        return file content from the cache
        """
        if not self.exists_preview(cache_path + preview_name, extension) or force:
            self.build_html_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=cache_path,
                extension=extension
            )
        return cache_path + preview_name + extension

    def get_json_preview(self, file_path: str, preview_name, cache_path, extension='.json', force: bool=False):
        """ 
        return file content from the cache
        """
        if not self.exists_preview(path=cache_path + preview_name, extension=extension) or force:
            self.build_json_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=cache_path,
                extension=extension
            )
        return cache_path + preview_name + extension

    def get_text_preview(self, file_path: str, preview_name, cache_path, extension='.txt', force: bool=False) -> BytesIO:
        """ 
        return file content from the cache
        """
        if not self.exists_preview(path=cache_path + preview_name, extension=extension) or force:
            self.build_text_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=cache_path,
                extension=extension
            )
        return cache_path + preview_name + extension

    def exists_preview(self, path, page_id=None, extension=''):
        """
        return true if the cache file exists
        """
        if page_id == None:
            full_path = '{path}{extension}'.format(
                path=path,
                extension=extension
            )
        else:
            full_path = '{path}_{page_id}_{extension}'.format(
                path=path,
                page_id=page_id,
                extension=extension
            )

        if os.path.exists(full_path):
            return True
        else:
            return False

    @classmethod
    def register(cls):
        PreviewBuilderFactory.get_instance().register_builder(cls)


class OnePagePreviewBuilder(PreviewBuilder):
    '''
    Generic preview handler for single page document
    '''
    def get_page_number(self, file_path, preview_name, cache_path):
        return 1

    def exists_preview(self, path, page_id=None, extension=''):
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

    def get_jpeg_preview(self, file_path: str, preview_name, cache_path, page_id, extension='.jpeg', size=(256, 256), force: bool=False):

        if (not self.exists_preview(cache_path + preview_name, page_id, extension)) or force:
            self.build_jpeg_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=cache_path,
                page_id=page_id,
                extension=extension,
                size=size
            )
        return cache_path + preview_name + extension


class ImagePreviewBuilder(OnePagePreviewBuilder):
    '''
    Generic preview handler for an Image (except multi-pages images)
    '''
    pass








