from preview_generator import file_converter
from preview_generator.preview.generic_preview import OnePagePreviewBuilder


class ZipPreviewBuilder(OnePagePreviewBuilder):
    mimetype = ['application/x-compressed',
                'application/x-zip-compressed',
                'application/zip',
                'multipart/x-zip',
                'application/x-tar',
                'application/x-gzip',
                'application/x-gtar',
                'application/x-tgz',
                ]

    def build_text_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int = 0,
                           extension: str = '.txt') -> None:
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

    def build_html_preview(self, file_path: str, preview_name: str,
                           cache_path: str, extension: str = '.html') -> None:
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

    def build_json_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int = 0,
                           extension: str = '.json') -> None:
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


class TargzPreviewBuilder(OnePagePreviewBuilder):
    mimetype = ['application/gzip',
                'application/gtar',
                'application/tgz',
                ]

    def build_text_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int = 0,
                           extension: str = '.txt') -> None:
        """
        generate the text preview
        """
        raise Exception("Not implemented for tar gz document")

    def build_html_preview(self, file_path: str, preview_name: str,
                           cache_path: str, extension: str = '.html') -> None:
        """
        generate the text preview
        """
        raise Exception("Not implemented for tar gz document")

    def build_json_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int = 0,
                           extension: str = '.json') -> None:
        """
        generate the json preview
        """
        raise Exception("Not implemented for tar gz document")

