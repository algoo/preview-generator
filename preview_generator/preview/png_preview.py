import typing
from preview_generator import file_converter
from preview_generator.preview.generic_preview import ImagePreviewBuilder


class ImagePreviewBuilderPillow(ImagePreviewBuilder):
    mimetype = ['image/png']

    def build_jpeg_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int,
                           extension: str = '.jpeg',
                           size: typing.Tuple[int, int] = (256, 256)) -> None:
        """
        generate the jpg preview
        """
        with open(file_path, 'rb') as img:
            result = file_converter.image_to_jpeg_pillow(img, size)
            with open(
                    '{path}{extension}'.format(
                        path=cache_path + preview_name,
                        extension=extension
                    ),
                    'wb'
            ) as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def get_original_size(self, file_path: str, page_id: int=-1) -> typing.Tuple[int, int]:
        with open(file_path, 'rb') as img:
            size = file_converter.get_image_size(img)
            return size
