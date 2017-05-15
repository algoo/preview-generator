from PyPreviewGenerator import file_converter
from PyPreviewGenerator.preview.generic_preview import OnePagePreviewBuilder

class TextPreviewBuilder(OnePagePreviewBuilder):

    mimetype = ['text/plain']

    def build_text_preview(self, file_path, preview_name, cache_path, page_id: int=0, extension='.txt'):
        """
        generate the text preview
        """

        # try:
        #     os.mkdir(cache_path.format(d_id=document_id))
        # except OSError:
        #     pass

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
