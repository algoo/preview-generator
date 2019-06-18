# -*- coding: utf-8 -*-

from io import BytesIO
import logging
from PIL import Image
import typing

from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import compute_resize_dims
from preview_generator.utils import ImgDims

TRANSPARENCY_MODES = ['RGBA', 'LA']
class ImagePreviewBuilderPillow(ImagePreviewBuilder):
    @classmethod
    def get_label(cls) -> str:
        return 'Bitmap images - based on Pillow'

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [
            'image/png',
            'application/postscript',
            'image/x-eps',
        ]

    def build_jpeg_preview(
        self, file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str='.jpeg',
        size: ImgDims=None,
        mimetype: str = ''
    ) -> None:
        """
        generate the jpg preview
        """
        with open(file_path, 'rb') as img:
            result = self.image_to_jpeg_pillow(img, size)
            preview_file_path = '{path}{extension}'.format(
                path=cache_path + preview_name,
                extension=extension
            )
            with open(preview_file_path, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def image_to_jpeg_pillow(
            self,
            png: typing.Union[str, typing.IO[bytes]],
            preview_dims: ImgDims
    ) -> BytesIO:
        self.logger.info('Converting image to jpeg using Pillow')

        with Image.open(png) as image:
            resize_dim = compute_resize_dims(
                dims_in=ImgDims(width=image.size[0], height=image.size[1]),
                dims_out=preview_dims
            )
            output = BytesIO()
            image = image.resize((resize_dim.width, resize_dim.height))
            if image.mode not in TRANSPARENCY_MODES:
                # INFO - G.M - 2019-06-18 - Try directly saving new image, this may failed due to
                # image mode issue.
                try:
                    image.save(output, 'jpeg')
                except OSError as exc:
                    image = image.convert('RGB')
                    image.save(output, 'jpeg')
            else:
                # INFO - G.M - 2019-06-18 - choose saving mode according to image mode, this should
                # be jpeg compatible mode
                if image.mode == 'RGBA':
                    output_image = Image.new(
                        'RGB',
                        (resize_dim.width, resize_dim.height),
                        (255, 255, 255)
                    )
                elif image.mode == 'LA':
                    output_image = Image.new(
                        'L',
                        (resize_dim.width, resize_dim.height),
                        1
                    )
                else:
                    raise Exception()

                # INFO - G.M - 2019-06-18 - in case of transparency mode, do apply image over blank output image.
                try:
                    output_image.paste(image, (0, 0), image)
                except ValueError:
                    self.logger.warning(
                        'Failed the transparency mask superposition. '
                        'Maybe your image does not contain a transparency mask')
                    output_image.paste(image)
                output_image.save(output, 'jpeg')

            output.seek(0, 0)
            return output