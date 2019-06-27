# -*- coding: utf-8 -*-

import logging
import typing

from PyPDF2 import PdfFileReader
from wand.image import Image as WImage

from preview_generator.utils import LOGGER_NAME


def txt_to_txt(text: typing.IO[typing.Any]) -> typing.IO[typing.Any]:
    logging.getLogger(LOGGER_NAME).info("Converting text to text")
    return text


def get_image_size(img: typing.IO[bytes]) -> typing.Tuple[int, int]:
    with WImage(file=img) as image:
        return image.size


def get_pdf_size(pdf: typing.Union[str, typing.IO[bytes]], page_id: int) -> typing.Tuple[int, int]:
    input_pdf = PdfFileReader(pdf)
    page = input_pdf.getPage(page_id).mediaBox
    size = (int(page.getUpperRight_x()), int(page.getUpperRight_y()))
    return size
