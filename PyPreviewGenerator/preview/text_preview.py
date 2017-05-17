from PyPreviewGenerator import file_converter
from PyPreviewGenerator.preview.generic_preview import OnePagePreviewBuilder

class TextPreviewBuilder(OnePagePreviewBuilder):

    mimetype = ['text/plain']

    def build_text_preview(self, file_path: str, preview_name: str, cache_path: str, page_id: int=0, extension: str='.txt') -> None:
        """
        generate the text preview
        """
        with open(file_path, 'rb') as img:
            result = file_converter.txt_to_txt(img)
            with open('{path}{extension}'.format(
                        path=cache_path + preview_name,
                        extension=extension
                    ),
                    'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)
