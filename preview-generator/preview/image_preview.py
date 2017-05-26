import typing

from preview_generator import file_converter
from preview_generator.preview.generic_preview import ImagePreviewBuilder


class ImagePreviewBuilderWand(ImagePreviewBuilder):
    mimetype = ['image/x-ms-bmp',
                'image/gif',
                'image/jpeg']

    def build_jpeg_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int,
                           extension: str = '.jpeg',
                           size: typing.Tuple[int, int] = (256, 256)) -> None:
        """
        generate the bmp preview
        """

        with open(file_path, 'rb') as img:
            result = file_converter.image_to_jpeg_wand(img, size)
            with open('{path}{extension}'.format(
                    path=cache_path + preview_name,
                    extension=extension
            ), 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)
