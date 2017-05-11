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

    def get_file_hash(self, file_path, size=None):
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

    def get_page_number(self, file_path, cache_path):
        raise Exception('Number of pages not supported for this kind of Preview'
                        ' Builder. Preview builder must implement a '\
                        'get_page_number method')

    def build_jpeg_preview(self, file_path, cache_path, page_id: int, extension='.jpg', size=(256,256)):
        """
        generate the jpg preview
        """
        raise Exception("Not implemented for this kind of document")

    def build_pdf_preview(self, file_path, cache_path, extension='.pdf'):
        """
        generate the jpeg preview
        """
        raise Exception("Not implemented for this kind of document")

    def build_html_preview(self, file_path, cache_path, page_id: int, extension='.html'):
        """
        generate the html preview
        """
        raise Exception("Not implemented for this kind of document")

    def build_json_preview(self, file_path, cache_path, page_id: int, extension='.json'):
        """
        generate the json preview
        """
        raise Exception("Not implemented for this kind of document")

    def build_text_preview(self, file_path, cache_path, page_id: int, extension='.txt'):
        """ 
        return file content from the cache
        """
        raise Exception("Not implemented for this kind of document")

    def get_jpeg_preview(self, file_path: str, cache_path, page_id, extension='.jpeg', size=(256,256), force: bool=False):

        print('gjp1')
        file_name = self.get_file_hash(file_path, size)
        if not self.exists_preview(cache_path + file_name, page_id, extension) or force:
            self.build_jpeg_preview(
                file_path=file_path,
                cache_path=cache_path,
                page_id=page_id,
                extension=extension,
                size=size
            )
        return '{cache}{file}_{page}_{ext}'.format(
            cache=cache_path,
            file=file_name,
            page=page_id,
            ext=extension,
        )
    def get_pdf_preview(self, file_path: str, cache_path, page='full', extension='.pdf', force: bool=False):
        """ 
        return file content from the cache
        """
        file_name = self.get_file_hash(file_path)
        if not self.exists_preview(
                path=cache_path + file_name,
                extension=extension) or force:
            self.build_pdf_preview(
                file_path=file_path,
                cache_path=cache_path,
                extension=extension
            )

        if page =='full':
            return cache_path + file_name + extension
        else:
            with open(
                    '{path}{file_name}.pdf'.format(
                        path=cache_path,
                        file_name=file_name
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
                    file_name=file_name,
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
                file_name=file_name,
                page=page,
                extension=extension
            )

    def get_html_preview(self, file_path: str, cache_path, page_id: int, extension='.html', force: bool=False):
        """ 
        return file content from the cache
        """
        file_name = self.get_file_hash(file_path)
        if not self.exists_preview(cache_path + file_name, page_id, extension) or force:
            self.build_html_preview(
                file_path=file_path,
                cache_path=cache_path,
                page_id=page_id,
                extension=extension
            )
        return cache_path + file_name + extension

    def get_json_preview(self, doc_id: int, page_id: int, force: bool=False):
        """ 
        return file content from the cache
        """
        return None

    def get_text_preview(self, file_path: str, cache_path, page_id: int, extension='.txt', force: bool=False) -> BytesIO:
        """ 
        return file content from the cache
        """
        file_name = self.get_file_hash(file_path)
        if not self.exists_preview(path=cache_path + file_name, extension=extension) or force:
            self.build_text_preview(
                file_path=file_path,
                cache_path=cache_path,
                page_id=page_id,
                extension=extension
            )
        return cache_path + file_name + extension

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
    def get_page_number(self, file_path, cache_path):
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

    def get_jpeg_preview(self, file_path: str, cache_path, page_id, extension='.jpeg', size=(256,256), force: bool=False):

        file_name = self.get_file_hash(file_path, size)
        if (not self.exists_preview(cache_path + file_name, page_id, extension)) or force:
            self.build_jpeg_preview(
                file_path=file_path,
                cache_path=cache_path,
                page_id=page_id,
                extension=extension,
                size=size
            )
        return cache_path + file_name + extension


class ImagePreviewBuilder(OnePagePreviewBuilder):
    '''
    Generic preview handler for an Image (except multi-pages images)
    '''

    def get_file_hash(self, file_path, size=(256,256)):

        file_name = '{fn}-{fh}x{fw}'.format(
            fn=os.path.basename(file_path),
            fh=str(size[0]),
            fw=str(size[1]),
        )

        file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        return '{fn}-{fh}'.format(fn=file_name, fh=file_hash)








