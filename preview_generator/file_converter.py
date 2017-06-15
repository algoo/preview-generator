import os
import zipfile

import logging
import typing
from io import BytesIO
from PIL import Image
from PyPDF2 import PdfFileReader
from wand.color import Color
from wand.image import Image as WImage
import json
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call


def image_to_jpeg_pillow(png: typing.Union[str, typing.IO[bytes]],
                         preview_size: typing.Tuple[int, int] = (
                         256, 256)) -> BytesIO:
    logging.info('Converting image to jpeg using Pillow')
    temp = Image.new('RGB', (preview_size[1], preview_size[0]), (255, 255, 255))
    with Image.open(png) as image:
        b, a = image.size
        x, y = preview_size
        size_rate = (a / b) / (x / y)
        if size_rate > 1:
            a = int(a * (y / b))
            b = int(b * (y / b))
        else:
            b = int(b * (x / a))
            a = int(a * (x / a))
        image = image.resize((b, a))
        left = int((b / 2) - (y / 2))
        top = int((a / 2) - (x / 2))
        width = left + y
        height = top + x
        box = (left, top, width, height)
        layer_copied = image.crop(box)
        try:
            temp.paste(layer_copied, (0, 0), layer_copied)
        except ValueError:
            logging.warning(
                'Failed the transparency mask superposition. Maybe your image '
                'does not contain a transparency mask')
            temp.paste(layer_copied)
        output = BytesIO()
        temp.save(output, 'jpeg')
        output.seek(0, 0)
        return output


def image_to_jpeg_wand(jpeg: typing.Union[str, typing.IO[bytes]],
                       preview_size: typing.Tuple[int, int] = (
                       256, 256)) -> BytesIO:
    '''
    for jpeg, gif and bmp
    :param jpeg: 
    :param size: 
    :return: 
    '''
    logging.info('Converting image to jpeg using wand')
    with WImage(file=jpeg) as image:
        b, a = image.size
        x, y = preview_size
        size_rate = (a / b) / (x / y)
        if size_rate > 1:
            a = int(a * (y / b))
            b = int(b * (y / b))
        else:
            b = int(b * (x / a))
            a = int(a * (x / a))
        image.resize(b, a)
        left = int((b / 2) - (y / 2))
        top = int((a / 2) - (x / 2))
        width = left + y
        height = top + x
        image.crop(left, top, width, height)
        content_as_bytes = image.make_blob('jpeg')
        output = BytesIO()
        output.write(content_as_bytes)
        output.seek(0, 0)
        return output


def pdf_to_jpeg(pdf: typing.Union[str, typing.IO[bytes]],
                preview_size: typing.Tuple[int, int] = (256, 256)) -> BytesIO:

    logging.info('Converting pdf to jpeg')

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
            b, a = image.size
            x, y = preview_size
            size_rate = (a / b) / (x / y)
            if size_rate > 1:
                a = int(a * (y / b))
                b = int(b * (y / b))
            else:
                b = int(b * (x / a))
                a = int(a * (x / a))
            image.resize(b, a)
            left = int((b / 2) - (y / 2))
            top = int((a / 2) - (x / 2))
            width = left + y
            height = top + x
            image.crop(left, top, width, height)
            content_as_bytes = image.make_blob('jpeg')
            output = BytesIO()
            output.write(content_as_bytes)
            output.seek(0, 0)
            return output


def office_to_pdf(odt: typing.IO[bytes], cache_path: str,
                  file_name: str) -> BytesIO:
    logging.info('Converting office to pdf')
    try:
        logging.info('Creation of directory' + cache_path + file_name + '_flag')
        os.mkdir(cache_path + file_name + '_flag')
    except OSError:
        pass

    if not os.path.exists('{path}{file_name}'.format(
            path=cache_path,
            file_name=file_name)
    ):

        with open('{path}{file_name}'.format(
                path=cache_path,
                file_name=file_name), 'wb') \
                as odt_temp:
            odt.seek(0, 0)
            buffer = odt.read(1024)
            while buffer:
                odt_temp.write(buffer)
                buffer = odt.read(1024)

        try:
            logging.info('Creation of directory' + cache_path)
            os.makedirs(cache_path)
        except OSError:
            pass

        # TODO There's probably a cleaner way to convert to pdf
        check_call(
            [
                'libreoffice',
                '--headless',
                '--convert-to',
                'pdf:writer_pdf_Export',
                '{path}{extension}'.format(
                    path=cache_path,
                    extension=file_name
                ),
                '--outdir',
                cache_path,
                '-env:UserInstallation=file:///tmp/LibreOffice_Conversion_${USER}',
            ],
            stdout=DEVNULL, stderr=STDOUT
        )

    try:
        logging.info('Removing directory' + cache_path + file_name + '_flag')
        os.removedirs(cache_path + file_name + '_flag')
    except OSError:
        pass

    try:
        logging.info('Removing directory {path}{file_name}'.format(
            path=cache_path,
            file_name=file_name
        )
        )
        os.remove('{path}{file_name}'.format(
            path=cache_path,
            file_name=file_name
        )
        )
    except OSError:
        pass
    with open('{path}{file_name}.pdf'.format(
            path=cache_path,
            file_name=file_name
    ), 'rb') as pdf:
        pdf.seek(0, 0)
        content_as_bytes = pdf.read()
        output = BytesIO(content_as_bytes)
        output.seek(0, 0)

        return output


def txt_to_txt(text: typing.IO[typing.Any]) -> typing.IO[typing.Any]:
    logging.info('Converting text to text')
    return text


def zip_to_txt(zip: typing.IO[bytes]) -> BytesIO:
    logging.info('Converting zip to text')
    zz = zipfile.ZipFile(zip)
    output = BytesIO()
    for line, info in enumerate(zz.infolist()):
        date = "%d-%02d-%02d %02d:%02d:%02d" % info.date_time[:6]
        output.write(str.encode(
            "%-46s %s %12d\n" % (info.filename, date, info.file_size)))
    output.seek(0, 0)
    return output


def zip_to_html(zip: typing.IO[bytes]) -> BytesIO:
    logging.info('Converting zip to html')
    zz = zipfile.ZipFile(zip)  # type: ignore
    output = BytesIO()
    output.write(str.encode('<p><ul>'))
    for line, info in enumerate(zz.infolist()):
        date = "%d-%02d-%02d %02d:%02d:%02d" % info.date_time[:6]
        output.write(
            str.encode(
                '<li>file {line}</li>'
                '<ul>'
                '<li>name : {name}</li>'
                '<li>size : {size}</li>'
                '<li>date : {date}</li>'
                '</ul>'.format(
                    line=line,
                    name=info.filename,
                    size=info.file_size,
                    date=date,
                    )
            )
        )
    output.write(str.encode('</ul></p>'))
    output.seek(0, 0)
    return output


def zip_to_json(zip: typing.IO[bytes]) -> BytesIO:
    logging.info('Converting zip to json')
    zz = zipfile.ZipFile(zip)
    output = BytesIO()
    files = []
    dictionnary = {}
    for line, info in enumerate(zz.infolist()):
        date = '%d-%02d-%02d %02d:%02d:%02d' % info.date_time[:6]
        files.append(dict(name=info.filename, size=info.file_size, date=date))
    dictionnary['files'] = files
    content = json.dumps(dictionnary)
    output.write(str.encode(content))
    output.seek(0, 0)
    return output


def image_to_json(img: typing.Union[str, typing.IO[bytes]]) -> BytesIO:
    logging.info('Converting image to json')
    info = {}
    with Image.open(img) as image:
        info['height'] = image.size[0]
        info['width'] = image.size[1]
        output = BytesIO()
        try:
            image.save(output, 'JPEG')
        except OSError:
            image.save(output, 'GIF')
        contents = output.getvalue()
        output.close()
        info['size'] = len(contents)
    output = BytesIO()
    content = json.dumps(info)
    output.write(str.encode(content))
    output.seek(0, 0)
    return output

def get_image_size(img: typing.IO[bytes]) -> typing.Tuple[int, int]:
    with WImage(file=img) as image:
        return image.size

def get_pdf_size(pdf: typing.Union[str, typing.IO[bytes]], page_id: int) -> typing.Tuple[int, int]:
    input_pdf = PdfFileReader(pdf)
    page = input_pdf.getPage(page_id).mediaBox
    size = (int(page.getUpperRight_x()), int(page.getUpperRight_y()))
    return size