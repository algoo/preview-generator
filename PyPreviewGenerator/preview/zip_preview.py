from PyPreviewGenerator import file_converter
from PyPreviewGenerator.preview.generic_preview import OnePagePreviewBuilder

class ZipPreviewBuilder(OnePagePreviewBuilder):

    mimetype = ['application/x-compressed',
                'application/x-zip-compressed',
                'application/zip',
                'multipart/x-zip',
                'application/x-tar'
                ]

    def build_text_preview(self, file_path, cache_path, page_id: int, extension='.txt'):
        """
        generate the text preview
        """

        # try:
        #     os.mkdir(cache_path.format(d_id=document_id))
        # except OSError:
        #     pass

        file_name = self.get_file_hash(file_path)

        with open(file_path, 'rb') as img:
            result = file_converter.zip_to_txt(img)
            with open(cache_path + file_name + extension, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)


    def build_html_preview(self, file_path, cache_path, page_id: int, extension='.html'):
        """
        generate the text preview
        """

        # try:
        #     os.mkdir(cache_path.format(d_id=document_id))
        # except OSError:
        #     pass

        file_name = self.get_file_hash(file_path)

        with open(file_path, 'rb') as img:
            result = file_converter.zip_to_html(img)
            with open(cache_path + file_name + extension, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

