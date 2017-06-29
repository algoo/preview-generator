# -*- coding: utf-8 -*-

from io import BytesIO
import logging
from PIL import Image
import typing

from preview_generator import file_converter
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import compute_resize_dims
from preview_generator.utils import compute_crop_dims
from preview_generator.utils import ImgDims


class ImagePreviewBuilderPillow(ImagePreviewBuilder):
    mimetype = ['image/png']

    def build_jpeg_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int,
                           extension: str='.jpeg',
                           size: ImgDims=None) -> None:
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

    def get_original_size(
            self,
            file_path: str,
            page_id: int=-1
    ) -> typing.Tuple[int, int]:
        # FIXME - use ImgDims instead of Tuple for return type
        with open(file_path, 'rb') as img:
            size = file_converter.get_image_size(img)
            return size

    def image_to_jpeg_pillow(
            self,
            png: typing.Union[str, typing.IO[bytes]],
            preview_dims: ImgDims
    ) -> BytesIO:
        logging.info('Converting image to jpeg using Pillow')
        temporary_image = Image.new(
            'RGB',
            (preview_dims.width, preview_dims.height),
            (255, 255, 255)
        )

        with Image.open(png) as image:

            preview_dims = ImgDims(
                width=preview_dims.width,
                height=preview_dims.height
            )

            resize_dim = compute_resize_dims(
                dims_in=ImgDims(width=image.size[0], height=image.size[1]),
                dims_out=preview_dims
            )
            image.resize((resize_dim.width, resize_dim.height))

            crop_dims = compute_crop_dims(
                ImgDims(image.width, image.height),
                preview_dims
            )

            crop_box = (
                crop_dims.left,
                crop_dims.top,
                crop_dims.right,
                crop_dims.bottom
            )
            layer_copied = image.crop(crop_box)

            try:
                temporary_image.paste(layer_copied, (0, 0), layer_copied)
            except ValueError:
                logging.warning(
                    'Failed the transparency mask superposition. '
                    'Maybe your image does not contain a transparency mask')
                temporary_image.paste(layer_copied)

            output = BytesIO()
            temporary_image.save(output, 'jpeg')
            output.seek(0, 0)
            return output
