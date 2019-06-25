# -*- coding: utf-8 -*-

from io import BytesIO
import logging

import PIL
from PIL import Image
import typing

from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import compute_resize_dims
from preview_generator.utils import ImgDims

# INFO - G.M - 2019-06-25 - some configuration for jpeg saved,
# see https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html?highlight=JPEG#jpeg
# optimize -> extra pass to select optimal encoded
# quality -> compression level from 1 to 100
# progressive -> permit to see a blured version of file instead of partial image when image
# is not fully downloaded, nice for web usage.
JPEG_OPTIMIZE = True
JPEG_QUALITY = 75
JPEG_PROGRESSIVE = True
# Pillow algorithm use for resampling, bilinear is not the fastest but is fast
# enough, this permit good enough image (using faster algorithm return much more
# aliasing. see https://pillow.readthedocs.io/en/latest/handbook/concepts.html?highlight=Bilinear#filters
# for algorithm list.
JPEG_RESAMPLE = PIL.Image.BILINEAR
# Pillow deal with many different mode of image:
# https://pillow.readthedocs.io/en/latest/handbook/concepts.html#modes
# those are mode known to have alpha layer, so needing special process to
# have clean white background
# RGBA is RGB + Alpha channel
# LA is L (8-bit pixels, black and white) + Alpha channel
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
            image = image.resize((resize_dim.width, resize_dim.height), resample=JPEG_RESAMPLE)
            if image.mode not in TRANSPARENCY_MODES:
                # INFO - G.M - 2019-06-18 - Try directly saving new image, this may failed due to
                # image mode issue.
                try:
                    image.save(output, 'jpeg', optimize=JPEG_OPTIMIZE, quality=JPEG_QUALITY, progressive=JPEG_PROGRESSIVE)
                except OSError as exc:
                    image = image.convert('RGB')
                    image.save(output, 'jpeg', optimize=JPEG_OPTIMIZE, quality=JPEG_QUALITY, progressive=JPEG_PROGRESSIVE)
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
                output_image.save(output, 'jpeg', optimize=JPEG_OPTIMIZE, quality=JPEG_QUALITY, progressive=JPEG_PROGRESSIVE)

            output.seek(0, 0)
            return output