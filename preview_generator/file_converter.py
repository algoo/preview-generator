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
