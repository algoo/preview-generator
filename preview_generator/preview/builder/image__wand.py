# -*- coding: utf-8 -*-

from io import BytesIO
import logging
import typing
import mimetypes
import wand.version

from wand.image import Color
from wand.image import Image as WImage

from preview_generator.preview.generic_preview import OnePagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import compute_resize_dims

from pdf2image import convert_from_bytes


# def convert_pdf_to_jpeg(
#         pdf: typing.Union[str, typing.IO[bytes]],
#         preview_size: ImgDims
# ) -> BytesIO:
#     with WImage(file=pdf) as img:
#         # HACK - D.A. - 2017-08-01
#         # The following 2 lines avoid black background in case of transparent
#         # objects found on the page. As we save to JPEG, this is not a problem
#         img.background_color = Color('white')
#         img.alpha_channel = 'remove'

#         resize_dims = compute_resize_dims(
#             ImgDims(img.width, img.height),
#             preview_size
#         )

#         img.resize(resize_dims.width, resize_dims.height)
#         content_as_bytes = img.make_blob('jpeg')
#         output = BytesIO()
#         output.write(content_as_bytes)
#         output.seek(0, 0)
#         return output


def convert_pdf_to_jpeg(
    pdf: typing.Union[str, typing.IO[bytes]],
    preview_size: ImgDims
) -> BytesIO:

    pdf = pdf.read()
    images = convert_from_bytes(pdf)

    output = BytesIO()
    for image in images:
        resize_dims = compute_resize_dims(
            ImgDims(image.width, image.height),
            preview_size
        )
        resized = image.resize((resize_dims.width, resize_dims.height,))
        resized.save(output, format="JPEG")

    output.seek(0, 0)
    return output


class ImagePreviewBuilderWand(OnePagePreviewBuilder):
    MIMETYPES = []  # type: typing.List[str]

    @classmethod
    def get_label(cls) -> str:
        return 'Images - based on WAND (image magick)'

    @classmethod
    def __load_mimetypes(cls) -> typing.List[str]:
        """
        Load supported mimetypes from WAND library
        :return: list of supported mime types
        """
        all_supported = wand.version.formats("*")
        mimes = []  # type: typing.List[str]
        for supported in all_supported:
            url = "./FILE.{0}".format(supported)  # Fake a url
            mime, enc = mimetypes.guess_type(url)
            if mime and mime not in mimes:
                if 'video' not in mime:
                    # TODO - D.A. - 2018-09-24 - Do not skip video if supported
                    mimes.append(mime)
        return mimes

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        """
        :return: list of supported mime types
        """
        if len(ImagePreviewBuilderWand.MIMETYPES) == 0:
            ImagePreviewBuilderWand.MIMETYPES = cls.__load_mimetypes()
        return ImagePreviewBuilderWand.MIMETYPES

    def build_jpeg_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int,
            extension: str = '.jpeg',
            size: ImgDims=None,
            mimetype: str = ''
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

        with WImage(file=jpeg, background=Color('white')) as image:

            preview_dims = ImgDims(
                width=preview_dims.width,
                height=preview_dims.height
            )

            resize_dim = compute_resize_dims(
                dims_in=ImgDims(width=image.size[0], height=image.size[1]),
                dims_out=preview_dims
            )
            image.resize(resize_dim.width, resize_dim.height)

            content_as_bytes = image.make_blob('jpeg')
            output = BytesIO()
            output.write(content_as_bytes)
            output.seek(0, 0)
            return output
