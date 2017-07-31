# -*- coding: utf-8 -*-

from io import BytesIO
import json
import logging
from PIL import Image
from PyPDF2 import PdfFileReader
import typing
from wand.image import Image as WImage
from preview_generator.utils import PreviewGeneratorJsonEncoder

def txt_to_txt(text: typing.IO[typing.Any]) -> typing.IO[typing.Any]:
    logging.info('Converting text to text')
    return text


def image_to_json(
        img: typing.IO[bytes],
        filesize: int=0
) -> BytesIO:
    logging.info('Converting image to json')
    with Image.open(img) as image:
        if not filesize:
            filesize = len(img.read())
            # INFO - D.A. - 2017-06-29
            # filesize here is not exactly what will be stored on filesystem
            # because filesystem size depends file system properties which are
            # not available when working with in memory objects
        info = {
            'width': image.size[0],
            'height': image.size[1],
            'size': filesize,
            'mode': image.mode,
            'info': image.info
        }

    output = BytesIO()

    content = json.dumps(info, cls=PreviewGeneratorJsonEncoder)
    output.write(content.encode())
    output.seek(0, 0)
    return output


def get_image_size(img: typing.IO[bytes]) -> typing.Tuple[int, int]:
    with WImage(file=img) as image:
        return image.size


def get_pdf_size(
        pdf: typing.Union[str, typing.IO[bytes]],
        page_id: int
) -> typing.Tuple[int, int]:
    input_pdf = PdfFileReader(pdf)
    page = input_pdf.getPage(page_id).mediaBox
    size = (int(page.getUpperRight_x()), int(page.getUpperRight_y()))
    return size
