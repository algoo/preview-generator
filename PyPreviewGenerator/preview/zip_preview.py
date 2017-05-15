from PyPreviewGenerator import file_converter
from PyPreviewGenerator.preview.generic_preview import OnePagePreviewBuilder

class ZipPreviewBuilder(OnePagePreviewBuilder):

    mimetype = ['application/x-compressed',
                'application/x-zip-compressed',
                'application/zip',
                'multipart/x-zip',
                'application/x-tar'
                ]

    def build_text_preview(self, file_path, preview_name, cache_path, page_id: int=0, extension='.txt'):
        """
        generate the text preview
        """

        with open(file_path, 'rb') as img:
            result = file_converter.zip_to_txt(img)
            with open(cache_path + preview_name + extension, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)


    def build_html_preview(self, file_path, preview_name, cache_path, extension='.html'):
        """
        generate the text preview
        """

        with open(file_path, 'rb') as img:
            result = file_converter.zip_to_html(img)
            with open(cache_path + preview_name + extension, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)


    def build_json_preview(self, file_path, preview_name, cache_path, page_id: int=0, extension='.json'):
        """
        generate the json preview
        """

        with open(file_path, 'rb') as img:
            result = file_converter.zip_to_json(img)
            with open(cache_path + preview_name + extension, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)


