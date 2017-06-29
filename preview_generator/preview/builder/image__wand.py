# -*- coding: utf-8 -*-

from io import BytesIO
import logging
import typing

from wand.image import Color
from wand.image import Image as WImage

from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import compute_resize_dims
from preview_generator.utils import compute_crop_dims


def convert_pdf_to_jpeg(
        pdf: typing.Union[str, typing.IO[bytes]],
        preview_size: ImgDims
) -> BytesIO:
    with WImage(file=pdf) as img:
        height, width = img.size
        if height < width:
            breadth = height
        else:
            breadth = width
        with WImage(
                width=breadth,
                height=breadth,
                background=Color('white')
        ) as image:
            image.composite(
                img,
                top=0,
                left=0
            )
            image.crop(0, 0, width=breadth, height=breadth)

            from preview_generator.utils import compute_resize_dims
            from preview_generator.utils import compute_crop_dims

            resize_dims = compute_resize_dims(
                ImgDims(image.width, image.height),
                preview_size
            )

            image.resize(resize_dims.width, resize_dims.height)

            crop_dims = compute_crop_dims(
                ImgDims(image.width, image.height),
                preview_size
            )
            image.crop(
                crop_dims.left,
                crop_dims.top,
                crop_dims.right,
                crop_dims.bottom
            )
            content_as_bytes = image.make_blob('jpeg')
            output = BytesIO()
            output.write(content_as_bytes)
            output.seek(0, 0)
            return output


class ImagePreviewBuilderWand(ImagePreviewBuilder):
    mimetype = [
        'image/x-ms-bmp',
        'image/gif',
        'image/jpeg',
    ]

    def build_jpeg_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int,
            extension: str = '.jpeg',
            size: ImgDims=None
    ) -> None:

        with open(file_path, 'rb') as img:
            result = self.image_to_jpeg_wand(
                img,
                ImgDims(width=size.width, height=size.height)
            )

            with open('{path}{extension}'.format(
                    path=cache_path + preview_name,
                    extension=extension
            ), 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def image_to_jpeg_wand(
            self,
            jpeg: typing.Union[str, typing.IO[bytes]],
            preview_dims: ImgDims=None
    ) -> BytesIO:
        '''
        for jpeg, gif and bmp
        :param jpeg:
        :param size:
        :return:
        '''
        logging.info('Converting image to jpeg using wand')

        with WImage(file=jpeg) as image:

            preview_dims = ImgDims(
                width=preview_dims.width,
                height=preview_dims.height
            )

            resize_dim = compute_resize_dims(
                dims_in=ImgDims(width=image.size[0], height=image.size[1]),
                dims_out=preview_dims
            )
            image.resize(resize_dim.width, resize_dim.height)

            # FIXME - remove this
            # left = round((image.width / 2) - (preview_dims.width / 2))
            # top = round((image.height / 2) - (preview_dims.height / 2))
            # right = left + preview_dims.width
            # bottom = top + preview_dims.height

            crop_dims = compute_crop_dims(
                ImgDims(image.width, image.height),
                preview_dims
            )
            image.crop(
                left=crop_dims.left,
                top=crop_dims.top,
                right=crop_dims.right,
                bottom=crop_dims.bottom
            )

            content_as_bytes = image.make_blob('jpeg')
            output = BytesIO()
            output.write(content_as_bytes)
            output.seek(0, 0)
            return output
